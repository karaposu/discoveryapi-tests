"""Generic LangChain wrapper for one structured-output LLM call.

Single public function: `call_structured(...)`. Centralizes the call
pattern used by both variant generation (`minimal4.py`) and candidate
judging (`judge_logic.py`):

    ChatOpenAI
       └─ with_structured_output(<schema>, method="function_calling")
              └─ ChatPromptTemplate (system + user)
                     └─ chain.invoke(<template args>) -> <schema instance>

Callers supply the prompts, the output schema, and the template args.
This module owns the plumbing (model construction, structured-output
wiring, prompt assembly, invoke call) and nothing else — no logging, no
timing, no retries. Those belong at the call site.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


DEFAULT_MODEL = "gpt-4o"


def call_structured(
    system_prompt: str,
    user_prompt: str,
    output_schema: Type[T],
    template_args: Dict[str, Any],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    chat_model: Optional[BaseChatModel] = None,
) -> T:
    """Make one LangChain structured-output call.

    `method="function_calling"` is used because OpenAI's newer strict
    response_format rejects schemas with Optional fields or default
    factories — which our project schemas typically have.

    Returns an instance of `output_schema` populated from the model's
    response.
    """
    llm = chat_model or ChatOpenAI(model=model, temperature=temperature)
    structured = llm.with_structured_output(
        output_schema, method="function_calling"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )
    chain = prompt | structured
    return chain.invoke(template_args)
