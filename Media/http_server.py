### http_server.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from storage import MEDIA_ROOT

app = FastAPI()
# Mount media directory to serve static files
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")
