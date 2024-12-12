# LiveVote API

---
## Requirements

- [FastAPI](https://fastapi.tiangolo.com)
- [Uvicorn](https://www.uvicorn.org)
- [SQLAlchemy](https://www.sqlalchemy.org)
- [PyMySQL](https://pypi.org/project/PyMySQL)
- [email-validator](https://pypi.org/project/email-validator)
- [SQLModel](https://sqlmodel.tiangolo.com)
- [python-jose](https://pypi.org/project/python-jose)
- [passlib[bcrypt]](https://pypi.org/project/passlib)
- [pytz](https://pypi.org/project/pytz)
- [python-dateutil](https://pypi.org/project/python-dateutil)
- [python-dotenv](https://pypi.org/project/python-dotenv)

## Specification

#### Minimum System Requirements:
- VCPUs: 0.25
- Memory: 0.5 GB
- Storage: 3 GB

#### Recommended System Requirements:
- VCPUs: 0.25
- Memory: 1 GB
- Storage: 5 GB

## Installation & Run Server Guide
### Clone Repository And Install Requirements
Open terminal and run these command:
```bash
git clone https://github.com/C242-LT-Liveness-Detection/live-vote-cc.git
cd live-vote-cc
pip install -r
```
### Run Server
Run these command in terminal:
```bash
uvicorn app.main:app
```
