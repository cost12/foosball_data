import dataclasses
from typing import Type, Annotated, Literal, Any
from enum import Enum, auto
import datetime
import logging

import pydantic
import polars as pl

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

class BoundedConstraint(pydantic.BaseModel):
    type: Literal["bounded"]
    min : float|None = None
    max : float|None = None

    def check_data(self, value: Any) -> bool:
        return (self.min is None or self.min <= value) and (self.max is None or self.max >= value)

class ChoiceConstraint(pydantic.BaseModel):
    type: Literal["choices"]
    choices : tuple[Any,...]

    def check_data(self, value: Any) -> bool:
        return value in self.choices

ValueConstraint = Annotated[
    BoundedConstraint | ChoiceConstraint,
    pydantic.Field(discriminator="type")
]

class FieldNotFound(Exception):
    ...

class GreaterConstraint(pydantic.BaseModel):
    type: Literal["greater"]
    greater : str
    lesser : str

    def check_data(self, data: dict) -> bool:
        if self.greater not in data:
            raise FieldNotFound(f"{self.greater} is not a field in the data")
        if self.lesser not in data:
            raise FieldNotFound(f"{self.lesser} is not a field in the data")
        return data[self.greater] > data[self.lesser]

class InequalityConstraint(pydantic.BaseModel):
    type: Literal["inequality"]
    fields : tuple[str,...]

    def check_data(self, data: dict) -> bool:
        values = set()
        for field in self.fields:
            if field not in data:
                raise FieldNotFound(f"{field} is not a field in the data")
            if data[field] in values:
                return False
            values.add(data[field])
        return True

DataConstraint = Annotated[
    GreaterConstraint | InequalityConstraint,
    pydantic.Field(discriminator="type")
]

class OrderConstraint(pydantic.BaseModel):
    type: Literal["order"]
    first_order : str
    second_order : str

    def check_data(self, data: list[dict]) -> bool:
        data = sorted(data, key=lambda x: x.get(self.first_order))
        if len(data) > 0:
            previous = data[0]
            for d in data[1:]:
                if d < previous:
                    return False
        return True

SeriesConstraint = Annotated[
    OrderConstraint,
    pydantic.Field(discriminator="type")
]

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
