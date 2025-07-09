from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import init_db
from backend.app.routers import auth, users, tests, reports, resources, notifications, gdpr
from backend.app.api import disc

app = FastAPI(title="Corporate Wellbeing Platform API")

origins = [
    "http://localhost",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tests.router)
app.include_router(reports.router)
app.include_router(resources.router)
app.include_router(notifications.router)
app.include_router(gdpr.router)
app.include_router(disc.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()