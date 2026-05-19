from typing import Optional, List


class Findings():
    def __init__(self, title: str, severity: str, notes: Optional[str] = None) -> None:
        self.title = title
        self.severity = severity
        self.notes = notes
        self.is_confirmed: bool = False

    def confirm(self)->None:
        self.is_confirmed = True

    def to_dict(self)-> dict:
        return {
            "title": self.title,
            "severity": self.severity,
            "notes": self.notes,
            "is_confirmed": self.is_confirmed
        }  
    

class Payload():
    def __init__(self,name: str, content: str, category: str):
        self.name = name
        self.content = content
        self.category = category


    def to_dict(self)-> dict:
        return {
            "name" : self.name,
            "content" : self.content,
            "category" : self.category
        }
    

class Project:
    def __init__(self, name: str, target: str):
        self.name = name
        self.target = target
        self.findings: List[Findings] = []
        self.payloads: List[Payload] = []

    def add_finding(self, finding: Findings) -> None:
        self.findings.append(finding)

    def add_payload(self, payload: Payload) -> None:
        self.payloads.append(payload)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "target": self.target,
            "findings": [f.to_dict() for f in self.findings],
            "payloads": [p.to_dict() for p in self.payloads],
        }