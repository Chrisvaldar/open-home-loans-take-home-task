from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import compare, receipt

load_dotenv()

PRODUCTION_FRONTEND_ORIGIN = "https://open-home-loans-take-home-task.vercel.app"

app = FastAPI(title="Frugl")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        PRODUCTION_FRONTEND_ORIGIN,
    ],
    allow_origin_regex=r"https://open-home-loans-take-home-task.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compare.router, prefix="/api")
app.include_router(receipt.router, prefix="/api")
