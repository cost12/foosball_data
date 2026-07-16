import dataclasses
from typing import Type, Annotated, Literal
from enum import Enum, auto
import datetime
import logging

import pydantic
import polars as pl

from .data_constraints import SeriesConstraint, DataConstraint, ValueConstraint

logger = logging.getLogger(__name__)

GAME_FIELDS = {
    "Winner",
    "Loser",
    "Winner Score",
    "Loser Score",
    "Winner Color",
    "Loser Color",
    "Date",
    "Number",
    'G PROB',
    'LL PROB',
    'LL EXIST PROB',
    'EXIST PROB'
}

STANDING_FIELDS = {
    "Name",
    "G",
    "W",
    "L",
    "W PCT",
    "STRK",
    "GF",
    "GA",
    "G PCT",
    "LWS",
    "LLS",
    "W PROB",
    "WOE",
    "Skill",
    "W RANK",
    "G RANK",
    "ELO",
    "GOAL ELO",
    "NW",
    "NL",
    "NW PCT",
    "NSOS",
    "NSOV",
    "NSINDEX",
    "SOS",
    "SOV",
    "SINDEX",
}

MATCHUP_FIELDS = {
    "Name",
    "Opponent",
    "G",
    "W",
    "L",
    "W PCT",
    "STRK",
    "GF",
    "GA",
    "G PCT",
    "LWS",
    "LLS",
    "W PROB",
    "WOE",
}

_TYPE_MAP : dict[str, Type] = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "date": datetime.date,
}

PlayerId = str
StadiumId = str

class PlayerRole(Enum):
    ALL = auto()
    OFFENSE = auto()
    DEFENSE = auto()

@dataclasses.dataclass(frozen=True)
class Player:
    player_id : PlayerId
    first_name : str
    last_name : str
    nick_name : str = ""

@dataclasses.dataclass(frozen=True)
class Stadium:
    stadium_id : StadiumId
    name : str
    home_color : str
    away_color : str
    description : str = ""

class MatchSide(Enum):
    HOME = auto()
    AWAY = auto()

@dataclasses.dataclass(frozen=True)
class GameParticipants:
    game_id : int
    side : MatchSide
    player_id : PlayerId
    player_role : PlayerRole

@dataclasses.dataclass(frozen=True)
class FoosballGame:
    game_id : int
    home_goals : int
    away_goals : int
    date : datetime.date
    stadium : StadiumId
    location : str

class DataSource(Enum):
    INPUT = auto()
    CALCULATED = auto()

class SimpleFieldCalculation(pydantic.BaseModel):
    type : Literal["simple"]

    def calculate_field(self, data: dict):
        ...

FieldCalculation = Annotated[
    SimpleFieldCalculation,
    pydantic.Field(discriminator="type")
]

class DataField(pydantic.BaseModel):
    name : str
    type : Type
    description : str = ""
    constraints : tuple[ValueConstraint,...] = pydantic.Field(default_factory=tuple)
    calculation : FieldCalculation|None = None

    @pydantic.field_validator("type", mode="before")
    @classmethod
    def parse_type(cls, v):
        if isinstance(v, str):
            try:
                return _TYPE_MAP[v]
            except KeyError as exc:
                raise ValueError(f"Unknown type: {v}") from exc
        return v

    @property
    def is_calculated(self):
        return self.calculation is not None

class DataSpecification(pydantic.BaseModel):
    fields : tuple[DataField,...]
    data_constraints : tuple[DataConstraint,...]
    series_constraints : tuple[SeriesConstraint,...]

@dataclasses.dataclass(frozen=True)
class ValidatedData:
    raw_data : pl.DataFrame
    data : pl.DataFrame
    fields : tuple[DataField,...]

@dataclasses.dataclass(frozen=True)
class InputData:
    raw_data : pl.DataFrame
    fields : tuple[DataField,...]

    def get_data(self) -> ValidatedData:
        ...

@dataclasses.dataclass(frozen=True)
class CalculatedTable:
    input_data : InputData
    fields : tuple[DataField,...]
