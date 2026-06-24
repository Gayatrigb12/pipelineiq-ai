from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Payload sent by the client to the chat endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The natural-language question to answer against the deal knowledge base.",
        examples=["Which deals in the negotiation stage have been inactive for more than 30 days?"],
    )


class ChatResponse(BaseModel):
    """Response returned by the chat endpoint."""

    answer: str = Field(
        ...,
        description="The model-generated answer to the submitted question.",
        examples=["There are 3 deals in negotiation that have been inactive for over 30 days: …"],
    )