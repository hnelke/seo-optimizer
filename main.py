import os
import json
import datetime
import urllib.parse
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment variables from .env file if it exists
def load_dotenv(dotenv_path=".env"):
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            key, val = parts
                            # Strip quotes
                            val_clean = val.strip().strip("'").strip('"')
                            os.environ[key.strip()] = val_clean
        except Exception as e:
            print(f"[WARNING] Fehler beim Laden der .env Datei: {e}")

load_dotenv()

from analyzer import fetch_and_analyze

app = FastAPI(
    title="SEO & KI-Readiness Analyzer",
    description="Ein Tool zur Auditierung von Webseiten auf traditionelles SEO und Google AI Overviews Bereitschaft mit Historie.",
    version="2.0.0"
)

# Paths configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
reports_file = os.path.join(current_dir, "reports.json")

def normalize_reports_db():
    if not os.path.exists(reports_file):
        return
    try:
        modified = False
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
        
        if "domains" in db:
            new_domains = {}
            for domain, reports in db["domains"].items():
                lower_domain = domain.lower()
                if lower_domain != domain:
                    modified = True
                
                normalized_reports = []
                for r in reports:
                    if "url" in r:
                        lower_url = r["url"].lower()
                        if r["url"] != lower_url:
                            r["url"] = lower_url
                            modified = True
                    normalized_reports.append(r)
                
                if lower_domain in new_domains:
                    new_domains[lower_domain].extend(normalized_reports)
                    modified = True
                else:
                    new_domains[lower_domain] = normalized_reports
            
            # Sort reports in each domain by timestamp to keep them chronological
            for domain in new_domains:
                new_domains[domain].sort(key=lambda x: x.get("timestamp", ""))
                
            db["domains"] = new_domains
            
        if modified:
            with open(reports_file, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            print("[INFO] reports.json erfolgreich auf Kleinbuchstaben normalisiert.")
    except Exception as e:
        print(f"[WARNING] Fehler bei der Normalisierung von reports.json: {e}")

normalize_reports_db()

if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Mount the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class AnalyzeRequest(BaseModel):
    url: str
    gemini_api_key: Optional[str] = None

def save_report(report: dict) -> dict:
    """Helper to save report inside reports.json grouped by domain."""
    url = report["url"].lower()
    report["url"] = url
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc.lower() if parsed_url.netloc else "unknown-domain"
    
    # Add timestamp
    timestamp = datetime.datetime.now().isoformat()
    report["timestamp"] = timestamp
    
    # Load database
    db = {"domains": {}}
    if os.path.exists(reports_file):
        try:
            with open(reports_file, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            pass # fallback to empty if corrupted
            
    if "domains" not in db:
        db["domains"] = {}
        
    if domain not in db["domains"]:
        db["domains"][domain] = []
        
    # Append new report to this domain's history
    db["domains"][domain].append(report)
    
    # Save back
    with open(reports_file, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        
    return report

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(
        content="<h1>SEO & KI-Readiness Analyzer</h1><p>index.html fehlt im static-Ordner.</p>",
        status_code=200
    )

@app.get("/glossar", response_class=HTMLResponse)
async def read_glossary():
    glossary_path = os.path.join(static_dir, "glossary.html")
    if os.path.exists(glossary_path):
        return FileResponse(glossary_path)
    return HTMLResponse(
        content="<h1>SEO & KI-Readiness Analyzer - Glossar</h1><p>glossary.html fehlt im static-Ordner.</p>",
        status_code=404
    )

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(static_dir, "favicon.ico"))


@app.post("/api/analyze")
async def api_analyze(request: AnalyzeRequest):
    url = request.url.strip().lower()
    if not url:
        raise HTTPException(status_code=400, detail="Die URL darf nicht leer sein.")
    
    if not url.startswith(("http://", "https://")) and "." not in url:
        raise HTTPException(status_code=400, detail="Bitte gib eine gültige Domain oder URL ein (z. B. wikipedia.org).")
        
    try:
        # Pass the api key to fetch_and_analyze if provided in request
        report = await fetch_and_analyze(url, gemini_api_key=request.gemini_api_key)
        # Save report to reports.json
        saved = save_report(report)
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def api_history():
    """Returns a list of all analyzed domains and their runs (without full details to keep payload small)."""
    if not os.path.exists(reports_file):
        return {"domains": {}}
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        slim_history = {}
        for domain, reports in db.get("domains", {}).items():
            slim_history[domain] = []
            for r in reports:
                slim_history[domain].append({
                    "timestamp": r.get("timestamp"),
                    "url": r.get("url"),
                    "overall_score": r.get("overall_score"),
                    "scores": r.get("scores")
                })
        return {"domains": slim_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Historie: {str(e)}")

@app.get("/api/report")
async def api_report(domain: str, timestamp: str):
    """Fetches a specific full report from the database."""
    domain = domain.lower()
    if not os.path.exists(reports_file):
        raise HTTPException(status_code=404, detail="Keine Berichte vorhanden.")
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        reports = db.get("domains", {}).get(domain, [])
        for r in reports:
            if r.get("timestamp") == timestamp:
                return r
                
        raise HTTPException(status_code=404, detail="Bericht zu diesem Zeitstempel nicht gefunden.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/report")
async def api_delete_report(domain: str, timestamp: str):
    """Deletes a specific report run from the database."""
    domain = domain.lower()
    if not os.path.exists(reports_file):
        raise HTTPException(status_code=404, detail="Keine Berichte vorhanden.")
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        reports = db.get("domains", {}).get(domain, [])
        new_reports = [r for r in reports if r.get("timestamp") != timestamp]
        
        if len(new_reports) == len(reports):
            raise HTTPException(status_code=404, detail="Bericht zum angegebenen Zeitstempel nicht gefunden.")
            
        if not new_reports:
            # Delete domain key entirely if no runs left
            del db["domains"][domain]
        else:
            db["domains"][domain] = new_reports
            
        with open(reports_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "message": "Bericht gelöscht."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/domain")
async def api_delete_domain(domain: str):
    """Deletes an entire domain and all its reports from the database."""
    domain = domain.lower()
    if not os.path.exists(reports_file):
        raise HTTPException(status_code=404, detail="Keine Berichte vorhanden.")
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        if domain not in db.get("domains", {}):
            raise HTTPException(status_code=404, detail="Domain nicht gefunden.")
            
        del db["domains"][domain]
        
        with open(reports_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "message": f"Domain {domain} komplett gelöscht."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time

    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")

    print("Starte SEO & KI-Readiness Analyzer auf http://localhost:8000 ...")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
