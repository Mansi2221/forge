import logging

import anthropic
from fastapi import APIRouter, HTTPException

from app.models.schemas import DocumentUpload, RAGQuery, RAGResponse
from app.rag.pipeline import ingest_document, rag_query, retrieve, vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ingest")
async def ingest(doc: DocumentUpload):
    if not doc.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty")
    if len(doc.content) > 500000:
        raise HTTPException(status_code=400, detail="Document exceeds maximum size (500K chars)")
    num_chunks = ingest_document(doc.filename, doc.content, doc.metadata)
    return {
        "filename": doc.filename,
        "chunks_created": num_chunks,
        "total_chunks": vector_store.count,
    }


@router.post("/query", response_model=RAGResponse)
async def query(req: RAGQuery):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        return rag_query(req)
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except anthropic.APIError as e:
        logger.error("RAG query failed: %s", e.message)
        raise HTTPException(status_code=502, detail="LLM service error")


@router.post("/search")
async def search(req: RAGQuery):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    chunks = retrieve(req)
    return {"query": req.query, "results": chunks}


@router.get("/stats")
async def stats():
    return {"total_chunks": vector_store.count}


@router.delete("/clear")
async def clear():
    vector_store.clear()
    return {"status": "cleared"}
