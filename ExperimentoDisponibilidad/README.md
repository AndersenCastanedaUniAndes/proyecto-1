## � CQRS inventario (FastAPI + PostgreSQL + Redis)

uvicorn app:app --reload                // Staging
uvicorn app:app --reload --workers 4    // Prod
uvicorn app:app --workers 4 --loop uvloop --http httptools

python .\consumers.py