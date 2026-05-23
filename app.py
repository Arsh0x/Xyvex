from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Project, Finding, Payload, User
from auth import hash_password, verify_password, create_access_token, decode_token
from schemas import UserCreate, TokenResponse, ProjectCreate, FindingCreate, PayloadCreate
from typing import Optional
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/")
def read_root():
    return {"message": "Xyvex API running"}

# ── AUTH ──

@app.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = models.User(email=user_data.email, hashed_password=hash_password(user_data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=TokenResponse)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

# ── PROJECTS ──

@app.get("/projects")
def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [p.to_dict() for p in db.query(models.Project).filter(models.Project.user_id == current_user.id).all()]

@app.post("/projects")
def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = models.Project(name=project_data.name, target=project_data.target, user_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.to_dict()

@app.get("/projects/{project_id}")
def get_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()

# ── FINDINGS ──

@app.post("/projects/{project_id}/findings")
def add_finding(project_id: int, finding_data: FindingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    finding = models.Finding(
        title=finding_data.title,
        severity=finding_data.severity,
        notes=finding_data.notes,
        project_id=project_id
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding.to_dict()

@app.get("/projects/{project_id}/findings")
def get_findings(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return [f.to_dict() for f in project.findings]

# ── PAYLOADS ──

@app.get("/payloads")
def get_payloads(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [p.to_dict() for p in db.query(models.Payload).all()]

@app.post("/payloads")
def create_payload(payload_data: PayloadCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = models.Payload(
        name=payload_data.name,
        content=payload_data.content,
        category=payload_data.category
    )
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload.to_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)