This project provides a web API capable of persisting and extracting data in accordance with [OpenAPI standards](https://swagger.io/resources/open-api/) to and from [Azure Data Lake Storage Gen2 (ADLSv2)](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction) governed by [Access control lists (ACLs)](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control-model#access-control-lists-acls) by impersonating users' identities.

# Running on the local host

## Install newest versions of dependencies

```
pip install --upgrade --user python-dotenv python-multipart uvicorn fastapi msal azure-storage-file-datalake --pre
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
The following steps are necessary to provision this application in the Microsoft Identity Platform.

## Using the Azure Portal

1. Navigate to [App registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade) and click **New registration**.
2. Type in a descriptive name for the application, e.g. `azure-storage-openapi`.
3. Leave the radiobox on **Accounts in this organizational directory only (x.xyz only - Single tenant)**
4. For the **Redirect URI (optional)**, enter `http://localhost:8000/authorized` or similar as appropriate so that when MIP redirects the user's request, it targets the running instance of this web application.
5. Click the **Register** button.
6. Take note of the created **Application (client) ID**.
7. Navigate to **Certificates & secrets** pane.
8. Click **New client secret**.
9. Type a description, e.g. `azure-storage-openapi Client Secret`.
10. Click **Add**.
11. Take note of the secret value. It will not be retrievable from the Azure Portal in the future.
12. Navigate to the **API permissions** pane.
13. Click **Add a permission**.
14. Select **Azure Storage**.
15. Check **user_impersonation**.
16. Click **Add permissions**.
17. Click **Grant admin consent for x.xyz**, and click **Yes**.

# Provisioning and configuring ADLSv2

## Provisioning a storage account and container

### Using the Azure Portal

Navigate to [Storage accounts](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) and click **Add**. Provision the storage account with parameters as appropriate, being certain to enable the Hierarchical Namespace (HNS) feature by choosing **Enabled** on the **Data Lake Storage Gen2 - Hierarchical namespace ** parameter under **Advanced**. Note that it is only possible to enable HNS if one of the following combinations of settings are selected:

| Account kind     | Performance   | Description                                                        |
| ---------------- |:-------------:| ------------------------------------------------------------------ |
| StorageV2        | Standard      | provides access to blobs, files, queues, tables, and disks         |
| BlockBlobStorage | Premium       | high transaction rates and single-digit consistent storage latency |
| BlobStorage      | Standard      | optimized for high capacity and high throughput                    |

Once the storage account is created, you will also need to make a storage container (often referred to as a 'file system' in HNS parlance) underneathe the storage account.

## Creating the Access Control Entries (ACEs) to Authorize a Security Principal

A security principal (SP) is an object that represents a user, group, service principal, or managed identity that is requesting access to Azure resources. There are two ways to authorize a SP to access a given blob. One way is by creating a [role assignment in Azure](https://docs.microsoft.com/en-us/azure/role-based-access-control/overview#role-assignments), typically either [`Storage Blob Data Owner`](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-owner), [`Storage Blob Data Contributor`](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor), or [`Storage Blob Data Reader`](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-reader). The other option is by using ACLs comprised of several ACEs to authorize a given SP. Both methods are supported by this project, though only instructions for the latter are given here. See the [Access control lists (ACLs) in Azure Data Lake Storage Gen2](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control) for details on how this mechanism works.

---
***NOTE:*** It is not possible to change the ACLs on the container (i.e. at the root of the filesystem) using the Azure Portal at this time. However, blobs and folders underneathe the root can have their permissions managed in the web-based Storage Explorer (preview) in the Azure portal.
---

Depending on the managing SP's inherited role assignment on the account, it will often be necessary to make an additional role assignment, such as `Storage Blob Data Owner`, on the target storage container or a higher scope to enable the SP to create the below ACEs. The role assignment may take some minutes to propagate after it is made.

It may also be relevant to adjust the [umask](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control#umask), though this is not documented here. Similarly, the below steps are for a user principal; how to carry out these steps for other SPs is left as an exercise for the reader.

### [Using the Azure CLI](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-directory-file-acl-cli#manage-access-control-lists-acls)

1. Login in to Azure via the Azure CLI with an account having permissions to assign ACLs on the Storage Account in question.

```sh
az login
```

2. Allow the intended SP to read, write, and traverse from the root of the filesystem, and make these permissions apply to newly created blobs and folders under the root (as the default ACL), e.g.:

```sh
az storage fs access set --acl user:bob@contoso.com:r-x -p / -f storagecontainer --account-name storageaccount --auth-mode login
az storage fs access set --acl default:user:bob@contoso.com:rwx -p / -f storagecontainer --account-name storageaccount --auth-mode login

```

where `bob@contoso.com` is the user principal name (UPN) to be authorized to the `storagecontainer` container in the `storageaccount` storage account. Now, any newly created folders and files will adhere to the assigned permissions.

### [Using PowerShell](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-directory-file-acl-powershell#manage-access-control-lists-acls)

1. With elevated privileges (e.g. as local Administrator), install the [Storage service data plane and management cmdlets for Azure Resource Manager](https://www.powershellgallery.com/packages/Az.Storage).

```PowerShell
Install-Module Az.Storage
```

2. In another PowerShell session, login in to Azure and allow the intended SP to read, write, and traverse from the root of the filesystem, and make these permissions apply to newly created blobs and folders under the root (as the default ACL), e.g.:

```PowerShell
Import-Module Az.Storage
Connect-AzAccount
$ctx = New-AzStorageContext -StorageAccountName 'storageaccount' -UseConnectedAccount
$rootFolder = Get-AzDataLakeGen2Item -Context $ctx -FileSystem 'storagecontainer'
$rootFolderACL = $rootFolder.ACL
$rootFolderACL = Set-AzDataLakeGen2ItemAclObject -AccessControlType User -EntityId xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx -Permission r-x -InputObject $rootFolderACL
$rootFolderACL = Set-AzDataLakeGen2ItemAclObject -AccessControlType User -EntityId xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx -Permission rwx -DefaultScope -InputObject $rootFolderACL
Update-AzDataLakeGen2Item -Context $ctx -FileSystem 'storagecontainer' -Acl $rootFolderACL
```

where `xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` is the object ID of the user to be authorized to the `storagecontainer` container in the `storageaccount` storage account. Now, any newly created folders and files will adhere to the assigned permissions.

# Architecture

- Python 3.x
- [Uvicorn ASGI server](https://www.uvicorn.org)
- [FastAPI web framework](https://fastapi.tiangolo.com/)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-overview) interfaced via [Microsoft Authentication Libraries (MSAL)](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview)
- [Azure Data Lake Storage Gen2](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)

# TODO

- Add user session support for security + multitenancy and to avoid global state
  - see [GitHub: tiangolo/fastapi: First-class session support in FastAPI](https://github.com/tiangolo/fastapi/issues/754#issuecomment-585386650)
- Make use of the token cache
- Make use of depends statements or middleware to cause APIs to require login
- Drop or mask logging statements and responses exposing sensitive information
- Use requirements.txt file instead of explicit pip command
- Don't throw NameError in case of undefined configuration
- Document more ways of registering the application in MIP
- Support other archs than amd64 in Docker image
  - Requires FROM to be set to a Python base image rather than FastAPI
- Audit Docker image supply chain
- Consider [allowing multiple files to be uploaded](https://fastapi.tiangolo.com/tutorial/request-files/#multiple-file-uploads) to root POST path operation
- Consider allowing application/octet-stream content type directly in request as opposed to as individual part(s) of the multipart/form-data
  - Alternative: consider application/x-www-form-urlencoded
- Consider adding support for the [Device authorization grant flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code)
- Consider adding support for the [On-Behalf-Of flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow)
  - That is, allow this project's web API to also require authorization
  - At present, this makes little sense, as this project only brokers data and doesn't contain any protected resources that users wouldn't already be able to access via Azure Storage directly
  - However, one could view the operational load on this application as a protected resource, or there may be other policy reasons or best practices in place that make first-class support for the OBO flow worthwhile
- Add instructions for application (client) identity with a certificate

# Relevant Links

## Libraries & Code Samples

- [GitHub: Microsoft Authentication Library (MSAL) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python)
  - [MSAL Python’s documentation](https://msal-python.readthedocs.io/en/latest/)
  - [Azure SDK for Python documentation: MSAL package](https://docs.microsoft.com/en-us/python/api/msal/msal?view=azure-python)
- [GitHub: Azure-Samples/ms-identity-python-webapp](https://github.com/Azure-Samples/ms-identity-python-webapp) -- the main inspiration for this project
- [GitHub: Azure-Samples/ms-identity-python-flask-webapp-call-graph](https://github.com/Azure-Samples/ms-identity-python-flask-webapp-call-graph) -- an updated version of the `ms-identity-python-webapp` sample above, that makes use of the common lib below
  - [GitHub: Azure-Samples/ms-identity-python-samples-common](https://github.com/Azure-Samples/ms-identity-python-samples-common) -- adds Flask adapter (and potentially others by the time you are reading this) and `ms_identity_web` API (not used in this project)
- [FastAPI documentation: Deploy with Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Azure DataLake service client library for Python](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-file-datalake/latest/index.html)
- [Azure Identity client library for Python](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity/latest/azure.identity.html)
- [GitHub: Azure/azure-sdk-for-python Issue #13834: PKCE Support with AuthorizationCodeCredential](https://github.com/Azure/azure-sdk-for-python/issues/13834) -- discusses approach used in this project to provide credential from MSAL authorization code grant with PKCE flow to Azure SDK for Python

## Azure

- [Azure Blob storage documentation: Access control model in Azure Data Lake Storage Gen2](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control-model)
- [Azure Blob storage documentation: Authorize access to blobs and queues using Azure Active Directory](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth-aad)
- [Azure Blob storage documentation: Acquire a token from Azure AD for authorizing requests from a client application](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth-aad-app) -- this requires role assignment for an entire storage container at its most granular; doesn't authorize individual blobs or folders
- [Azure Data Lake Storage (Gen2): Exploring AAD B2B & ACL hardening](https://kvaes.wordpress.com/2019/02/06/azure-data-lake-storage-gen2-exploring-aad-b2b-acl-hardening/)

## OAuth 2.0 Authorization Code Flow

- [Microsoft identity platform documentation: Microsoft identity platform and OAuth 2.0 authorization code flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Auth0 Docs: Authorization Code Flow with Proof Key for Code Exchange (PKCE)](https://auth0.com/docs/flows/authorization-code-flow-with-proof-key-for-code-exchange-pkce)
- [Auth0 Docs: Call Your API Using the Authorization Code Flow with PKCE](https://auth0.com/docs/flows/call-your-api-using-the-authorization-code-flow-with-pkce)
- [NHS Digital: The Authorization Code Flow in Detail](https://rograce.github.io/openid-connect-documentation/explore_auth_code_flow)
- [Okta: Implement the OAuth 2.0 Authorization Code with PKCE Flow](https://developer.okta.com/blog/2019/08/22/okta-authjs-pkce)
- [RFC7636: Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)
- [RFC8628: OAuth 2.0 Device Authorization Grant](https://tools.ietf.org/html/rfc8628)
