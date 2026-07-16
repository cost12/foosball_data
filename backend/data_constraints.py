from typing import Annotated, Literal, Any
import logging

import pydantic

logger = logging.getLogger(__name__)

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
