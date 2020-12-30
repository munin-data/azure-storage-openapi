This repo provides an OpenAPI-compliant endpoint capable of persisting TODO to Azure Storage.

# Running on the local host

## Install dependencies

```
pip install --user uvicorn
pip install --user fastapi
```

## Running on the local host

Run the API using the Uvicorn:

```
uvicorn app.main:app --reload
```

Navigate to the displayed address where Guvicorn is running, e.g. http://127.0.0.1:8000.

# Docker container

## Building

Build a Docker image by running the command:

```
docker build --tag munindata/azure-storage-openapi .
```

---
***NOTE:*** To debug the image build process, it is helpful to use the command:
```
docker build --progress plain --tag munindata/azure-storage-openapi .
```
---

## Running in a container on the local Docker host

Run a Docker container by using the command:

```
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

TODO

# Architecture

- Python 3.8.x.
- [Uvicorn ASGI server](https://www.uvicorn.org).
- [FastAPI web framework](https://fastapi.tiangolo.com/).

## Dependencies

- [Microsoft Authentication Library (MSAL) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python) [1.8.0](https://github.com/AzureAD/microsoft-authentication-library-for-python/releases/tag/1.8.0)

# TODO

- Support other archs than amd64 in Docker image
  - Requires FROM to be set to a Python base image rather than FastAPI
- Audit Docker image supply chain

# Relevant Links

- [GitHub: Azure-Samples/ms-identity-python-webapp](https://github.com/Azure-Samples/ms-identity-python-webapp) -- the main inspiration for this project
- [GitHub: Azure-Samples/ms-identity-python-flask-webapp-call-graph](https://github.com/Azure-Samples/ms-identity-python-flask-webapp-call-graph) -- an updated version of the `ms-identity-python-webapp` sample above, that makes use of the common lib below
  - [GitHub: Azure-Samples/ms-identity-python-samples-common](https://github.com/Azure-Samples/ms-identity-python-samples-common) -- adds Flask adapter (and potentially others by the time you are reading this) and `ms_identity_web` API (not used in this project)
- [FastAPI Documentation: Deploy with Docker](https://fastapi.tiangolo.com/deployment/docker/)
