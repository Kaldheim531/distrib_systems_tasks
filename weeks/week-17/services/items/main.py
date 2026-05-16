import logging

from fastapi import FastAPI, HTTPException

app = FastAPI()
logging.basicConfig(level=logging.INFO)

items = []
last_id = 0


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/items")
def get_items():
    return items


@app.post("/items", status_code=201)
def create_item(item: dict):
    global last_id

    last_id += 1
    new_item = {
        "id": last_id,
        "name": item.get("name", ""),
        "sku": item.get("sku", ""),
    }
    items.append(new_item)
    logging.info("item created: %s", new_item["id"])
    return new_item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item

    raise HTTPException(status_code=404, detail="Item not found")
