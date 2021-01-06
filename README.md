This repo provides an OpenAPI-compliant endpoint capable of persisting TODO to Azure Storage.

# Running on the local host

## Install newest versions of dependencies

```
pip install --upgrade --user python-dotenv python-multipart uvicorn fastapi msal
```

## Running on the local host

Configure the Azure tenant ID, registered application (client) ID, and secret as environment variables:

```sh
export azureStorageOpenapiTenantID='00000000-0000-0000-0000-000000000000'
export azureStorageOpenapiClientID='00000000-0000-0000-0000-000000000000'
export azureStorageOpenapiClientSecret='0000000000000000000000000000000000'
```

or, alternatively, create a [`.env` file](https://pypi.org/project/python-dotenv/) to provide the configuration:

```sh
azureStorageOpenapiTenantID=00000000-0000-0000-0000-000000000000
azureStorageOpenapiClientID=00000000-0000-0000-0000-000000000000
azureStorageOpenapiClientSecret=0000000000000000000000000000000000
```

Run the API using the Uvicorn:

```sh
uvicorn app.main:app --reload
```

Navigate to the displayed address where Guvicorn is running, e.g. http://127.0.0.1:8000.

# Docker container

## Building

Build a Docker image by running the command:

```sh
docker build --tag munindata/azure-storage-openapi .
```

---
***NOTE:*** To debug the image build process, it is helpful to use the command:
```sh
docker build --progress plain --tag munindata/azure-storage-openapi .
```
---

## Running in a container on the local Docker host

Run a Docker container by using the command:

```sh
docker run --detach --rm --publish 80:80 munindata/azure-storage-openapi
```

You can then connect to the running web API at http://127.0.0.1.

---
***NOTE:*** The application's endpoint may also be available at other network locations such as http://172.17.0.2 or http://192.168.99.100 depending on your Docker network configuration. Use `docker network ls` and `docker network inspect` to find other likely candidate addresses.

---

# Viewing API documentation and schema

## OpenAPI 3.0 schema

You may find the OpenAPI API and data schema for both requests and responses by appending `/openapi.json` to the base address, e.g. http://127.0.0.1:8000/openapi.json when running on the local host.

## [Swagger UI](https://github.com/swagger-api/swagger-ui)

You may find Swagger UI's view on the schema by appending `/docs` to the base address, e.g. http://127.0.0.1:8000/docs when running on the local host.

## [ReDoc](https://github.com/Rebilly/ReDoc)

To see ReDoc's view of the OpenAPI 3.0 documentation and schema, append `/redoc` to the address, e.g. http://127.0.0.1:8000/redoc when running on the local host.

# Deploying to Azure

Deploy to TODO by TODO

# Provisioning in MIP
The following steps are necessary to provision the application in the Microsoft Identity Platform.

## Using the Azure Portal

1. Navigate to [App registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade) and click *New registration*.
2. Type in a descriptive name for the application, e.g. `azure-storage-openapi`.
3. Leave the radiobox on *Accounts in this organizational directory only (x.xyz only - Single tenant)*
4. For the *Redirect URI (optional)*, enter `http://localhost:8000/authorized` or similar as appropriate so that when MIP redirects the user's request, it targets the running instance of this web application.
5. Click the *Register* button.
6. Take note of the created *Application (client) ID*.
7. Navigate to *Certificates & secrets* pane.
8. Click *New client secret*.
9. Type a description, e.g. `azure-storage-openapi Client Secret`.
10. Click *Add*.
11. Take note of the secret value. It will not be retrievable from the Azure Portal in the future.
12. Navigate to the *API permissions* pane.
13. Click *Add a permission*.
14. Select *Azure Storage*.
15. Check *user_impersonation*.
16. Click *Add permissions*.
17. Click *Grant admin consent for x.xyz*, and click *Yes*.

# Architecture

- Python 3.8.x
- [Uvicorn ASGI server](https://www.uvicorn.org)
- [FastAPI web framework](https://fastapi.tiangolo.com/)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-overview) interfaced via [Microsoft Authentication Libraries (MSAL)](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview)
- [Azure Data Lake Storage Gen2](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)

# TODO

- Refactor out duplicated code (e.g. `msal.ConfidentialClientApplication`) in favor of `_build` pattern or similar
- Add user session support for security + multitenancy and to avoid global state
  - see [GitHub: tiangolo/fastapi: First-class session support in FastAPI](https://github.com/tiangolo/fastapi/issues/754#issuecomment-585386650)
- Make use of the token cache
- (Probably) Target correct scope
- Drop or mask logging statements exposing sensitive information
- Use requirements.txt file instead of explicit pip command
- Don't throw NameError in case of undefined configuration
- Document more ways of registering the application in MIP
- Support other archs than amd64 in Docker image
  - Requires FROM to be set to a Python base image rather than FastAPI
- Audit Docker image supply chain
- Consider [allowing multiple files to be uploaded](https://fastapi.tiangolo.com/tutorial/request-files/#multiple-file-uploads) to root POST path operation
- Consider allowing application/octet-stream content type directly in request as opposed to as individual part(s) of the multipart/form-data
  - Alternative: consider application/x-www-form-urlencoded
- Add instructions for application (client) identity with a certificate

# Relevant Links

- [GitHub: Azure-Samples/ms-identity-python-webapp](https://github.com/Azure-Samples/ms-identity-python-webapp) -- the main inspiration for this project
- [GitHub: Azure-Samples/ms-identity-python-flask-webapp-call-graph](https://github.com/Azure-Samples/ms-identity-python-flask-webapp-call-graph) -- an updated version of the `ms-identity-python-webapp` sample above, that makes use of the common lib below
  - [GitHub: Azure-Samples/ms-identity-python-samples-common](https://github.com/Azure-Samples/ms-identity-python-samples-common) -- adds Flask adapter (and potentially others by the time you are reading this) and `ms_identity_web` API (not used in this project)
- [GitHub: Microsoft Authentication Library (MSAL) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python)
  - [MSAL Python’s documentation](https://msal-python.readthedocs.io/en/latest/)
  - [Azure SDK for Python documentation: MSAL package](https://docs.microsoft.com/en-us/python/api/msal/msal?view=azure-python)
- [FastAPI documentation: Deploy with Docker](https://fastapi.tiangolo.com/deployment/docker/)

## Azure

- [Azure Blob storage documentation: Acquire a token from Azure AD for authorizing requests from a client application](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth-aad-app) -- this requires role assignment for an entire storage container at its most granular; doesn't authorize individual blobs or folders
- [Azure Data Lake Storage (Gen2): Exploring AAD B2B & ACL hardening](https://kvaes.wordpress.com/2019/02/06/azure-data-lake-storage-gen2-exploring-aad-b2b-acl-hardening/)

## OAuth 2.0 Authorization Code Flow

- [Microsoft identity platform documentation: Microsoft identity platform and OAuth 2.0 authorization code flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Auth0 Docs: Authorization Code Flow](https://auth0.com/docs/flows/authorization-code-flow)
- [Auth0 Docs: Call Your API Using the Authorization Code Flow](https://auth0.com/docs/flows/call-your-api-using-the-authorization-code-flow)
- [NHS Digital: The Authorization Code Flow in Detail](https://rograce.github.io/openid-connect-documentation/explore_auth_code_flow)
