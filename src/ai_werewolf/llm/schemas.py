from pydantic import BaseModel, Field


class NightAction(BaseModel):
    """A werewolf's private nightly kill choice."""

    target_id: int = Field(description="id of the player to eliminate tonight")
    reasoning: str = Field(description="brief private reasoning, not shown to other players")


class Statement(BaseModel):
    """A player's public contribution to the day discussion."""

    speech: str = Field(description="what to say out loud to the group")
    reasoning: str = Field(description="brief private reasoning behind the speech, not shown to other players")


class VoteAction(BaseModel):
    """A player's public day vote."""

    target_id: int = Field(description="id of the player to vote to eliminate")
    reasoning: str = Field(description="brief private reasoning behind the vote, not shown to other players")
