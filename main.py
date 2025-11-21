import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from database import db, create_document, get_documents
from schemas import (
    Journal,
    JournalPage,
    CalendarEvent,
    Sticker,
    Drawing,
)

app = FastAPI(title="Lümn Note API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Lümn Note Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from Lümn Note API"}

# ---------- Schema Introspection ----------
@app.get("/schema")
def get_schema() -> Dict[str, Any]:
    """Expose Pydantic JSON Schemas for the database viewer/tools"""
    models = {
        "journal": Journal,
        "journalpage": JournalPage,
        "calendarevent": CalendarEvent,
        "sticker": Sticker,
        "drawing": Drawing,
    }
    return {
        "schemas": {name: model.model_json_schema() for name, model in models.items()},
        "collections": list(models.keys()),
    }

# ---------- Health / Test ----------
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ---------- Journals ----------
@app.post("/api/journals")
def create_journal(journal: Journal) -> Dict[str, str]:
    inserted_id = create_document("journal", journal)
    return {"id": inserted_id}

@app.get("/api/journals")
def list_journals(limit: int = Query(50, ge=1, le=200)) -> List[Dict[str, Any]]:
    items = get_documents("journal", {}, limit)
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

# ---------- Journal Pages ----------
@app.post("/api/pages")
def create_page(page: JournalPage) -> Dict[str, str]:
    inserted_id = create_document("journalpage", page)
    return {"id": inserted_id}

@app.get("/api/pages")
def get_page(journal_id: str, date: str) -> Dict[str, Any]:
    docs = get_documents("journalpage", {"journal_id": journal_id, "date": date}, 1)
    if not docs:
        raise HTTPException(status_code=404, detail="Page not found")
    doc = docs[0]
    doc["id"] = str(doc.pop("_id"))
    return doc

# ---------- Calendar Events ----------
@app.post("/api/events")
def create_event(event: CalendarEvent) -> Dict[str, str]:
    inserted_id = create_document("calendarevent", event)
    return {"id": inserted_id}

@app.get("/api/events")
def list_events(date: Optional[str] = None, month: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Query by exact date (YYYY-MM-DD) or by month (YYYY-MM) prefix.
    """
    filt: Dict[str, Any] = {}
    if date:
        filt["date"] = date
    elif month:
        filt["date"] = {"$regex": f"^{month}"}
    items = get_documents("calendarevent", filt, None)
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

# ---------- Stickers ----------
@app.post("/api/stickers")
def create_sticker(sticker: Sticker) -> Dict[str, str]:
    inserted_id = create_document("sticker", sticker)
    return {"id": inserted_id}

@app.get("/api/stickers")
def list_stickers(date: Optional[str] = None, month: Optional[str] = None) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if date:
        filt["date"] = date
    elif month:
        filt["date"] = {"$regex": f"^{month}"}
    items = get_documents("sticker", filt, None)
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

# ---------- Drawings ----------
@app.post("/api/drawings")
def create_drawing(drawing: Drawing) -> Dict[str, str]:
    inserted_id = create_document("drawing", drawing)
    return {"id": inserted_id}

@app.get("/api/drawings")
def list_drawings(date: Optional[str] = None, month: Optional[str] = None) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if date:
        filt["date"] = date
    elif month:
        filt["date"] = {"$regex": f"^{month}"}
    items = get_documents("drawing", filt, None)
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

# ---------- Day Aggregate ----------
@app.get("/api/day/{date}")
def get_day(date: str, journal_id: Optional[str] = None) -> Dict[str, Any]:
    resp: Dict[str, Any] = {"date": date}
    # page
    page_docs = get_documents("journalpage", ({"journal_id": journal_id, "date": date} if journal_id else {"date": date}), 1)
    if page_docs:
        p = page_docs[0]
        p["id"] = str(p.pop("_id"))
        resp["page"] = p
    else:
        resp["page"] = None
    # events
    evts = get_documents("calendarevent", {"date": date}, None)
    for e in evts:
        e["id"] = str(e.pop("_id"))
    resp["events"] = evts
    # stickers
    st = get_documents("sticker", {"date": date}, None)
    for s in st:
        s["id"] = str(s.pop("_id"))
    resp["stickers"] = st
    # drawings meta only (points can be large but we store anyway)
    dr = get_documents("drawing", {"date": date}, None)
    for d in dr:
        d["id"] = str(d.pop("_id"))
    resp["drawings"] = dr
    return resp

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
