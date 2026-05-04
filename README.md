# infra-pulse

Infrastructure health-check REST API. Checks TCP port reachability
and ICMP ping across any host. Built as a production-grade project
to demonstrate containerization, CI/CD, and API design.

## Live demo
https://infra-pulse.yourdomain.com/docs

## Stack
- **FastAPI** — async REST API with auto-generated Swagger docs
- **Docker** — multi-stage build, non-root, minimal image (~70 MB)
- **GitHub Actions** — test → build → push to GHCR → deploy
- **Nginx** — reverse proxy with TLS (Let's Encrypt)
- **pytest** — full test suite runs in CI before every deploy

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Service info |
| GET | `/health` | No | Health check + uptime |
| GET | `/docs` | No | Interactive API docs |
| GET | `/api/v1/check/port/{host}/{port}` | Key | TCP port check |
| GET | `/api/v1/check/ping/{host}` | Key | ICMP ping check |
| POST | `/api/v1/batch` | Key | Batch check up to 20 hosts |

## Run locally
```bash
git clone https://github.com/YOUR_USERNAME/infra-pulse
cd infra-pulse
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
# Open http://localhost:8000/docs
```

## Run with Docker
```bash
docker build -t infra-pulse .
docker run -p 8000:8000 --env-file .env infra-pulse
```
