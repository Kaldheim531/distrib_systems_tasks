from concurrent import futures
import logging

import grpc
from fastapi import FastAPI, HTTPException

from . import items_pb2, items_pb2_grpc

app = FastAPI()
logging.basicConfig(level=logging.INFO)

items = []
last_id = 0
grpc_server = None


def make_item(data: dict):
    global last_id

    last_id += 1
    item = {
        "id": last_id,
        "name": data.get("name", ""),
        "sku": data.get("sku", ""),
    }
    items.append(item)
    logging.info("item created: %s", item["id"])
    return item


def find_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def update_item_data(item_id: int, data: dict):
    item = find_item(item_id)
    if item is None:
        return None

    item["name"] = data.get("name", item["name"])
    item["sku"] = data.get("sku", item["sku"])
    logging.info("item updated: %s", item["id"])
    return item


def delete_item_data(item_id: int):
    item = find_item(item_id)
    if item is None:
        return False

    items.remove(item)
    logging.info("item deleted: %s", item_id)
    return True


def to_proto(item: dict):
    return items_pb2.Item(id=item["id"], name=item["name"], sku=item["sku"])


class ItemsGrpcService(items_pb2_grpc.ItemsServiceServicer):
    def CreateItem(self, request, context):
        item = make_item({"name": request.name, "sku": request.sku})
        return to_proto(item)

    def GetItem(self, request, context):
        item = find_item(request.id)
        if item is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "Item not found")
        return to_proto(item)

    def ListItems(self, request, context):
        return items_pb2.ListItemsResponse(items=[to_proto(item) for item in items])

    def UpdateItem(self, request, context):
        item = update_item_data(request.id, {"name": request.name, "sku": request.sku})
        if item is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "Item not found")
        return to_proto(item)

    def DeleteItem(self, request, context):
        ok = delete_item_data(request.id)
        if not ok:
            context.abort(grpc.StatusCode.NOT_FOUND, "Item not found")
        return items_pb2.DeleteItemResponse(ok=True)


@app.on_event("startup")
async def start_grpc():
    global grpc_server

    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    items_pb2_grpc.add_ItemsServiceServicer_to_server(ItemsGrpcService(), grpc_server)
    grpc_server.add_insecure_port("[::]:50051")
    grpc_server.start()


@app.on_event("shutdown")
async def stop_grpc():
    if grpc_server is not None:
        grpc_server.stop(0)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/items")
async def get_items():
    return items


@app.post("/items", status_code=201)
async def create_item(item: dict):
    return make_item(item)


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = find_item(item_id)
    if item is not None:
        return item

    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: dict):
    updated = update_item_data(item_id, item)
    if updated is not None:
        return updated

    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if delete_item_data(item_id):
        return {"ok": True}

    raise HTTPException(status_code=404, detail="Item not found")
