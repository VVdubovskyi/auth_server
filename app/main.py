from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from admin import adminModels, adminRoutes
from core import database

adminModels.Base.metadata.create_all(bind=database.engine)



app = FastAPI(title="Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:5173"],  # або ["*"] для всіх
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(adminRoutes.router, prefix="/api/admin", tags=["AdminAuth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
