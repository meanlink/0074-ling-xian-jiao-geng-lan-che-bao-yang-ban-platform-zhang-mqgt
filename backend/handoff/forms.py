from typing import Annotated, Literal
from pydantic import BaseModel, Field, model_validator

Key = Annotated[str, Field(pattern=r"^[A-Z0-9-]{3,24}$")]
Initials = Annotated[str, Field(min_length=2, max_length=24)]

SIGNATURE_ALIASES = ("initials", "signature", "signed_by", "receiver_initials")
TARGET_ALIASES = ("next_shift", "next", "nextShift", "target_shift", "target",
                  "handover_to", "receiver_shift")

def _pick(data, names):
    if not isinstance(data, dict): return None
    for name in names:
        value = data.get(name)
        if isinstance(value, str) and value.strip(): return value.strip()
    return None

class _Aliased(BaseModel):
    """Accept the canonical field name plus a few obvious spellings."""

    @model_validator(mode="before")
    @classmethod
    def canonical(cls, data):
        if not isinstance(data, dict): return data
        found = {}
        initials = _pick(data, SIGNATURE_ALIASES)
        if initials is not None: found["initials"] = initials
        target = _pick(data, TARGET_ALIASES)
        if target is not None: found["next_shift"] = target
        return data | found

class Slice(BaseModel):
    code: Key
    shift: Key
    work: Key
    lo: int = Field(ge=0, lt=2880)
    hi: int = Field(gt=0, le=2880)
    staff: str = Field(min_length=2, max_length=60)
    weight: Literal[25, 50, 75, 100]

    @model_validator(mode="after")
    def length(self):
        if self.hi <= self.lo: raise ValueError("结束须晚于开始")
        return self

class Followup(BaseModel):
    id: Key
    shift: Key
    work: Key
    matter: str = Field(min_length=5, max_length=240)

class Accept(_Aliased):
    initials: Initials
    next_shift: Key

class Close(_Aliased):
    initials: Initials

class Packet(BaseModel):
    destination: Literal["lead", "desk"]
