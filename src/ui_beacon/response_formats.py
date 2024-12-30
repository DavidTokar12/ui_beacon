from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class StepPlannerResponse(BaseModel):
    current_page: str = Field(
        description="The name of the page the user is currently on"
    )
    goal_page: str = Field(
        description="The page the user has to navigate to, to achieve their goal"
    )
    page_navigation_steps: list[str] = Field(
        description="The steps the user has to take to navigate to the goal page"
    )
    action_completion_steps: list[str] = Field(
        description="The steps the user has to take to complete the action"
    )
    functionality_explanation: str = Field(
        description="An explanation of the functionality of the page for the user"
    )
