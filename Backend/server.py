from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes.upload_routes import router
from models.ai_models import load_models

# -------------------------
# Lifespan handler: Load AI models at startup
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Loading AI models...")
    load_models()  # Load YOLO & OCR models here
    print("✅ AI models loaded successfully")
    yield
    print("🛑 API shutting down...")


# -------------------------
# Create FastAPI app
# -------------------------
app = FastAPI(
    title="License Plate Recognition API",
    lifespan=lifespan
)

# -------------------------
# Enable CORS for frontend
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Include Routes
# -------------------------
app.include_router(router)