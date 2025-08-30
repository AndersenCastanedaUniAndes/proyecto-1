## � CQRS inventario (FastAPI + PostgreSQL + Redis)

uvicorn app:app --reload                // Staging
uvicorn app:app --reload --workers 4    // Prod
uvicorn app:app --workers 4 --loop uvloop --http httptools

python .\consumers.py



# Consumer A
CONSUMER_NAME=c-a python consumers.py

# Consumer B
CONSUMER_NAME=c-b python consumers.py
