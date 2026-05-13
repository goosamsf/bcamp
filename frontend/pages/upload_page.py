import sys
sys.path.insert(0, '.')

import streamlit as st
import json
from frontend.utils.api_client import upload_pcap, stream_analysis, check_health


def render_upload_page():
    st.title("패킷 분석기 (Educational Packet Analyzer)")
    st.markdown("PCAP 파일을 업로드하면 AI Agent가 협업하여 네트워크 트래픽을 분석하고 교육적으로 설명합니다.")

    # Health check
    health = check_health()
    if health.get("status") != "ok":
        st.error(f"백엔드 서버에 연결할 수 없습니다. 서버를 먼저 실행하세요.")
        st.code("python -m uvicorn backend.main:app --reload")
        return

    st.sidebar.header("설정")
    complexity = st.sidebar.radio(
        "학습 수준",
        options=["beginner", "intermediate", "advanced"],
        format_func=lambda x: {"beginner": "초급 (Beginner)", "intermediate": "중급 (Intermediate)", "advanced": "고급 (Advanced)"}[x],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**지원 파일 형식:** `.pcap`, `.pcapng`")
    st.sidebar.markdown("**최대 파일 크기:** 50MB")
    st.sidebar.markdown("**샘플 PCAP:** [Wireshark Samples](https://wiki.wireshark.org/SampleCaptures)")

    uploaded_file = st.file_uploader(
        "PCAP 파일을 드래그하거나 클릭하여 업로드",
        type=["pcap", "pcapng"],
        help="Wireshark에서 캡처한 .pcap 또는 .pcapng 파일",
    )

    if uploaded_file is not None:
        file_size_kb = len(uploaded_file.getvalue()) / 1024
        st.info(f"파일: **{uploaded_file.name}** ({file_size_kb:.1f} KB)")

        if st.button("AI 분석 시작", type="primary", use_container_width=True):
            _run_analysis(uploaded_file, complexity)


def _run_analysis(uploaded_file, complexity: str):
    """Upload file and stream analysis events."""
    progress_container = st.container()

    with progress_container:
        with st.status("분석 중...", expanded=True) as status_box:
            # Step 1: Upload
            st.write("파일 업로드 중...")
            try:
                upload_result = upload_pcap(uploaded_file.getvalue(), uploaded_file.name)
                session_id = upload_result["session_id"]
                st.write(f"업로드 완료: `{session_id[:8]}...`")
            except Exception as e:
                st.error(f"업로드 실패: {e}")
                return

            # Step 2: Stream analysis
            st.write("AI Agent 분석 시작...")
            agent_messages = {}
            final_report_json = None

            agent_labels = {
                "orchestrator": "오케스트레이터 (Orchestrator)",
                "pcap_agent": "PCAP 파싱 Agent",
                "protocol_agent": "프로토콜 분석 Agent",
                "education_agent": "교육 콘텐츠 Agent",
                "summary_agent": "리포트 생성 Agent",
            }

            try:
                for event in stream_analysis(session_id, complexity):
                    evt_type = event.get("event")
                    data = event.get("data", {})

                    if evt_type == "agent_start":
                        agent = data.get("agent", "")
                        label = agent_labels.get(agent, agent)
                        st.write(f"🔄 {label} 실행 중...")

                    elif evt_type == "agent_complete":
                        agent = data.get("agent", "")
                        label = agent_labels.get(agent, agent)
                        msg = data.get("message", "")
                        if msg:
                            st.write(f"✅ {label} 완료: {msg[:100]}")
                        else:
                            st.write(f"✅ {label} 완료")

                    elif evt_type == "analysis_complete":
                        final_report_json = json.dumps(data) if isinstance(data, dict) else data
                        st.write("✅ 분석 완료!")
                        status_box.update(label="분석 완료!", state="complete")

                    elif evt_type == "error":
                        error_msg = data.get("error", "Unknown error")
                        st.error(f"오류: {error_msg}")
                        status_box.update(label="분석 실패", state="error")
                        return

            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
                return

            if final_report_json:
                st.session_state["session_id"] = session_id
                st.session_state["report_json"] = final_report_json
                st.session_state["complexity"] = complexity
                st.session_state["page"] = "analysis"
                st.rerun()
