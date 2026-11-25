from fastapi import HTTPException
from handoff.followup_store import entries,incoming
from handoff.packet_store import packet,save
from handoff.shifts import orders,sealed,shift_for,writable
from handoff.slices_store import list_slices
from handoff.weighted import allocated

def board(cx,shift):
    code=shift["code"]
    rows=allocated(list_slices(cx,code),orders(cx,shift))
    followups=entries(cx,code)
    waiting=incoming(cx,code)
    return {"work":rows,"total_minutes":sum(row["minutes"] for row in rows),
            "pending":sum(row["status"]=="open" for row in followups),
            "unsettled":sum(row["status"]=="held" for row in followups),
            "incoming":len(waiting),
            "accepted":[{"id":row["id"],"work":row["work"],"initials":row["initials"],
                         "holder":row["shift"],"next_shift":row["next_shift"],
                         "next_team":row["next_team"],"status":row["status"]}
                        for row in followups if row["status"]!="open"]}

def view(cx,code):
    shift=shift_for(cx,code)
    item=packet(cx,code)
    job=None
    if item and item["delivery"]=="pending":
        job=cx.execute("SELECT id,status,error,attempts FROM app_jobs WHERE id=%s",(item["job_id"],)).fetchone()
    return {"board":item["data"] if item else board(cx,shift),"packet":item,
            "job":job,"incoming":incoming(cx,code)}

def seal(cx,code,body):
    """Freeze the board and enqueue dispatch; followups move on delivery only.

    A signature cannot slip in between the pending check and the handoff
    insert: signing locks this same shift row first, and seal holds it until
    its handoff row is written.
    """
    from core import enqueue
    shift=writable(cx,code)
    data=board(cx,shift)
    if data["pending"]:
        raise HTTPException(409,"续办条未获接班人签收")
    if data["unsettled"]:
        raise HTTPException(409,"本班还有待办结或再交的续办条")
    if data["incoming"]:
        raise HTTPException(409,"本班还有未送达的续办条，须等上游班次完成交接")
    if not data["total_minutes"]:
        raise HTTPException(409,"当前班次没有工时可交接")
    job=enqueue(cx,"cabin-handoff",{"shift":code})
    return save(cx,code,body.destination,data,job)

def retry(cx,code):
    """Requeue a failed dispatch against the same frozen handoff.

    No second handoff is written and no second job is created, so a retry can
    never produce a duplicate follow-up packet.  The handoff row is read, not
    locked: the worker holds the job row while delivering, and taking these
    locks in the opposite order would deadlock with a retry in flight.
    """
    from core import retry as retry_job
    item=packet(cx,code)
    if not item: raise HTTPException(404,"此班尚未封口")
    if item["delivery"]=="sent":
        raise HTTPException(409,"此班交接已送达")
    if not retry_job(cx,item["job_id"]):
        raise HTTPException(409,"分发尚未失败，无需重试")
    return packet(cx,code)
