from fastapi import FastAPI
import models
import routes
from core import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Auth Service")

app.include_router(routes.router, prefix="/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
