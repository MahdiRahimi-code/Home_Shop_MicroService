# app/routers/addresses.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.schemas import AddressIn, AddressOut
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
async def add_address(addr: AddressIn, db=Depends(get_db), user=Depends(CurrentUser)):
    doc = addr.model_dump()
    doc["user_id"] = user["id"]
    res = await db.addresses.insert_one(doc)
    doc["_id"] = res.inserted_id
    if addr.is_default:
        await db.addresses.update_many(
            {"user_id": user["id"], "_id": {"$ne": res.inserted_id}},
            {"$set": {"is_default": False}}
        )
    return fix_objectid(doc)


@router.get("/", response_model=list[AddressOut])
async def visit_addresses(db=Depends(get_db), user=Depends(CurrentUser)):
    docs = [fix_objectid(doc) async for doc in db.addresses.find({"user_id": user["id"]})]
    return docs


@router.put("/{address_id}", response_model=AddressOut)
async def edit_address(address_id: str, addr: AddressIn, db=Depends(get_db), user=Depends(CurrentUser)):
    result = await db.addresses.find_one_and_update(
        {"_id": ObjectId(address_id), "user_id": user["id"]},
        {"$set": addr.model_dump()},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if addr.is_default:
        await db.addresses.update_many(
            {"user_id": user["id"], "_id": {"$ne": result["_id"]}},
            {"$set": {"is_default": False}}
        )
    return fix_objectid(result)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(address_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
    res = await db.addresses.delete_one({"_id": ObjectId(address_id), "user_id": user["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")





# from fastapi import APIRouter, Depends, HTTPException, status
# from bson import ObjectId
# from app.schemas import AddressIn, AddressOut
# from app.deps import get_db, CurrentUser

# router = APIRouter(prefix="/addresses", tags=["addresses"])

# def fix_objectid(doc):
#     doc["_id"] = str(doc["_id"])
#     return doc

# @router.post("/", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
# async def add_address(addr: AddressIn, db=Depends(get_db), user=Depends(CurrentUser)):
#     doc = addr.model_dump()
#     doc["user_id"] = user["id"]
#     res = await db.addresses.insert_one(doc)
#     doc["_id"] = res.inserted_id
#     if addr.is_default:
#         await db.addresses.update_many(
#             {"user_id": user["id"], "_id": {"$ne": res.inserted_id}},
#             {"$set": {"is_default": False}}
#         )
#     return fix_objectid(doc)

# @router.get("/", response_model=list[AddressOut])
# async def visit_addresses(db=Depends(get_db), user=Depends(CurrentUser)):
#     return [fix_objectid(doc) async for doc in db.addresses.find({"user_id": user["id"]})]

# @router.put("/{address_id}", response_model=AddressOut)
# async def edit_address(address_id: str, addr: AddressIn, db=Depends(get_db), user=Depends(CurrentUser)):
#     result = await db.addresses.find_one_and_update(
#         {"_id": ObjectId(address_id), "user_id": user["id"]},
#         {"$set": addr.model_dump()},
#         return_document=True
#     )
#     if not result:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
#     if addr.is_default:
#         await db.addresses.update_many(
#             {"user_id": user["id"], "_id": {"$ne": result["_id"]}},
#             {"$set": {"is_default": False}}
#         )
#     return fix_objectid(result)

# @router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_address(address_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
#     res = await db.addresses.delete_one({"_id": ObjectId(address_id), "user_id": user["id"]})
#     if res.deleted_count == 0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
