from typing import Annotated, Literal, Any, TypeVar, Mapping
import logging
import dataclasses
from enum import Enum, auto

import pydantic
import polars as pl

logger = logging.getLogger(__name__)

T = TypeVar("T", pl.DataFrame, pl.LazyFrame)

class ConstraintLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

class HandlingContext(pydantic.BaseModel):
    level : ConstraintLevel = ConstraintLevel.WARNING
    remove : bool = False

class MessageFormat(pydantic.BaseModel):
    error_string_template : str
    constraint_context : HandlingContext
    kwargs : Mapping[str,Any]

    def error_string(self, rows: int) -> str:
        if rows > 0:
            header = f"{self.constraint_context.level.name}{" (removed)" if self.constraint_context.remove else ""}"
        else:
            header = "INFO"
        return f"{header}: {self.error_string_template.format(rows=rows, **self.kwargs)}"

@dataclasses.dataclass(frozen=True)
class InvalidRows:
    invalid_rows : T
    message_template : MessageFormat
    context : HandlingContext

    def __post_init__(self):
        if isinstance(self.invalid_rows, pl.LazyFrame):
            object.__setattr__(self, 'invalid_rows', self.invalid_rows.collect())

    def get_message(self) -> str:
        return self.message_template.error_string(self.invalid_rows.shape[0])

    def effective_level(self) -> ConstraintLevel:
        if self.invalid:
            return self.context.level
        return ConstraintLevel.INFO

    @property
    def invalid(self) -> bool:
        return self.invalid_rows.shape[0] > 0

class BoundedConstraint(pydantic.BaseModel):
    type : Literal["bounded"]
    min : float|None = None
    max : float|None = None
    error_string_template : str = "Found {rows} rows in '{field}' with a value outside of the bounds [{min}, {max}]"

    def filter(self, field: str) -> pl.Expr:
        expr = pl.lit(False)
        if self.min is not None:
            expr |= pl.col(field) < self.min
        if self.max is not None:
            expr |= pl.col(field) > self.max
        return expr

class ChoiceConstraint(pydantic.BaseModel):
    type: Literal["choices"]
    choices : tuple[Any,...]
    error_string_template : str = "Found {rows} rows in '{field}' with a value not in {choices}"

    def filter(self, field: str) -> pl.Expr:
        return ~pl.col(field).is_in(self.choices)

class NonEmptyConstraint(pydantic.BaseModel):
    type: Literal["non_empty"]
    error_string_template : str = "Found {rows} rows in '{field}' that were empty"

    def filter(self, field: str) -> pl.Expr:
        return pl.col(field).str.len_chars() == 0

class PopulatedConstraint(pydantic.BaseModel):
    type: Literal["populated"]
    error_string_template : str = "Found {rows} rows in '{field}' that weren't populated"

    def filter(self, field: str) -> pl.Expr:
        return pl.col(field).is_null()

class PopulatedFloatConstraint(pydantic.BaseModel):
    type: Literal["populated float"]
    error_string_template : str = "Found {rows} rows in '{field}' that weren't populated"

    def filter(self, field: str) -> pl.Expr:
        return pl.col(field).is_null() | pl.col(field).is_nan()

class UniqueConstraint(pydantic.BaseModel):
    type: Literal["unique"]
    error_string_template : str = "Found {rows} rows in '{field}' that weren't unique"

    def filter(self, field: str) -> pl.Expr:
        return pl.col(field).is_duplicated()

FieldConstraintContext = Annotated[
    BoundedConstraint | ChoiceConstraint | NonEmptyConstraint | PopulatedConstraint | PopulatedFloatConstraint | UniqueConstraint,
    pydantic.Field(discriminator="type")
]

class FieldConstraint(pydantic.BaseModel):
    constraint_context : FieldConstraintContext
    handling_context : HandlingContext = HandlingContext()

    def error_string(self, field: str) -> MessageFormat:
        return MessageFormat(
            error_string_template=self.constraint_context.error_string_template,
            constraint_context=self.handling_context,
            kwargs={"field": field, **self.constraint_context.model_dump(exclude="type")}
        )

class GreaterConstraint(pydantic.BaseModel):
    type: Literal["greater"]
    greater : str
    lesser : str
    error_string_template : str = "Found {rows} rows where '{lesser}' >= '{greater}'"

    def filter(self) -> pl.Expr:
        return pl.col(self.greater) <= pl.col(self.lesser)

class InequalityConstraint(pydantic.BaseModel):
    type: Literal["inequality"]
    fields : tuple[str,...]
    error_string_template : str = "Found {rows} rows two or more of {fields} had the same value"

    def filter(self) -> pl.Expr:
        return (
            pl.concat_list(self.fields).list.n_unique()
            <
            pl.concat_list(self.fields).list.drop_nulls().list.len()
        )

DataConstraintContext = Annotated[
    GreaterConstraint | InequalityConstraint,
    pydantic.Field(discriminator="type")
]

class DataConstraint(pydantic.BaseModel):
    constraint_context : DataConstraintContext
    handling_context : HandlingContext = HandlingContext()

    def error_string(self) -> MessageFormat:
        return MessageFormat(
            error_string_template=self.constraint_context.error_string_template,
            constraint_context=self.handling_context,
            kwargs=self.constraint_context.model_dump(exclude="type")
        )

class OrderConstraint(pydantic.BaseModel):
    type: Literal["order"]
    first_order : str
    second_order : str
    error_string_template : str = "Found {rows} rows where '{second_order}' was not sorted by '{first_order}"

    def filter(self, data: T) -> T:
        return data.sort(
            self.first_order
        ).filter(
            pl.col(self.second_order) < pl.col(self.second_order).shift(1)
        )

SeriesConstraintContext = Annotated[
    OrderConstraint,
    pydantic.Field(discriminator="type")
]

class SeriesConstraint(pydantic.BaseModel):
    constraint_context : SeriesConstraintContext
    handling_context : HandlingContext = HandlingContext()

    def error_string(self) -> MessageFormat:
        return MessageFormat(
            error_string_template=self.constraint_context.error_string_template,
            constraint_context=self.handling_context,
            kwargs=self.constraint_context.model_dump(exclude="type")
        )
