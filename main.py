import time

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse

from fastapi_limiter import FastAPILimiter



from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from src.routes import contacts, auth, users
from src.database.db import get_db
from src.conf.config import settings




app = FastAPI()

origins = [
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):

    """
    The add_process_time_header function is a middleware function that adds the time it took to process
    the request in seconds;.

    :param request: Request: Get the request object
    :param call_next: Call the next function in the pipeline
    :return: The response object with a new header called &quot;process-time&quot;

    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
async def startup():

    """
    The startup function is used for limiting the number of requests .

    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

@app.get('/')
async def root():

    """
    The root function is the entry point for the API.
    It returns a simple message to let you know that it works.

    """
    return {'message': "Hello, if you see this message it is great"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):

    """
    The healthchecker function is a simple function that checks if the database is configured correctly.

    :param db: Session: Pass the database session to the function
    :return: A dict with a message key

    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")



app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')



