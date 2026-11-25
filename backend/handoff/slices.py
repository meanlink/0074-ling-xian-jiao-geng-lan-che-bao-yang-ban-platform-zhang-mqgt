from fastapi import APIRouter,Depends
from core import db,require
from handoff.forms import Slice
from handoff.slice_service import log
from handoff.slices_store import list_slices

router=APIRouter(prefix="/api/cabin")

@router.get("/shifts/{code}/slices")
def slices(code:str,_=Depends(require())):
    with db() as cx: return list_slices(cx,code)

@router.post("/slices",status_code=201)
def create(body:Slice,_=Depends(require("operator"))):
    with db() as cx: return log(cx,body)
