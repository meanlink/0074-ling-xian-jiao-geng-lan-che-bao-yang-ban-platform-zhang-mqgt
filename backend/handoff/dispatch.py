from fastapi import HTTPException
from handoff.followup_store import release
from handoff.packet_store import send

def deliver(cx,payload):
    # Followups move only once the packet is actually sent.  Marking first and
    # releasing next keeps the two in one transaction; if the release fails
    # (receiver sealed meanwhile) the whole delivery rolls back and the job
    # can be retried without losing the followups.
    sent=send(cx,payload["shift"])
    if not sent: raise HTTPException(409,"交接已送达，无需重复分发")
    moved=release(cx,payload["shift"])
    return {"inbox":sent["destination"],"handoff":sent["shift"],
            "followups_ack":len(sent["data"]["accepted"]),"weighted_minutes":sent["data"]["total_minutes"],
            "followups_moved":[row["id"] for row in moved]}
