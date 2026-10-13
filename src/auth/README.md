OAuth is a standard that lets an application access a service on your behalf without receiving your password. Its main purpose is authorization: controlling what the application is allowed to do.
For example, suppose an application needs to read files from your Google Drive:
1. The application redirects you to Google.
2. You sign in directly with Google.
3. Google asks whether you allow the application to read your files.
4. After approval, the application receives an access token.
5. The application uses that token to call the Google Drive API.


Your password stays with Google.
The main terms are:
Term	Meaning
Client	The application requesting access
Authorization server	The system that grants access and issues tokens
Resource server	The API hosting the protected data
Access token	A credential the application presents when calling the API
Scope	The permissions requested, such as reading files
Refresh token	A credential that can obtain a new access token when the previous one expires


An API request commonly includes the token like this:
GET /api/files
Authorization: Bearer <access_token>

OAuth itself does not define user login or identity verification. OpenID Connect (OIDC) adds that identity layer on top of OAuth 2.0.
For your API work, there are two common situations:
- A business user uses your GUI: the application obtains access on behalf of that user.
- Your backend calls another service automatically: it can use the client credentials flow to obtain access as the application itself.
Compared with a PAT (Personal Access Token), OAuth provides a standardized process for obtaining and renewing tokens. A PAT is typically created manually and supplied directly to the application.