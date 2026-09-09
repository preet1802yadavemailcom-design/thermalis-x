# THERMALIS-X Production & Container Deployment Guide

## Docker Deployment

### Multi-Container Stack (`docker-compose.yml`)
Runs the FastAPI application, PostgreSQL with PostGIS, and pre-built frontend UI:

```yaml
version: '3.8'
services:
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: thermalis_db
      POSTGRES_USER: thermalis
      POSTGRES_PASSWORD: thermalis_secure_password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg2://thermalis:thermalis_secure_password@db:5432/thermalis_db
      DEMO_MODE: "false"
      REAL_DATA_MODE: "true"
    depends_on:
      - db

volumes:
  pgdata:
```

### Quick Launch Command
```bash
docker compose up -d
```
