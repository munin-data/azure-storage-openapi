from typing import Optional

from fastapi import FastAPI, Response, status

app = FastAPI()


@app.post("/{directory:path}", status_code=status.HTTP_201_CREATED)
async def write_json(directory: str, response: Response):
    response.headers["Location"] = "TODO"
    return directory

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

