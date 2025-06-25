# app/routers/_utils.py

# def fix_objectid(doc: dict) -> dict:
#     """
#     در صورت وجود فیلد "_id" از نوع ObjectId ، آن را به str تبدیل می‌کند.
#     """
#     if "_id" in doc and not isinstance(doc["_id"], str):
#         doc["_id"] = str(doc["_id"])
#     return doc

from bson import ObjectId


def fix_objectid(doc: dict) -> dict:
    if "_id" in doc and not isinstance(doc["_id"], str):
        doc["_id"] = str(doc["_id"])
    for field in ("category_id", "discount_id", "address_id"):
        if field in doc and isinstance(doc[field], ObjectId):
            doc[field] = str(doc[field])
        elif field not in doc:
            doc[field] = None
    return doc


# def fix_objectid(doc: dict) -> dict:
#     if "_id" in doc and not isinstance(doc["_id"], str):
#         doc["_id"] = str(doc["_id"])
#     for field in ["category_id", "discount_id"]:
#         if field in doc and isinstance(doc[field], ObjectId):
#             doc[field] = str(doc[field])
#         elif field not in doc:
#             doc[field] = None
#     return doc

