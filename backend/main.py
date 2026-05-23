from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import compare, receipt

load_dotenv()

app = FastAPI(title="Smart Shopping Destination")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compare.router, prefix="/api")
app.include_router(receipt.router, prefix="/api")
