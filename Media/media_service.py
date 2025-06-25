### media_service.py
import os
import asyncio
from concurrent import futures
from datetime import datetime

import grpc
from pymongo import MongoClient
from google.protobuf import empty_pb2
from google.protobuf import empty_pb2

import proto.media_pb2 as media_pb2
import proto.media_pb2_grpc as media_pb2_grpc
from storage import save_file, remove_file, BASE_URL
from rabit import publish_event

import asyncio
import threading
import grpc
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from proto.media_pb2_grpc import add_MediaServiceServicer_to_server
from proto import media_pb2_grpc, media_pb2


# MONGO_URL = os.getenv("MONGO_URL", "mongodb://root:admin@localhost:27017/core_db?authSource=admin")
# GRPC_PORT = int(os.getenv("GRPC_PORT", "50052"))
from config import get_settings
settings = get_settings()

MONGO_URL = settings.mongo_uri
GRPC_PORT = settings.grpc_port



class MediaService(media_pb2_grpc.MediaServiceServicer):
    def __init__(self):
        client = MongoClient(MONGO_URL)
        self.db = client.get_database("media_db")
        self.collection = self.db.get_collection("media")

    async def UploadProfilePicture(self, request, context):
        user_id = request.user_id
        rel_path = f"profile/{user_id}/{request.filename}"
        save_file(rel_path, request.data)
        doc = {
            "entity": "profile",
            "entity_id": user_id,
            "filename": request.filename,
            "path": rel_path,
            "url": f"{BASE_URL}/{rel_path}",
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(doc)
        media_id = str(result.inserted_id)
        # Publish event asynchronously
        asyncio.create_task(
            publish_event("media.profile_uploaded", {"user_id": user_id, "media_id": media_id, "url": doc["url"]})
        )
        return media_pb2.UploadMediaResponse(media_id=media_id, url=doc["url"])

    async def RemoveProfilePicture(self, request, context):
        user_id = request.user_id
        doc = self.collection.find_one_and_delete({"entity": "profile", "entity_id": user_id})
        if doc:
            remove_file(doc["path"])
            asyncio.create_task(
                publish_event("media.profile_removed", {"user_id": user_id, "media_id": str(doc["_id"])})
            )
        return empty_pb2.Empty()

    async def UploadProductImage(self, request, context):
        product_id = request.product_id
        rel_path = f"product/{product_id}/{request.filename}"
        save_file(rel_path, request.data)
        doc = {
            "entity": "product",
            "entity_id": product_id,
            "filename": request.filename,
            "path": rel_path,
            "url": f"{BASE_URL}/{rel_path}",
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(doc)
        media_id = str(result.inserted_id)
        asyncio.create_task(
            publish_event("media.product_image_uploaded", {"product_id": product_id, "media_id": media_id, "url": doc["url"]})
        )
        return media_pb2.UploadMediaResponse(media_id=media_id, url=doc["url"])

    async def RemoveProductImage(self, request, context):
        from bson import ObjectId
        doc = self.collection.find_one_and_delete({"_id": ObjectId(request.media_id), "entity": "product"})
        if doc:
            remove_file(doc["path"])
            asyncio.create_task(
                publish_event("media.product_image_removed", {"product_id": doc["entity_id"], "media_id": request.media_id})
            )
        return empty_pb2.Empty()

    async def SaveProfilePictureMeta(self, request, context):
        user_id = request.user_id
        rel_path = f"profile/{user_id}/{request.filename}"

        doc = {
            "entity": "profile",
            "entity_id": user_id,
            "filename": request.filename,
            "path": rel_path,
            "url": f"{BASE_URL}/{rel_path}",
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(doc)
        media_id = str(result.inserted_id)

        asyncio.create_task(
            publish_event("media.profile_uploaded", {
                "user_id": user_id,
                "media_id": media_id,
                "url": doc["url"]
            })
        )

        return media_pb2.UploadMediaResponse(media_id=media_id, url=doc["url"])



app = FastAPI(title="Media Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def grpc_server():
    server = grpc.aio.server()
    add_MediaServiceServicer_to_server(MediaService(), server)
    server.add_insecure_port("[::]:50052")  # gRPC port
    await server.start()
    print("✅ gRPC Media server started on port 50052")
    await server.wait_for_termination()

def start_grpc_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(grpc_server())

if __name__ == "__main__":
    threading.Thread(target=start_grpc_thread, daemon=True).start()
    uvicorn.run("media_service:app", host="0.0.0.0", port=8002, reload=True)
