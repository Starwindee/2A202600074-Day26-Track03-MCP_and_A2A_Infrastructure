"""Deterministic mock chat model for offline lab execution.

This model supports:
- invoke/ainvoke
- tool calling via bind_tools
- simple JSON routing responses

It is intentionally heuristic and stable, so students can run all stages
without a real OpenRouter key.
"""

from __future__ import annotations

import json
import re
from uuid import uuid4

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import PrivateAttr


class MockChatModel(BaseChatModel):
    """A lightweight deterministic chat model for local/offline labs."""

    model_name: str = "mock-legal-llm"
    temperature: float = 0.3
    _bound_tool_names: list[str] = PrivateAttr(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "mock-legal-llm"

    @property
    def _identifying_params(self) -> dict:
        return {"model_name": self.model_name, "temperature": self.temperature}

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):  # type: ignore[override]
        """Bind tool names so the model can emit tool_calls."""
        clone = self.model_copy(deep=True)
        clone._bound_tool_names = [_tool_name(t) for t in tools]
        return clone

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs) -> ChatResult:
        message = self._respond(messages)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _respond(self, messages: list[BaseMessage]) -> AIMessage:
        system_text = "\n".join(m.content for m in messages if m.type == "system" and isinstance(m.content, str)).lower()
        last_human = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
        question = (last_human.content if last_human and isinstance(last_human.content, str) else "").strip()
        last_msg = messages[-1] if messages else None

        if self._bound_tool_names:
            if isinstance(last_msg, ToolMessage):
                return AIMessage(content=_final_from_tools(messages, question))

            if question:
                tool_calls = _select_tool_calls(self._bound_tool_names, question)
                if tool_calls:
                    return AIMessage(content="", tool_calls=tool_calls)
            return AIMessage(content=_generic_legal_answer(question))

        if "only valid json" in system_text and "needs_tax" in system_text:
            q = question.lower()
            needs_tax = any(k in q for k in ("tax", "irs", "thuế", "fbar", "fatca"))
            needs_compliance = any(k in q for k in ("compliance", "sec", "regulation", "gdpr", "ccpa", "aml", "sox", "privacy", "dữ liệu"))
            return AIMessage(content=json.dumps({"needs_tax": needs_tax, "needs_compliance": needs_compliance}))

        return AIMessage(content=_generic_legal_answer(question))


def _tool_name(tool: object) -> str:
    if isinstance(tool, dict):
        if "function" in tool and isinstance(tool["function"], dict):
            return str(tool["function"].get("name", "tool"))
        return str(tool.get("name", "tool"))
    name = getattr(tool, "name", None)
    if isinstance(name, str) and name:
        return name
    fn_name = getattr(tool, "__name__", None)
    if isinstance(fn_name, str) and fn_name:
        return fn_name
    return "tool"


def _select_tool_calls(tool_names: list[str], question: str) -> list[dict]:
    q = question.lower()
    calls: list[dict] = []

    def add(name: str, args: dict) -> None:
        calls.append({"name": name, "args": args, "id": f"call_{uuid4().hex[:10]}", "type": "tool_call"})

    for name in tool_names:
        if name == "delegate_to_legal_agent":
            add(name, {"question": question})
            return calls

    for name in tool_names:
        if name in {"search_legal_knowledge", "search_legal_database"}:
            add(name, {"query": question})

    if "check_statute_of_limitations" in tool_names:
        case_type = "contract"
        if "tort" in q or "bồi thường" in q:
            case_type = "tort"
        elif "property" in q or "tài sản" in q:
            case_type = "property"
        add("check_statute_of_limitations", {"case_type": case_type})

    if "search_case_law" in tool_names:
        add("search_case_law", {"keywords": question})

    if "calculate_damages" in tool_names and any(k in q for k in ("damage", "damages", "thiệt hại", "contract value")):
        add("calculate_damages", {"breach_type": "standard breach", "contract_value": 100000.0})

    if "calculate_penalty" in tool_names and any(k in q for k in ("revenue", "$", "triệu", "million", "phạt", "penalty")):
        annual_revenue = _extract_revenue(question)
        violation = "data_privacy" if any(k in q for k in ("privacy", "data", "gdpr", "dữ liệu")) else "tax_evasion"
        severity = "high" if any(k in q for k in ("caught", "rò rỉ", "evasion", "fraud")) else "medium"
        add("calculate_penalty", {"violation_type": violation, "severity": severity, "annual_revenue": annual_revenue})

    if "check_compliance_requirements" in tool_names:
        industry = "technology" if any(k in q for k in ("tech", "startup", "phần mềm", "saas")) else "finance"
        company_size = "startup" if "startup" in q else "mid-size"
        add("check_compliance_requirements", {"industry": industry, "company_size": company_size})

    return calls


def _extract_revenue(text: str) -> float:
    t = text.lower().replace(",", "")
    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)\s*m", t)
    if m:
        return float(m.group(1)) * 1_000_000
    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)\s*(million|triệu)", t)
    if m:
        return float(m.group(1)) * 1_000_000
    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)", t)
    if m:
        return float(m.group(1))
    return 1_000_000.0


def _final_from_tools(messages: list[BaseMessage], question: str) -> str:
    tool_outputs = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            name = msg.name or "tool"
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            tool_outputs.append((name, content))

    if not tool_outputs:
        return _generic_legal_answer(question)

    lines = ["Summary based on tool outputs:"]
    for name, output in tool_outputs:
        lines.append(f"- [{name}] {output}")
    lines.append("")
    lines.append(
        "Recommendation: review contract, tax, compliance, and data-risk items and consult a licensed attorney before decisions."
    )
    return "\n".join(lines)


def _generic_legal_answer(question: str) -> str:
    q = question.lower()
    sections = []
    if any(k in q for k in ("contract", "hợp đồng", "nda", "breach")):
        sections.append("Contract risk: possible compensatory damages, consequential damages, and injunctive relief.")
    if any(k in q for k in ("tax", "thuế", "irs", "fbar", "fatca")):
        sections.append("Tax risk: potential back taxes, civil penalties, and criminal exposure in serious cases.")
    if any(k in q for k in ("compliance", "sec", "sox", "regulation", "tuân thủ")):
        sections.append("Compliance risk: regulatory enforcement, remediation obligations, and increased oversight.")
    if any(k in q for k in ("privacy", "data", "gdpr", "ccpa", "dữ liệu")):
        sections.append("Privacy risk: administrative fines, data-subject claims, and breach-notification duties.")
    if not sections:
        sections.append(
            "Review facts, contracts, statutory duties, and regulator jurisdiction to determine concrete legal exposure."
        )
    sections.append("Note: educational content only, not legal advice.")
    return "\n".join(sections)
