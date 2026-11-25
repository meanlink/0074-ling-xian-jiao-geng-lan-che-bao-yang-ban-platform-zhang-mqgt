from handoff.packet_store import send

def deliver(cx,payload):
    sent=send(cx,payload["shift"])
    return {"inbox":sent["destination"],"handoff":sent["shift"],
            "followups_ack":len(sent["data"]["accepted"]),"weighted_minutes":sent["data"]["total_minutes"]}
