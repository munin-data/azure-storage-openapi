import os
import urllib
from dotenv import find_dotenv, load_dotenv
import datetime

from fastapi import FastAPI, File, UploadFile, Response, Request, status
from fastapi.responses import RedirectResponse

import msal
from azure.core.credentials import AccessToken
from azure.storage.filedatalake import DataLakeFileClient

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = FastAPI()

auth_code_flow = {}
confidential_client_app = msal.ConfidentialClientApplication(
    os.environ.get('azureStorageOpenapiClientID'),
    authority='https://login.microsoftonline.com/' + os.environ.get('azureStorageOpenapiTenantID') + '/',
    client_credential=os.environ.get('azureStorageOpenapiClientSecret'),
    token_cache=msal.SerializableTokenCache()
)


class MyCredential(object):
    def __init__(self, token: str, expires_on: int):
        self.token = token
        self.expires_on = expires_on

    def get_token(self, *scopes, **kwargs):
        return AccessToken(self.token, self.expires_on)

@app.get("/login")
async def login(request: Request):
    global auth_code_flow

    auth_code_flow = confidential_client_app.initiate_auth_code_flow(
        ["https://storage.azure.com/user_impersonation"],
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

@app.get("/authorized")
async def authorized(request: Request):
    try:
        result = confidential_client_app.acquire_token_by_auth_code_flow(
            auth_code_flow,
            request.query_params._dict
        )
        file = DataLakeFileClient(
            account_url='https://storageaccount.dfs.core.windows.net',
            file_system_name='storagecontainer',
            file_path='directory/file.txt',
            credential=MyCredential(
                token=result['access_token'],
                expires_on=int(result['expires_in'] + datetime.datetime.now().timestamp()) # probably not quite right
            )
        )
        print(file.download_file().readall())
        if "error" in result:
            return "error: " + result
        return result
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
