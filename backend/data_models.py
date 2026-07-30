import dataclasses
from typing import IO, Type, Annotated, Literal, Iterable, TypeVar, Mapping
from enum import Enum, auto
import datetime
import logging
from pathlib import Path

from frozendict import frozendict

import pydantic
import polars as pl

from .data_constraints import DataConstraint, FieldConstraint, SeriesConstraint, InvalidRows

logger = logging.getLogger(__name__)

T = TypeVar("T", pl.DataFrame, pl.LazyFrame)

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
    "int": pl.Int64,
    "float": pl.Float64,
    "str": pl.String,
    "bool": pl.Boolean,
    "date": pl.Date,
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

class DateFieldConversion(pydantic.BaseModel):
    type : Literal["date"]
    format : str

    def convert_field(self, data: pl.LazyFrame, field: str) -> pl.LazyFrame:
        return data.with_columns(pl.col(field).str.strptime(pl.Date, self.format, strict=False))

FieldConversion = Annotated[
    DateFieldConversion,
    pydantic.Field(discriminator="type")
]

class DataField(pydantic.BaseModel):
    name : str
    input_type : str
    #store_type : str
    description : str = ""
    constraints : tuple[FieldConstraint,...] = pydantic.Field(default_factory=tuple)
    calculation : FieldCalculation|None = None
    conversion : FieldConversion|None = None

    @property
    def is_calculated(self):
        return self.calculation is not None

class DataSpecification(pydantic.BaseModel):
    fields : tuple[DataField,...]
    data_constraints : tuple[DataConstraint,...]
    series_constraints : tuple[SeriesConstraint,...]

    def check_data(self, data: T) -> tuple[T, list[InvalidRows]]:
        return check_data(
            data,
            field_constraints={field.name: field.constraints for field in self.fields if not field.is_calculated},
            data_constraints=self.data_constraints,
            series_constraints=self.series_constraints,
        )

def read_in_data(source: str | Path | IO[str] | IO[bytes] | bytes, fields: Iterable[DataField]) -> pl.DataFrame:
    data = pl.read_csv(source, schema_overrides={field.name: _TYPE_MAP[field.input_type] for field in fields if not field.is_calculated}).lazy()
    for field in fields:
        if not field.is_calculated and field.conversion is not None:
            data = field.conversion.convert_field(data, field.name)
    data = data.select([field.name for field in fields if not field.is_calculated])
    return data.collect()

def check_data(
        data: T,
        *,
        field_constraints: Mapping[str,Iterable[FieldConstraint]] = frozendict(),
        data_constraints: Iterable[DataConstraint] = tuple(),
        series_constraints: Iterable[SeriesConstraint] = tuple(),
    ) -> tuple[T, list[InvalidRows]]:
    invalid : list[InvalidRows] = []

    for field, constraints in field_constraints.items():
        for constraint in constraints:
            invalid.append(
                InvalidRows(
                    data.filter(constraint.constraint_context.filter(field)),
                    constraint.error_string(field),
                    constraint.handling_context,
                )
            )
            if constraint.handling_context.remove:
                data = data.filter(~constraint.constraint_context.filter(field))

    for constraint in data_constraints:
        invalid.append(
            InvalidRows(
                data.filter(constraint.constraint_context.filter()),
                constraint.error_string(),
                constraint.handling_context,
            )
        )
        if constraint.handling_context.remove:
            data = data.filter(~constraint.constraint_context.filter())

    for constraint in series_constraints:
        invalid.append(
            InvalidRows(
                constraint.constraint_context.filter(data),
                constraint.error_string(),
                constraint.handling_context,
            )
        )
        if constraint.handling_context.remove:
            data = data.join(constraint.constraint_context.filter(data), on=data.columns, how='anit')

    return data, invalid

@dataclasses.dataclass(frozen=True)
class ValidatedData:
    raw_data : pl.DataFrame
    data : pl.DataFrame
    fields : tuple[DataField,...]

@dataclasses.dataclass(frozen=True)
class InputData:
    raw_data : pl.DataFrame
    specification : DataSpecification

    def get_data(self) -> ValidatedData:
        ...

@dataclasses.dataclass(frozen=True)
class CalculatedTable:
    input_data : InputData
    fields : tuple[DataField,...]
