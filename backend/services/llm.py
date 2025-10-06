from __future__ import annotations

from openai import OpenAI
from ..config.settings import get_settings

_settings = get_settings()
_client = OpenAI(api_key=_settings.openai_api_key)

def ask_llm(prompt: str) -> str:
    """Simple one-shot chat."""
    resp = _client.chat.completions.create(
        model=_settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()

def generate_patch_comment(diff: str, summary: dict) -> str:
    """Send terraform diff + summary to LLM and return markdown suggestions."""
    prompt = f"""
You are AutoInfra CoPilot. Review this Terraform plan and propose fixes.

Summary: {summary}
Diff:

Return markdown with:
- One line badge (🟢 or 🔴 Auto-check)
- Short explanation
- Suggested patch blocks (```diff fenced)
"""
    resp = _client.chat.completions.create(
        model=_settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()
