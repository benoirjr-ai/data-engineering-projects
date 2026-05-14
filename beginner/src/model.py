from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional

class TeamSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


    team_id: int
    team_name: str
    overall: int = Field(ge=0, le=100)
    attack: int
    midfield: int
    defence: int
    transfer_budget_eur: float
    nationality_name: str

    # Handle the empty tactical strings 
    def_defence_pressure: Optional[int] = None

    @field_validator('*', mode='before')
    @classmethod
    def parse_empty_strings(cls, v):
        return None if v == "" else v