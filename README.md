# Educational Packet Analyzer AI Agent

PCAP 파일을 업로드하면 Multi-Agent 파이프라인이 패킷을 분석하고, 감지된 프로토콜에 대한 교육 콘텐츠(난이도별 설명 + 퀴즈)를 자동 생성하는 AI 서비스입니다.

---

## 시스템 구조

```
PCAP 업로드
    │
    ▼
Orchestrator Agent  ──── 상태 검증 및 라우팅
    │
    ├──▶ PCAP Agent       : 패킷 파싱, 플로우 추출, 통계, 이상탐지 (Scapy)
    │         │
    ├──▶ Protocol Agent   : 프로토콜 식별, OSI 계층 매핑, RAG 지식 검색, RFC 참조
    │         │
    ├──▶ Education Agent  : 난이도별 설명 생성, 퀴즈 생성 (LLM + RAG)
    │         │
    └──▶ Summary Agent    : 최종 리포트 합성 (FullAnalysisReport)
```

### Agent 역할

| Agent | 역할 |
|-------|------|
| **Orchestrator** | 상태 검증, 에러 처리, 다음 Agent 라우팅 결정 |
| **PCAP Agent** | Scapy로 PCAP 파싱, 네트워크 플로우 추출, 통계 계산, 이상 패킷 탐지 |
| **Protocol Agent** | 프로토콜 식별, OSI 레이어 분류, FAISS RAG 지식 검색, RFC 참조 |
| **Education Agent** | 초급/중급/고급 3단계 설명 생성, 퀴즈 문제 생성 (LLM 호출) |
| **Summary Agent** | 전체 분석 결과 종합, LLM 기반 서술형 요약 생성, 최종 리포트 반환 |

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Agent Framework | LangGraph (StateGraph + MemorySaver) |
| LLM | Anthropic Claude / OpenAI GPT (설정으로 전환) |
| RAG | FAISS + LangChain |
| 패킷 분석 | Scapy |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| 데이터 검증 | Pydantic v2 |

---

## 디렉토리 구조

```
bcamp/
├── agents/
│   ├── graph/
│   │   ├── graph_builder.py   # LangGraph StateGraph 빌드 및 싱글턴 관리
│   │   ├── state.py           # PacketAnalyzerState (TypedDict)
│   │   └── edges.py           # 조건부 라우팅 함수
│   ├── nodes/
│   │   ├── orchestrator_agent.py
│   │   ├── pcap_agent.py
│   │   ├── protocol_agent.py
│   │   ├── education_agent.py
│   │   └── summary_agent.py
│   ├── tools/
│   │   ├── pcap_tools.py      # parse_pcap_file, extract_flows, compute_statistics, detect_packet_anomalies
│   │   ├── rag_tools.py       # query_rag_knowledge, lookup_rfc_summary
│   │   └── analysis_tools.py  # identify_protocol_from_port, analyze_tcp_flags, rank_by_educational_value
│   └── prompts/               # 각 Agent의 System Prompt
├── backend/
│   ├── main.py                # FastAPI 앱 (lifespan: RAG + Graph 초기화)
│   ├── api/routes/
│   │   ├── upload.py          # POST /api/upload
│   │   ├── analysis.py        # POST /api/analyze, GET /api/result/{session_id}
│   │   └── health.py          # GET /api/health
│   ├── models/
│   │   └── request_models.py
│   └── services/
│       └── session_store.py   # 세션 기반 분석 결과 저장
├── frontend/
│   ├── app.py                 # Streamlit 진입점 (upload / analysis 페이지 라우팅)
│   ├── pages/
│   │   ├── upload_page.py     # PCAP 업로드 UI
│   │   └── analysis_page.py   # 분석 결과 시각화 UI
│   └── utils/
│       ├── api_client.py      # Backend API 호출
│       └── formatting.py      # 결과 포맷팅
├── rag/
│   ├── knowledge_base/
│   │   ├── protocols/         # TCP/IP, DNS, HTTP, TLS, ARP, ICMP, UDP 등 마크다운 문서
│   │   ├── concepts/          # OSI 계층, 패킷 구조, 3-way handshake 개념 문서
│   │   └── security/          # SYN flood, 포트 스캐닝 등 보안 개념 문서
│   ├── vector_store.py        # FAISS 인덱스 빌드/로드
│   ├── embeddings.py          # 임베딩 모델 설정
│   ├── document_loader.py     # 마크다운 문서 로더
│   └── retriever.py           # RAG 검색기
├── schemas/
│   ├── packet_schemas.py      # RawPacket, NetworkFlow, PCAPStatistics, OSILayer
│   ├── analysis_schemas.py    # ProtocolAnalysis, Anomaly
│   ├── education_schemas.py   # EducationalContent, QuizQuestion, DifficultyLevel
│   └── agent_schemas.py       # FullAnalysisReport
├── config/
│   └── settings.py            # Pydantic Settings (.env 로드)
├── tests/
│   └── fixtures/
│       └── sample.pcap
├── .env.example
├── requirements.txt
├── setup.sh
├── run_backend.sh
└── run_frontend.sh
```

---

## 설치 및 실행

### 1. 환경 설정

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
LLM_PROVIDER=anthropic          # anthropic 또는 openai
ANTHROPIC_API_KEY=sk-ant-...    # Anthropic 사용 시
OPENAI_API_KEY=sk-...           # OpenAI 사용 시
MODEL_NAME=claude-haiku-4-5-20251001
```

### 2. 설치 및 RAG 인덱스 빌드

```bash
bash setup.sh
```

### 3. 실행

```bash
# 터미널 1 - Backend
bash run_backend.sh

# 터미널 2 - Frontend
bash run_frontend.sh
```

- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- API 문서: http://localhost:8000/docs

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/health` | 서버 상태 확인 |
| POST | `/api/upload` | PCAP 파일 업로드 (multipart/form-data) |
| POST | `/api/analyze` | 분석 시작 (session_id, complexity_level) |
| GET | `/api/result/{session_id}` | 분석 결과 조회 |

---

## 지원 LLM 모델

| Provider | 모델 예시 |
|----------|-----------|
| Anthropic | `claude-haiku-4-5-20251001` (빠름/저렴), `claude-sonnet-4-6` (균형), `claude-opus-4-7` (최고품질) |
| OpenAI | `gpt-4o-mini`, `gpt-4o`, `gpt-4.1` |

---

## RAG 지식베이스 커버리지

- **프로토콜**: TCP/IP, UDP, DNS, HTTP/HTTPS, TLS/SSL, ARP, ICMP
- **네트워크 개념**: OSI 7계층, 패킷 구조, 3-way handshake
- **보안**: SYN Flood, 포트 스캐닝
