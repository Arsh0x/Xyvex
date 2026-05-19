from fastapi import FastAPI
from typing import List
from models import Project, Findings, Payload

app = FastAPI()

# In-memory storage
projects_list = []
payloads_list = []

@app.get("/")
def read_root():
    return {"message": "Xyvex API running"}

@app.get("/projects")
def get_projects():
    return [p.to_dict() for p in projects_list]

@app.post("/projects")
def create_project(name: str, target: str):
    project = Project(name=name, target=target)
    projects_list.append(project)
    return project.to_dict()

@app.get("/payloads")
def get_payloads():
    return [p.to_dict() for p in payloads_list]

@app.post("/payloads")
def create_payload(name: str, content: str, category: str):
    payload = Payload(name=name, content=content, category=category)
    payloads_list.append(payload)
    return payload.to_dict()

@app.post("/projects/{project_index}/findings")
def add_finding(project_index: int, title: str, severity: str, notes: str = None):
    if project_index < 0 or project_index >= len(projects_list):
        return {"error": "Project not found"}
    
    finding = Findings(title=title, severity=severity, notes=notes)
    projects_list[project_index].add_finding(finding)
    return finding.to_dict()

@app.get("/projects/{project_index}/findings")
def get_findings(project_index: int):
    if project_index < 0 or project_index >= len(projects_list):
        return {"error": "Project not found"}
    
    return [f.to_dict() for f in projects_list[project_index].findings]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)