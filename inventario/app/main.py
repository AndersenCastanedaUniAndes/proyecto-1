from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as inventario_router


def create_app() -> FastAPI:
    app = FastAPI(title="Inventario Service", version="0.1.0")

    # Allow local frontend dev server and same-origin calls
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    app.include_router(inventario_router)
    return app


app = create_app()
