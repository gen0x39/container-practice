from fastapi import FastAPI, HTTPException
import json


app = FastAPI()


@app.get("/")
async def root():
    return "Hello World"

@app.get("/items")
async def get_items():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    with open('data.json', 'r') as f:
        data = json.load(f)
    for item in data:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
