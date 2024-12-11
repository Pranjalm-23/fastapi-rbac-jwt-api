# FastAPI-Backend API with JWT Authentication and RBAC

This is a FastAPI Backend API implementing user authentication with JWT and Role-Based Access Control (RBAC). Users can register, log in, and access resources based on their roles (e.g., `admin` or `user`).

---

## **Features**

1. **User Registration and Login**
   - Register users with hashed passwords.
   - Log in to receive a JWT for authentication.

2. **Role-Based Access Control (RBAC)**
   - `admin` users can create, update, delete, and view resources.
   - `user` role can only view resources.

3. **CRUD Operations for Projects**
   - Perform operations like adding and viewing projects.

4. **MongoDB Support**
   - Store users and projects in MongoDB.

5. **JWT Authentication**
   - Authenticate and authorize API requests using JWT.

---

## **Endpoints**

0. **Health Check**
   - **GET** `/health`

1. **User Registration**
   - **POST** `/register`
   - Body: `{ "username": "example", "password": "password123", "role": "user" }`

2. **User Login**
   - **POST** `/login`
   - Body: `{ "username": "example", "password": "password123" }`
   - Response: `{ "access_token": "JWT_TOKEN" }`

3. **Get Projects**
   - **GET** `/projects`
   - Requires: JWT

4. **Create Project**
   - **POST** `/projects`
   - Body: `{ "name": "Project A", "description": "Description of project" }`
   - Requires: JWT with `admin` role.

5. **Update Project**
   - **PUT** `/projects/<project_id>`
   - Body: `{  "name": "Updated Project Name", "description": "Updated Project Description"}`
   - Requires: JWT with `admin` role.

6. **Delete Project**
   - **DELETE** `/projects/<project_id>`
   - Requires: JWT with `admin` role.

## **Setup Instructions**

### Prerequisites
1. Python 3.9+
2. MongoDB running locally or in the cloud.

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/Pranjalm-23/fastapi-rbac-jwt-api/
   cd fastapi-rbac-jwt-api
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Update the following constants in **`main.py`** (previously `app.py`):
   - `JWT_SECRET_KEY`: Add your JWT secret key.
   - `MONGO_URI`: Update with your MongoDB connection string.

   Example:
   ```python
   JWT_SECRET_KEY = "your_updated_secret_key"
   MONGO_CONNECTION_STRING = "your_mongo_connection_string"
   ```
4. Run the application using `Uvicorn`
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
5. Access the application in your browser or via an API client at:
   - [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Swagger and Redoc Documentation
#### To test your APIs and see their documentation when the app is running
- **Swagger UI:** Go to `http://127.0.0.1:8000/docs`.
- **Redoc UI:** Go to `http://127.0.0.1:8000/redoc`.