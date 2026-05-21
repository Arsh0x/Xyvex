from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Project, Finding, Payload
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Xyvex API running"}

# ── PROJECTS ──

@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    return [p.to_dict() for p in db.query(models.Project).all()]

@app.post("/projects")
def create_project(name: str, target: str, db: Session = Depends(get_db)):
    project = models.Project(name=name, target=target)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.to_dict()

@app.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()

# ── FINDINGS ──

@app.post("/projects/{project_id}/findings")
def add_finding(project_id: int, title: str, severity: str, notes: str = None, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    finding = models.Finding(title=title, severity=severity, notes=notes, project_id=project_id)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding.to_dict()

@app.get("/projects/{project_id}/findings")
def get_findings(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return [f.to_dict() for f in project.findings]

# ── PAYLOADS ──

@app.get("/payloads")
def get_payloads(db: Session = Depends(get_db)):
    return [p.to_dict() for p in db.query(models.Payload).all()]

@app.post("/payloads")
def create_payload(name: str, content: str, category: str, db: Session = Depends(get_db)):
    payload = models.Payload(name=name, content=content, category=category)
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload.to_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)