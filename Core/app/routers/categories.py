from fastapi import APIRouter, Depends
from app.schemas import CategoryOut
from app.deps import get_db

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryOut])
async def visit_categories(db=Depends(get_db)):
    cursor = db.category.find({"is_active": True}).sort("name", 1)
    result = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        result.append(doc)
    return result

