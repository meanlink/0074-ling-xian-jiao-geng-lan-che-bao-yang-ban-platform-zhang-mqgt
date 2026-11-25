from fastapi import APIRouter,Depends
from core import db,require
from handoff.forms import Packet
from handoff.packet_service import prepare,view

router=APIRouter(prefix="/api/cabin/handoff")

@router.get("/{code}")
def report(code:str,_=Depends(require())):
    with db() as cx: return view(cx,code)

@router.post("/{code}",status_code=201)
def seal(code:str,body:Packet,_=Depends(require("reviewer"))):
    with db() as cx: return prepare(cx,code,body)
