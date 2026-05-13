# Packet Analyzer AI Agent

교육용 패킷 분석기 AI Agent 서비스

## 기술 스택
- **Backend**: FastAPI, LangGraph
- **Frontend**: Streamlit
- **AI**: Anthropic Claude (RAG + Agent)
- **분석**: Scapy, FAISS

## 실행 방법

### 환경 설정
```bash
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 입력
```

### 실행
```bash
./setup.sh
./run_backend.sh
./run_frontend.sh
```
