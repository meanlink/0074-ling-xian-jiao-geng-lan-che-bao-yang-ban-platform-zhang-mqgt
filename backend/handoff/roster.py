from fastapi import APIRouter,Depends
from core import db,require
from handoff.shifts import orders,shift_for

router=APIRouter(prefix="/api/cabin")

@router.get("/shifts")
def list_shifts(_=Depends(require())):
    with db() as cx:
        return cx.execute("SELECT * FROM cabin_shifts ORDER BY roster_day DESC,lo,code").fetchall()

@router.get("/shifts/{code}/orders")
def list_orders(code:str,_=Depends(require())):
    with db() as cx:
        return orders(cx,shift_for(cx,code))
