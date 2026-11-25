from fastapi import APIRouter
from handoff import followups,packets,roster,slices
from handoff.demo import seed
from handoff.dispatch import deliver

router=APIRouter()
for section in (roster,slices,followups,packets):
    router.include_router(section.router)

def run_job(cx,kind,payload):
    if kind=="cabin-handoff": return deliver(cx,payload)
    raise ValueError(f"Unknown cabin task {kind}")
