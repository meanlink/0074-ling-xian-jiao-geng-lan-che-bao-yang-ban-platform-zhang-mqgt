from fastapi import APIRouter,Depends
from core import db,require
from handoff.forms import Accept,Followup
from handoff.followup_store import accept,entries,log,lookup
from handoff.shifts import compatible,writable

router=APIRouter(prefix="/api/cabin")

@router.get("/shifts/{code}/followups")
def list_entries(code:str,_=Depends(require())):
    with db() as cx: return entries(cx,code)

@router.post("/followups",status_code=201)
def create(body:Followup,_=Depends(require("operator"))):
    with db() as cx:
        compatible(cx,writable(cx,body.shift),body.work)
        return log(cx,body)

@router.put("/followups/{code}")
def acknowledge(code:str,body:Accept,user=Depends(require("reviewer"))):
    with db() as cx:
        writable(cx,lookup(cx,code)["shift"])
        return accept(cx,code,user["email"],body)
