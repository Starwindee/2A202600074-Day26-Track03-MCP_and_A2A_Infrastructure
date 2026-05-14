# Minh Chung Ket Qua Lab (Raw Logs)

**Lab:** Day26 - MCP and A2A Infrastructure  
**Ngay thuc hien:** 2026-05-14  
**Che do chay:** `MOCK_LLM=true` (khong can OpenRouter key that)

## 1) Tong quan hoan thanh

- [x] Stage 1: Direct LLM
- [x] Stage 2: RAG + Tools
- [x] Stage 3: Single Agent (ReAct)
- [x] Stage 4: Multi-Agent in-process
- [x] Stage 5: Distributed A2A (full services + test client)
- [x] Exercise 2: Tools + Knowledge Base
- [x] Exercise 4: Privacy Agent + Conditional Routing

## 2) File log thuc te Stage 1-5

> Tat ca file ben duoi la output thuc thi duoc ghi lai tu terminal.

| Hang muc | Lenh chay | Ket qua |
|---|---|---|
| Stage 1 | `uv run python stages/stage_1_direct_llm/main.py` | PASS - [logs/stage1.log](./logs/stage1.log) |
| Stage 2 | `uv run python stages/stage_2_rag_tools/main.py` | PASS - [logs/stage2.log](./logs/stage2.log) |
| Stage 3 | `uv run python stages/stage_3_single_agent/main.py` | PASS - [logs/stage3.log](./logs/stage3.log) |
| Stage 4 | `uv run python stages/stage_4_milti_agent/main.py` | PASS - [logs/stage4.log](./logs/stage4.log) |
| Exercise 2 | `uv run python exercises/exercise_2_tools.py` | PASS |
| Exercise 4 | `uv run python exercises/exercise_4_multiagent.py` | PASS |
| Stage 5 E2E | Start Registry + 4 agents, sau do `uv run python test_client.py` | PASS - [logs/stage5_client.log](./logs/stage5_client.log) |

## 3) Minh chung Stage 5 (A2A)

- Log client:
  - [logs/stage5_client.log](./logs/stage5_client.log)
- Log tung service:
  - [logs/stage5/registry.err.log](./logs/stage5/registry.err.log)
  - [logs/stage5/customer.err.log](./logs/stage5/customer.err.log)
  - [logs/stage5/law.err.log](./logs/stage5/law.err.log)
  - [logs/stage5/tax.err.log](./logs/stage5/tax.err.log)
  - [logs/stage5/compliance.err.log](./logs/stage5/compliance.err.log)

Trong log Stage 5 co the thay:
- Dang ky agent voi Registry
- Discover agent theo task
- Truyen `trace_id` va `delegation_depth` qua cac hop
- Client nhan duoc response cuoi cung thanh cong

## 4) Ghi chu ky thuat

- Da bo sung che do mock trong `common/llm.py` + `common/mock_llm.py`.
- Khi console Windows gap loi Unicode, chay them:
  - `PYTHONIOENCODING=utf-8`
- Da update `.env.example` de mac dinh ho tro mock mode:
  - `MOCK_LLM=true`
  - `LLM_TEMPERATURE=0.3`

## 5) Ket luan

Lab da duoc hoan thanh day du theo checklist codelab va co ket qua chay xac nhan cho cac phan bat buoc.
