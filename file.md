


Login 
Client Request: The user initiates the login process by sending a request containing five key parameters: grant_type, username, password, scope, and crucially, the client-facing identifier, client_id.
Tenant Resolution (Master DB Lookup): The system uses the provided client_id to query the core MongoDB database to retrieve the corresponding internal tenant_id and tenant_name (or tenant_label).
Tenant Database Connection: Using the newly resolved tenant_id, the system connects to or selects the specific, isolated tenant database instance where the user's data resides.
User Verification (Tenant DB Query): The system executes a search within the tenant's user collection to find the user record:
Query: tenant_database.users.find_one({"username": form_data.username})
Password Verification: The function verify_password is called to compare the plain-text password submitted by the user against the secure password hash stored in the retrieved user record.
Token Creation (JWT Encoding): If the password verification succeeds, an access_token is generated using the JWT library:
              the_to _encode_payload = data={"sub": user["username"], "role": user["role"], "tenant_id": tenant_id}

Operation: jwt.encode(the_to_encode_payload, secret_key, and algorithm)
Success Response: The system returns a comprehensive JSON response to the client, providing the necessary credentials and identity information:

"id": The user's MongoDB unique identifier (user["_id"]).
"access_token": The newly generated JWT used for subsequent authenticated requests.
"token_type": Set to "bearer".
"username": The user's username.
"role": The user's role/permission level.
"tenant_id": The identifier of the tenant's isolated data space.
"tenant_label": The human-readable name of the tenant (result["name"]).
"tenant_slug": A URL-safe identifier for the tenant, often derived from the client_id (form_data.client_id)."



User Invitation Process Flow
This flow describes how a user (the inviter, or current_user) sends a new invitation to another user (the username).
Input Requirements: The process starts with two main inputs:
Invitation Data: The username and role for the person being invited.
Inviter Context: The current_user object, which provides the tenant_id and access to the tenant's database (current_user.db).

Check 1: User Existence (Prevent Duplicates):
The system first checks the user collection within the tenant's database (current_user.db.users).
IF the username already exists, the process stops and returns a "Username already exists" error.

Check 2: Pending Invitation Check (Prevent Spam):
If the user doesn't exist, the system checks the invitation collection (current_user.db.invitations).
IF an invitation for that username already exists:
The existing, old invitation record is deleted.
A new invitation process is started (proceed to Step 4).

Create Invitation Payload:
A new payload object (the_to_encode) is constructed with all necessary data for the new invitation token:
username
role
invited_by (the current_user's ID)
tenant_id
expired_date (a timestamp for when the invitation link expires)

Generate Invitation Token (JWT):
The system generates a new, secure invitation_token by encoding the payload (from Step 4) using the application's JWT secret key and algorithm:
Operation: JWT.encode(the_to_encode, secret_key, algorithm)

Store & Finalize:
The generated invitation_token (and often the raw payload data) is saved as a new record in the current_user.db.invitations collection.
The system then sends the invitation (e.g., an email containing the token link) to the invited user.


User Registration via Invitation Token
The register endpoint accepts four inputs: username, role, password, and the token itself.

Token Verification and Decoding:
The system first attempts to decode and verify the invitation_token using the secret key and algorithm: jwt.decode(token, Secret_key, algorithms).
If decoding is successful, the payload is extracted, providing the original data, including the temporary username, role, invited_by, and tenant_id.
Database Validation (Invitation Check):
Using the data extracted from the token (like the temporary username and tenant_id), the system queries the invitations collection.
Check 1: Validity: If no matching invitation record is found, the token is considered an invalid invitation token.
Check 2: Usage: If a record is found, the system checks if the invitation has already been used (e.g., if the field used: true). If so, the system returns a "Token has already been used" error.
Username Uniqueness Check:
The system performs a final check against the main users collection.
If the user-provided registration username already exists in the database, the process stops and returns a "Username already exists" error.
Password Hashing:
The user's plain-text registration password is securely hashed (using Argon2 or BCrypt) to create the hashed_password.
User Creation (Insertion):
A new document is created and inserted into the users collection of the tenant database. This record contains:
The final username
The hashed_password
The assigned role (from the token payload)
created_by (from the token's invited_by field)
created_at timestamp
Update Invitation Status:
Finally, the system updates the original invitation record in the invitations collection.
The status is changed to indicate usage, typically by setting a flag like used: true. This prevents the same token from being used again in the future.



