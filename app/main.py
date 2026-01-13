from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, students, metrics, imports, admin

app = FastAPI(title="Student Risk Platform (Starter)", version="0.1.0")

origins = settings.cors_origin_list()
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(metrics.router)
app.include_router(imports.router)
app.include_router(admin.router)

@app.get("/health")
async def health():
    return {"ok": True}
