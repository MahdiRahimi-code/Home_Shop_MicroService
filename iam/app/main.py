import asyncio
import threading
import grpc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from iam_pb2_grpc import add_IAMServiceServicer_to_server
from grpc_impl.iam_service import IAMService
from routers import user, admin
import uvicorn

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # یا دقیق‌تر: ["http://localhost:5000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(user.router)

# تابع اجرای gRPC سرور
async def grpc_server():
    server = grpc.aio.server()
    add_IAMServiceServicer_to_server(IAMService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("✅ gRPC IAM server started on port 50051")
    await server.wait_for_termination()

# اجرای هم‌زمان gRPC و FastAPI
def start_servers():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(grpc_server())

if __name__ == "__main__":
    # اجرای gRPC سرور در ترد جدا
    threading.Thread(target=start_servers, daemon=True).start()
    # اجرای FastAPI با Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
