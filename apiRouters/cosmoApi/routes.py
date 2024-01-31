from fastapi import APIRouter
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from apiRouters.cosmoApi.config import db
from datetime import datetime
cosmo=APIRouter()


class Item(BaseModel):
    id: str
    boughtQuantity: int
    totalAmount: int

class UserAddress(BaseModel):
    city: str
    country: str
    zipCode: str

class Order(BaseModel):
    items: List[Item]
    userAddress: UserAddress


@cosmo.get("/products/")
async def get_products(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_price: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None, ge=0)
):
    collection = db["products"]
    # Query filters
    filters = {}
    if min_price is not None:
        print(min_price)
        filters["productPrice"] = {"$gte": min_price}
    if max_price is not None:
        filters.setdefault("productPrice", {}).update({"$lte": max_price})
        

    # Count total number of records
    total = collection.count_documents(filters)

    # Fetch products with pagination and filters
    products_cursor = collection.find(filters).skip(offset).limit(limit)
    products = [
        {
            "id": str(product["_id"]),
            "productName": product["productName"],
            "productPrice": product["productPrice"],
            "productQuantity": product["productQuantity"]
        }
        for product in products_cursor
    ]

    # Calculate next and previous offsets
    next_offset = None
    prev_offset = None
    if offset + limit < total:
        next_offset = offset + limit
    if offset - limit >= 0:
        prev_offset = max(0, offset - limit)

    # Response metadata
    metadata = {
        "limit": limit,
        "nextOffset": next_offset,
        "prevOffset": prev_offset,
        "total": total
    }
    # print(products)
    return {"data": products, "page": metadata}


@cosmo.post("/orders/")
async def create_order(order: Order):
    # print(order)
    # Generate createdOn timestamp
    created_on = datetime.utcnow()

    # Prepare order data
    #order_data = {
    #     "createdOn": created_on,
    #     "items": order.items,
    #     "userAddress": order.userAddress.dict()
    # }
    order_data = {
        "createdOn": created_on,
        "items": [item.dict() for item in order.items],  # Convert items to dictionaries
        "userAddress": order.userAddress.dict()
    }
    print(order_data)
    # Insert order into MongoDB
    collection = db["orderList"]
    result = collection.insert_one(order_data)

    # Check if insertion was successful
    if result.inserted_id:
        return {"message": "Order created successfully", "order_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create order")



