from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router_users
app = FastAPI()
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# app.include_router(router_get_matchs.router, prefix="/api/v1/matchs")
app.include_router(router_users.router, prefix="/api/v1/users")
# app.include_router(router_get_report.router, prefix="/api/v1/report")