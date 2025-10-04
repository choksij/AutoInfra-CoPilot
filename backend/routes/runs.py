# backend/routes/runs.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Dict
from ..models import RunRequest, StatusResponse
from ..orchestrator import execute_run
from ..services.storage import get_storage

router = APIRouter()

# simple in-memory store for current session
status_store: Dict[str, StatusResponse] = {}


@router.post("/run", response_model=StatusResponse)
def kickoff_run(req: RunRequest) -> StatusResponse:
    # Run synchronously (MVP)
    status_doc = execute_run(req)

    # Cache in-memory for /status
    status_store[status_doc.run_id] = status_doc

    # Persist to storage (CH or Memory) using the new signatures
    try:
        st = get_storage()
        st.insert_run(
            run_id=status_doc.run_id,
            repo=req.repo,
            pr_number=req.pr_number,
            commit_sha=req.commit_sha,
            status=status_doc.status,
            summary=status_doc.summary,
        )
        st.insert_findings(status_doc.run_id, status_doc.findings)

        if status_doc.self_check is not None:
            sc = status_doc.self_check
            st.insert_outcome(
                run_id=status_doc.run_id,
                issues_before=int(sc.get("issues_before", 0)),
                issues_after=int(sc.get("issues_after", 0)),
                policy_before=int(sc.get("policy_before", 0)),
                policy_after=int(sc.get("policy_after", 0)),
                safe_to_merge=status_doc.safe_to_merge,
            )


    except Exception:
        pass

    return status_doc


@router.get("/status", response_model=StatusResponse)
def get_status(run_id: str) -> StatusResponse:
    doc = status_store.get(run_id)
    if not doc:
        raise HTTPException(status_code=404, detail="run_id not found")
    return doc


@router.get("/history")
def get_history(limit: int = 20):
    st = get_storage()
    return [h.model_dump() for h in st.history(limit=limit)]
