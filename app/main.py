from fastapi import FastAPI, Response, status

app = FastAPI()


@app.post("/{directory:path}", status_code=status.HTTP_201_CREATED)
async def write_json(directory: str, response: Response):
    response.headers["Location"] = "TODO"
    return directory
