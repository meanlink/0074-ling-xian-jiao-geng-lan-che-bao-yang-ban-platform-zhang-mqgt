from fastapi import APIRouter,Depends,HTTPException
from core import db,require
from handoff.forms import Accept,Close,Followup
from handoff.followup_store import close,entries,everything,incoming,log,lookup,sign
from handoff.shifts import compatible,later_shift,sealed,shift_for,writable

router=APIRouter(prefix="/api/cabin")

def detail(row):
    return {"id":row["id"],"origin":row["origin"],"shift":row["shift"],
            "work":row["work"],"matter":row["matter"],"status":row["status"],
            "receiver":row["receiver"],"initials":row["initials"],
            "next_shift":row["next_shift"],"delivered_to":row["delivered_to"],
            "origin_team":row["origin_team"],"origin_lo":row["origin_lo"],"origin_hi":row["origin_hi"],
            "holder_team":row["holder_team"],"holder_lo":row["holder_lo"],"holder_hi":row["holder_hi"],
            "next_team":row["next_team"],"delivered_team":row["delivered_team"],
            "closed_by":row["closed_by"],"closed_initials":row["closed_initials"],
            "signed_at":row["signed_at"],"delivered_at":row["delivered_at"],"closed_at":row["closed_at"]}

@router.get("/shifts/{code}/followups")
def list_entries(code:str,_=Depends(require())):
    with db() as cx: return [detail(row) for row in entries(cx,code)]

@router.get("/shifts/{code}/incoming")
def list_incoming(code:str,_=Depends(require())):
    """Signed off to this shift; the delivering shift has not sent yet."""
    with db() as cx: return [detail(row) for row in incoming(cx,code)]

@router.get("/followups")
def list_all(_=Depends(require())):
    with db() as cx: return [detail(row) for row in everything(cx)]

@router.post("/followups",status_code=201)
def create(body:Followup,_=Depends(require("operator"))):
    with db() as cx:
        compatible(cx,writable(cx,body.shift),body.work)
        return log(cx,body)

@router.put("/followups/{code}")
def acknowledge(code:str,body:Accept,user=Depends(require("reviewer"))):
    with db() as cx:
        row=lookup(cx,code)
        # Lock in the same order sealing uses: holding shift, receiving shift,
        # then the followup itself, so sign-off and seal cannot interleave.
        holder=shift_for(cx,row["shift"],True)
        if sealed(cx,holder["code"],False):
            raise HTTPException(409,"此班交接已封口")
        target=later_shift(cx,holder,body.next_shift)
        return sign(cx,code,holder["code"],user["email"],body,target["code"])

@router.put("/followups/{code}/close")
def finish(code:str,body:Close,user=Depends(require("reviewer"))):
    with db() as cx:
        row=lookup(cx,code)
        holder=shift_for(cx,row["shift"],True)
        if sealed(cx,holder["code"],False):
            raise HTTPException(409,"此班交接已封口")
        return close(cx,code,holder["code"],user["email"],body)
