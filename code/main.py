from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from routers import auth
from routers import assessment
from routers import therapy
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from config import setting

app = FastAPI(
    title="Therapeutic Tool For ADHD APIs ",
    docs_url="/",
    description="Project by Riddhi's Team",
    version="0.0.1",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="APIs for Therapeutic Tool For ADHD",
        version="0.1.0",
        description="A Virtual Reality Therapeutic Tool For ADHD",
        routes=app.routes,
        servers=[{"url": setting.SERVER}] if setting.SERVER != "" else [],
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://mapmycrop.store/images/logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# add multiple routers here ->
app.include_router(auth.route)
app.include_router(assessment.route)
app.include_router(therapy.route)


@app.get("/")
def home():
    return {"data": "at home"}