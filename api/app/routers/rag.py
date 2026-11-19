from fastapi import APIRouter

from app.models.schemas import DocumentUpload, RAGQuery, RAGResponse
from app.rag.pipeline import ingest_document, rag_query, retrieve, vector_store

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ingest")
async def ingest(doc: DocumentUpload):
    num_chunks = ingest_document(doc.filename, doc.content, doc.metadata)
    return {
        "filename": doc.filename,
        "chunks_created": num_chunks,
        "total_chunks": vector_store.count,
    }


@router.post("/query", response_model=RAGResponse)
async def query(req: RAGQuery):
    return rag_query(req)


@router.post("/search")
async def search(req: RAGQuery):
    chunks = retrieve(req)
    return {"query": req.query, "results": chunks}


@router.get("/stats")
async def stats():
    return {"total_chunks": vector_store.count}


@router.delete("/clear")
async def clear():
    vector_store.clear()
    return {"status": "cleared"}
