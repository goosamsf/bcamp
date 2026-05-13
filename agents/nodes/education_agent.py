import sys
sys.path.insert(0, '.')

import json
import time
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from agents.graph.state import PacketAnalyzerState
from agents.tools.rag_tools import query_rag_knowledge, lookup_rfc_summary
from agents.prompts.education_prompts import EDUCATION_AGENT_SYSTEM_PROMPT
from schemas.education_schemas import EducationalContent, ConceptExplanation, QuizQuestion, DifficultyLevel
from config import settings


def _get_llm():
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=settings.model_name, temperature=0.3, openai_api_key=settings.openai_api_key)
    else:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=settings.model_name, temperature=0.3, anthropic_api_key=settings.anthropic_api_key)


def _build_education_prompt(protocol: dict, rag_context: str, complexity: str) -> str:
    return f"""Generate educational content for the protocol: {protocol['protocol_name']}

Context from this PCAP capture:
- Packet count: {protocol.get('packet_count', 0)}
- Percentage of traffic: {protocol.get('percentage_of_traffic', 0)}%
- Key observations: {protocol.get('key_observations', [])}
- OSI Layer: {protocol.get('osi_layer', 'Unknown')}

Knowledge base context:
{rag_context}

Target complexity level: {complexity}

Generate a JSON response with this exact structure:
{{
  "what_it_is": "one sentence definition",
  "what_it_does_in_this_capture": "specific to this capture's data",
  "real_world_analogy": "relatable everyday analogy",
  "beginner_explanation": "simple explanation with analogy",
  "intermediate_explanation": "technical explanation of mechanism",
  "advanced_explanation": "deep technical details, RFCs, edge cases",
  "why_it_matters": "practical significance",
  "interesting_fact": "surprising or memorable fact",
  "quiz_question": "a question testing understanding (not memorization)",
  "quiz_options": ["correct answer", "plausible wrong answer 1", "plausible wrong answer 2", "plausible wrong answer 3"],
  "quiz_correct": "correct answer text (must match one of quiz_options exactly)",
  "quiz_explanation": "why the answer is correct and what it teaches",
  "related_protocols": ["protocol1", "protocol2"]
}}

Respond with ONLY valid JSON, no markdown formatting."""


async def education_agent_node(state: PacketAnalyzerState) -> dict:
    """Educational Content Agent: generates layered explanations and quizzes."""
    complexity = state.get("user_complexity_level", "beginner")

    trace_entry = {
        "sender_agent": "education_agent",
        "recipient_agent": "orchestrator",
        "message_type": "task_result",
        "timestamp": time.time(),
        "summary": "",
        "payload": {},
        "confidence_score": 0.95,
    }

    try:
        protocol_analysis_json = state.get("protocol_analysis_json", "[]")
        protocols = json.loads(protocol_analysis_json)

        llm = _get_llm()
        educational_contents = []
        all_quiz_questions = []

        for proto_data in protocols[:6]:  # limit to 6 protocols
            proto_name = proto_data["protocol_name"]

            # Retrieve fresh RAG context for education
            rag_result_str = query_rag_knowledge.invoke({
                "query": f"{proto_name} educational explanation analogy beginner",
                "category": "all",
            })
            rag_data = json.loads(rag_result_str)
            rag_context = "\n\n".join(r["content"][:400] for r in rag_data.get("results", [])[:3])
            rag_sources = [r["source"] for r in rag_data.get("results", [])[:3]]

            prompt = _build_education_prompt(proto_data, rag_context, complexity)

            try:
                response = llm.invoke([
                    SystemMessage(content=EDUCATION_AGENT_SYSTEM_PROMPT.format(complexity_level=complexity)),
                    HumanMessage(content=prompt),
                ])
                raw = response.content.strip()

                # Strip markdown code blocks if present
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()

                edu_data = json.loads(raw)

                # Build EducationalContent with 3 difficulty levels
                layered = [
                    ConceptExplanation(
                        difficulty=DifficultyLevel.BEGINNER,
                        explanation=edu_data.get("beginner_explanation", ""),
                        analogy=edu_data.get("real_world_analogy"),
                    ),
                    ConceptExplanation(
                        difficulty=DifficultyLevel.INTERMEDIATE,
                        explanation=edu_data.get("intermediate_explanation", ""),
                    ),
                    ConceptExplanation(
                        difficulty=DifficultyLevel.ADVANCED,
                        explanation=edu_data.get("advanced_explanation", ""),
                    ),
                ]

                options = edu_data.get("quiz_options", ["A", "B", "C", "D"])
                quiz = QuizQuestion(
                    question=edu_data.get("quiz_question", f"What is {proto_name}?"),
                    options=options[:4],
                    correct_answer=edu_data.get("quiz_correct", options[0] if options else ""),
                    explanation=edu_data.get("quiz_explanation", ""),
                    difficulty=DifficultyLevel(complexity),
                )
                all_quiz_questions.append(quiz.model_dump())

                content = EducationalContent(
                    protocol_name=proto_name,
                    what_it_is=edu_data.get("what_it_is", ""),
                    what_it_does_in_this_capture=edu_data.get("what_it_does_in_this_capture", ""),
                    layered_explanations=layered,
                    real_world_analogy=edu_data.get("real_world_analogy", ""),
                    why_it_matters=edu_data.get("why_it_matters", ""),
                    interesting_fact=edu_data.get("interesting_fact", ""),
                    quiz_questions=[quiz],
                    related_protocols=edu_data.get("related_protocols", []),
                    rag_sources=rag_sources,
                )
                educational_contents.append(content.model_dump())

            except (json.JSONDecodeError, Exception) as parse_err:
                # Fallback: create minimal educational content using RAG context
                fallback = EducationalContent(
                    protocol_name=proto_name,
                    what_it_is=f"{proto_name} is a network protocol",
                    what_it_does_in_this_capture=f"Found {proto_data.get('packet_count', 0)} packets",
                    layered_explanations=[
                        ConceptExplanation(
                            difficulty=DifficultyLevel.BEGINNER,
                            explanation=rag_context[:300] if rag_context else f"{proto_name} protocol",
                        )
                    ],
                    rag_sources=rag_sources,
                )
                educational_contents.append(fallback.model_dump())

        trace_entry["summary"] = f"Generated educational content for {len(educational_contents)} protocols"
        trace_entry["payload"] = {"protocols_covered": [p["protocol_name"] for p in educational_contents]}

        msg = AIMessage(content=f"[Education Agent] Generated layered educational content for {len(educational_contents)} protocols with {len(all_quiz_questions)} quiz questions.")

        return {
            "educational_content_json": json.dumps(educational_contents),
            "agent_statuses": {**state.get("agent_statuses", {}), "education_agent": "complete"},
            "current_agent": "education_agent",
            "messages": [msg],
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
        }

    except Exception as e:
        trace_entry["message_type"] = "error"
        trace_entry["summary"] = f"Error: {e}"
        return {
            "error_message": str(e),
            "agent_statuses": {**state.get("agent_statuses", {}), "education_agent": "failed"},
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
            "current_agent": "education_agent",
        }
