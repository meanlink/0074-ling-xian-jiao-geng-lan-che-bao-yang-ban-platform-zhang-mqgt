from fastapi import HTTPException
from core import enqueue
from handoff.followup_store import entries
from handoff.packet_store import packet,save
from handoff.shifts import orders,shift_for,writable
from handoff.slices_store import list_slices
from handoff.weighted import allocated

def board(cx,shift):
    code=shift["code"]
    rows=allocated(list_slices(cx,code),orders(cx,shift))
    followups=entries(cx,code)
    return {"work":rows,"total_minutes":sum(row["minutes"] for row in rows),
            "pending":sum(row["status"]=="open" for row in followups),
            "accepted":[{"id":row["id"],"work":row["work"],"initials":row["initials"]}
                        for row in followups if row["status"]=="ack"]}

def view(cx,code):
    shift=shift_for(cx,code,True)
    item=packet(cx,code)
    return {"board":item["data"] if item else board(cx,shift),"packet":item}

def prepare(cx,code,body):
    data=board(cx,writable(cx,code))
    if data["pending"]:
        raise HTTPException(409,"续办条未获接班人签收")
    if not data["total_minutes"]:
        raise HTTPException(409,"当前班次没有工时可交接")
    job=enqueue(cx,"cabin-handoff",{"shift":code})
    return save(cx,code,body.destination,data,job)
