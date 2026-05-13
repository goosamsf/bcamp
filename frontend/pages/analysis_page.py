import sys
sys.path.insert(0, '.')

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from frontend.utils.formatting import (
    get_protocol_color, bytes_to_human, seconds_to_human,
    OSI_LAYER_LABELS, SEVERITY_COLORS,
)


def render_analysis_page():
    report_json = st.session_state.get("report_json")
    if not report_json:
        st.warning("분석 결과가 없습니다. PCAP 파일을 먼저 업로드하세요.")
        if st.button("← 업로드 페이지로"):
            st.session_state["page"] = "upload"
            st.rerun()
        return

    report = json.loads(report_json)

    st.title("패킷 분석 결과")
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← 새 분석"):
            st.session_state["page"] = "upload"
            st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Packet Table", "Protocol Explorer", "Learn", "Agent Trace"
    ])

    stats = report.get("pcap_statistics", {})
    protocols = report.get("protocol_analyses", [])
    anomalies = report.get("anomalies", [])
    educational = report.get("educational_contents", [])
    agent_trace = report.get("agent_execution_trace", [])
    learning_moments = report.get("top_learning_moments", [])
    summary = report.get("overall_summary", "")

    # Tab 1: Overview
    with tab1:
        _render_overview(stats, protocols, anomalies, summary, learning_moments)

    # Tab 2: Packet Table
    with tab2:
        _render_packet_table(report.get("raw_packets", []), protocols)

    # Tab 3: Protocol Explorer
    with tab3:
        _render_protocol_explorer(protocols)

    # Tab 4: Learn
    with tab4:
        _render_learn_tab(educational, report.get("quiz_questions", []), st.session_state.get("complexity", "beginner"))

    # Tab 5: Agent Trace
    with tab5:
        _render_agent_trace(agent_trace)


def _render_overview(stats, protocols, anomalies, summary, learning_moments):
    # Summary
    if summary:
        st.info(summary)

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 패킷", f"{stats.get('total_packets', 0):,}")
    col2.metric("총 데이터", bytes_to_human(stats.get('total_bytes', 0)))
    col3.metric("캡처 시간", seconds_to_human(stats.get('capture_duration_seconds', 0)))
    col4.metric("고유 프로토콜", len(protocols))

    col5, col6 = st.columns(2)
    col5.metric("고유 소스 IP", len(stats.get('unique_src_ips', [])))
    col6.metric("이상 탐지", f"{len(anomalies)}건", delta_color="inverse" if anomalies else "off")

    st.markdown("---")

    # Protocol distribution chart
    if protocols:
        col_chart, col_moments = st.columns([3, 2])

        with col_chart:
            st.subheader("프로토콜 분포")
            proto_dist = stats.get("protocol_distribution", {})
            if proto_dist:
                df = pd.DataFrame([
                    {"프로토콜": k, "패킷 수": v, "색상": get_protocol_color(k)}
                    for k, v in sorted(proto_dist.items(), key=lambda x: x[1], reverse=True)[:10]
                ])
                fig = px.pie(
                    df, values="패킷 수", names="프로토콜",
                    color="프로토콜",
                    color_discrete_map={row["프로토콜"]: row["색상"] for _, row in df.iterrows()},
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)

        with col_moments:
            st.subheader("주요 학습 포인트")
            for i, moment in enumerate(learning_moments, 1):
                st.markdown(f"**{i}.** {moment}")

    # Anomaly alerts
    if anomalies:
        st.markdown("---")
        st.subheader("이상 패턴 감지")
        for anomaly in anomalies:
            severity = anomaly.get("severity", "low")
            color = SEVERITY_COLORS.get(severity, "#grey")
            with st.expander(f"⚠️ [{severity.upper()}] {anomaly.get('anomaly_type', '')}"):
                st.markdown(f"**설명:** {anomaly.get('description', '')}")
                st.info(f"**교육적 의미:** {anomaly.get('educational_note', '')}")

    # Top talkers
    top_talkers = stats.get("top_talkers", [])
    if top_talkers:
        st.markdown("---")
        st.subheader("Top Talkers (가장 많은 트래픽)")
        df_talkers = pd.DataFrame(top_talkers[:5])
        if not df_talkers.empty:
            df_talkers["total_bytes_human"] = df_talkers["total_bytes"].apply(bytes_to_human)
            st.dataframe(df_talkers[["ip", "total_bytes_human"]].rename(
                columns={"ip": "IP 주소", "total_bytes_human": "데이터량"}
            ), use_container_width=True)


def _render_packet_table(raw_packets, protocols):
    st.subheader("패킷 목록")
    if not raw_packets:
        st.info("패킷 데이터가 없습니다.")
        return

    # Protocol filter
    available_protocols = list(set(p.get("protocol", "Unknown") for p in raw_packets))
    selected_protocols = st.multiselect(
        "프로토콜 필터", available_protocols, default=available_protocols[:5]
    )

    filtered = [p for p in raw_packets if p.get("protocol") in selected_protocols]

    rows = []
    for p in filtered[:200]:
        flags = p.get("tcp_flags") or {}
        flag_str = " ".join(k.upper() for k, v in flags.items() if v) if flags else ""
        rows.append({
            "#": p.get("packet_index", ""),
            "시간": f"{p.get('timestamp', 0):.3f}",
            "출발지": f"{p.get('src_ip', '')}" + (f":{p.get('src_port')}" if p.get('src_port') else ""),
            "목적지": f"{p.get('dst_ip', '')}" + (f":{p.get('dst_port')}" if p.get('dst_port') else ""),
            "프로토콜": p.get("protocol", ""),
            "크기(B)": p.get("length", 0),
            "TCP 플래그": flag_str,
            "요약": p.get("raw_summary", "")[:60],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=400)
    st.caption(f"총 {len(filtered)}개 패킷 표시 중 (최대 200개)")


def _render_protocol_explorer(protocols):
    st.subheader("프로토콜 탐색기")
    if not protocols:
        st.info("분석된 프로토콜이 없습니다.")
        return

    for proto in protocols:
        name = proto.get("protocol_name", "Unknown")
        color = get_protocol_color(name)
        count = proto.get("packet_count", 0)
        pct = proto.get("percentage_of_traffic", 0)
        layer = OSI_LAYER_LABELS.get(proto.get("osi_layer", ""), "Unknown")
        rfc = proto.get("rfc_reference", "")

        with st.expander(f"**{name}** — {count}개 패킷 ({pct}%)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**OSI 레이어:** `{layer}`")
                if rfc:
                    st.markdown(f"**RFC 참조:** `{rfc}`")
            with col2:
                st.progress(min(pct / 100, 1.0), text=f"{pct}%")

            observations = proto.get("key_observations", [])
            if observations:
                st.markdown("**주요 관찰 사항:**")
                for obs in observations:
                    st.markdown(f"- {obs}")

            rag_context = proto.get("rag_retrieved_context", [])
            if rag_context:
                with st.expander("RAG 지식베이스 참조"):
                    for ctx in rag_context[:2]:
                        st.caption(ctx[:300])


def _render_learn_tab(educational, quiz_questions, complexity):
    st.subheader("네트워크 학습")

    complexity_labels = {
        "beginner": "초급",
        "intermediate": "중급",
        "advanced": "고급",
    }

    if not educational:
        st.info("교육 콘텐츠가 없습니다.")
        return

    for edu in educational:
        name = edu.get("protocol_name", "")
        st.markdown(f"### {name}")

        # One-liner and analogy
        if edu.get("what_it_is"):
            st.markdown(f"**정의:** {edu['what_it_is']}")
        if edu.get("real_world_analogy"):
            st.info(f"**비유:** {edu['real_world_analogy']}")

        # Capture-specific insight
        if edu.get("what_it_does_in_this_capture"):
            st.markdown(f"**이 캡처에서:** {edu['what_it_does_in_this_capture']}")

        # Layered explanations
        layered = edu.get("layered_explanations", [])
        if layered:
            difficulty_tabs = st.tabs(["초급 설명", "중급 설명", "고급 설명"])
            for i, (level_name, tab) in enumerate(zip(["beginner", "intermediate", "advanced"], difficulty_tabs)):
                with tab:
                    matching = [e for e in layered if e.get("difficulty") == level_name]
                    if matching:
                        st.markdown(matching[0].get("explanation", ""))
                        if matching[0].get("analogy"):
                            st.caption(f"비유: {matching[0]['analogy']}")

        cols = st.columns(2)
        if edu.get("why_it_matters"):
            with cols[0]:
                st.markdown(f"**왜 중요한가?** {edu['why_it_matters']}")
        if edu.get("interesting_fact"):
            with cols[1]:
                st.markdown(f"**흥미로운 사실!** {edu['interesting_fact']}")

        st.markdown("---")

    # Quiz section
    if quiz_questions:
        st.subheader("퀴즈 - 이해도 점검")
        for i, q in enumerate(quiz_questions[:5]):
            st.markdown(f"**Q{i+1}.** {q.get('question', '')}")
            options = q.get("options", [])
            answer = st.radio(
                "답을 선택하세요",
                options,
                key=f"quiz_{i}",
                index=None,
                label_visibility="collapsed",
            )
            if answer:
                correct = q.get("correct_answer", "")
                if answer == correct:
                    st.success(f"정답! {q.get('explanation', '')}")
                else:
                    st.error(f"오답. 정답: {correct}\n\n{q.get('explanation', '')}")
            st.markdown("---")


def _render_agent_trace(agent_trace):
    st.subheader("AI Agent 협업 과정 (A2A Trace)")
    st.caption("LangGraph Multi-Agent 시스템의 실제 실행 흐름입니다.")

    if not agent_trace:
        st.info("Agent 실행 이력이 없습니다.")
        return

    agent_colors = {
        "orchestrator": "#9C27B0",
        "pcap_agent": "#2196F3",
        "protocol_agent": "#FF9800",
        "education_agent": "#4CAF50",
        "summary_agent": "#F44336",
    }

    for i, trace in enumerate(agent_trace):
        sender = trace.get("sender_agent", "unknown")
        color = agent_colors.get(sender, "#757575")
        msg_type = trace.get("message_type", "")
        summary = trace.get("summary", "")
        ts = trace.get("timestamp", 0)

        icon = "✅" if msg_type == "task_result" else ("🔀" if msg_type == "routing" else "❌")

        with st.container():
            st.markdown(
                f"""<div style="border-left: 4px solid {color}; padding: 8px 16px; margin: 4px 0; background: #f8f9fa; border-radius: 0 4px 4px 0">
                <b style="color: {color}">{icon} {sender}</b> → <i>{msg_type}</i><br/>
                {summary}
                </div>""",
                unsafe_allow_html=True,
            )
