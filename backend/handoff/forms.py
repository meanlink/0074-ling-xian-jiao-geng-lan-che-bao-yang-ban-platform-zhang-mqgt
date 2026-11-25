from typing import Literal
from pydantic import BaseModel,Field,model_validator

Key=Field(pattern=r"^[A-Z0-9-]{3,24}$")

class Slice(BaseModel):
    code:str=Key
    shift:str=Key
    work:str=Key
    lo:int=Field(ge=0,lt=2880)
    hi:int=Field(gt=0,le=2880)
    staff:str=Field(min_length=2,max_length=60)
    weight:Literal[25,50,75,100]

    @model_validator(mode="after")
    def length(self):
        if self.hi<=self.lo: raise ValueError("结束须晚于开始")
        return self

class Followup(BaseModel):
    id:str=Key
    shift:str=Key
    work:str=Key
    matter:str=Field(min_length=5,max_length=240)

class Accept(BaseModel):
    initials:str=Field(min_length=2,max_length=24)

class Packet(BaseModel):
    destination:Literal["lead","desk"]
