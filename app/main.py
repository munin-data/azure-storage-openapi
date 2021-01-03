from fastapi import FastAPI, File, UploadFile, Response, status

app = FastAPI()


@app.post("/{directory:path}", status_code=status.HTTP_201_CREATED)
async def write_json(directory: str, response: Response, payload: UploadFile = File(...)):
    response.headers["Location"] = "TODO"
    return directory + "/" + payload.filename
