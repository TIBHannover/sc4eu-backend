from fastapi import FastAPI
from vote_views.views import term_router, vote_router, term_vote_router
from views.notification_view import notification_router
from dotenv import load_dotenv
import os

fastapi_app = FastAPI(title="FastAPI Vote Service")
fastapi_app.include_router(term_router)
fastapi_app.include_router(vote_router)
fastapi_app.include_router(term_vote_router)
fastapi_app.include_router(notification_router)

load_dotenv()

HOST = str(os.environ.get('FASTAPI_HOST'))
PORT = os.environ.get('FASTAPI_PORT')

if PORT is not None:
    PORT = int(PORT)
else:
    raise ValueError("FASTAPI_PORT environment variable is required")
    
@fastapi_app.get("/fastapi")
def health():
    return {"status": "FastAPI running locally"}

# Only run the server when this file is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host=HOST, port=PORT)