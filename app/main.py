import os
import urllib
from dotenv import find_dotenv, load_dotenv

from fastapi import FastAPI, File, UploadFile, Response, Request, status
from fastapi.responses import RedirectResponse
import msal

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = FastAPI()


auth_code_flow = {}

@app.get("/login")
async def login(request: Request):
    global auth_code_flow
    
    auth_code_flow = msal.ConfidentialClientApplication(
        os.environ.get('azureStorageOpenapiClientID'),
        authority='https://login.microsoftonline.com/' + os.environ.get('azureStorageOpenapiTenantID') + '/',
        client_credential=os.environ.get('azureStorageOpenapiClientSecret'),
        token_cache=msal.SerializableTokenCache()
    ).initiate_auth_code_flow(
        [],
        redirect_uri=request.url_for("authorized")
    )
    print("auth_uri: " + auth_code_flow["auth_uri"])
    return RedirectResponse(auth_code_flow["auth_uri"], status_code=307)
    # or if we prefer a clickable link to kick off the process
    #return Response(content="<!DOCTYPE html><html><head><title>Login</title></head><body><a href=\"{0}\">click this to login</a></body></html>".format(auth_url.replace("&", "&amp;")), media_type="text/html; charset=UTF-8")

@app.post("/{directory:path}", status_code=status.HTTP_201_CREATED)
async def write_json(directory: str, response: Response, payload: UploadFile = File(...)):
    response.headers["Location"] = "TODO"
    return directory + "/" + payload.filename

@app.post("/authorized")
@app.get("/authorized")
async def authorized(request: Request):
    try:
        print(f"auth_code_flow: {type(auth_code_flow)}, query_params: {type(request.query_params._dict)}")
        result = msal.ConfidentialClientApplication(
            os.environ.get('azureStorageOpenapiClientID'),
            authority='https://login.microsoftonline.com/' + os.environ.get('azureStorageOpenapiTenantID') + '/',
            client_credential=os.environ.get('azureStorageOpenapiClientSecret'),
            token_cache=msal.SerializableTokenCache()
        ).acquire_token_by_auth_code_flow(
            auth_code_flow,
            request.query_params._dict
        )
        if "error" in result:
            return "error: " + result
        return result
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
