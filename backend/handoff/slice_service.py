from fastapi import HTTPException
from handoff.shifts import compatible,writable
from handoff.slices_store import add,list_slices
from handoff.weighted import overloaded

def log(cx,body):
    shift=writable(cx,body.shift)
    compatible(cx,shift,body.work)
    if not shift["lo"]<=body.lo<body.hi<=shift["hi"]:
        raise HTTPException(409,"所记工作分钟必须完整落在本班")
    rows=list_slices(cx,body.shift)
    offenders=overloaded(rows+[body.model_dump()])
    if offenders:
        problem=offenders[0]
        raise HTTPException(409,f"{problem['staff']} 在 {problem['minute']} 分钟处的投入权重超过 100%")
    return add(cx,body)
