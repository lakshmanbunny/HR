import os
import sys

# Backend package root (contains app/, core/, workflows/, config/)
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db

# ------ LangSmith Tracing ------
os.environ["LANGCHAIN_TRACING_V2"] = "true"
if settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT or "recruitment-poc"

# Initialize database first before importing routes/services that depend on it
init_db()

from app.api.routes import router
from app.interview.routes import router as interview_router
from app.api.opencats_routes import router as opencats_router

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     duration = time.time() - start_time
#     print(f"--- [API] {request.method} {request.url.path} - {response.status_code} ({duration:.2f}s) ---")
#     return response


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.chatbot_routes import router as chatbot_router

# Include API routes
app.include_router(router, prefix=settings.API_V1_STR)
app.include_router(interview_router, prefix=f"{settings.API_V1_STR}/interview")
app.include_router(chatbot_router, prefix=f"{settings.API_V1_STR}/chatbot")
app.include_router(opencats_router, prefix=f"{settings.API_V1_STR}/opencats")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Recruitment Screening API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
