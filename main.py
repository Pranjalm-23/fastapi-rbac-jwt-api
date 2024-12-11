from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List
from datetime import datetime, timedelta
from model import UserModel, ProjectModel, ProjectOutModel

# Constants
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_SECRET_KEY = "your_secret_key"
MONGO_CONNECTION_STRING = 'mongodb://sdfghjke&replicaSet=globaldb&maxIdleTimeMS=120000'
MONGO_DB = "fastapi_rbac"

# Database Config
MONGO_URI = MONGO_CONNECTION_STRING
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Token Functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("username")
        role: str = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=403, detail="Invalid token")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

def role_required(required_role: str):
    async def dependency(user: dict = Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return dependency

# FastAPI App
app = FastAPI()

@app.on_event("startup")
async def startup():
    print("Connected to MongoDB successfully.")

@app.on_event("shutdown")
async def shutdown():
    client.close()

# Routes
@app.post("/register", response_model=dict)
async def register(user: UserModel):
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user.password = hash_password(user.password)
    await db.users.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"username": form_data.username})
    if user and verify_password(form_data.password, user["password"]):
        token = create_access_token({"username": user["username"], "role": user["role"]})
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/projects", response_model=List[ProjectOutModel], dependencies=[Depends(get_current_user)])
async def get_projects():
    projects = await db.projects.find().to_list(100)
    return [{"id": str(p["_id"]), "name": p["name"], "description": p["description"]} for p in projects]

@app.post("/projects", response_model=dict, dependencies=[Depends(role_required("admin"))])
async def create_project(project: ProjectModel):
    result = await db.projects.insert_one(project.dict())
    return {"message": "Project created successfully", "id": str(result.inserted_id)}

@app.put("/projects/{project_id}", response_model=dict, dependencies=[Depends(role_required("admin"))])
async def update_project(project_id: str, project: ProjectModel):
    project_obj = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.projects.update_one({"_id": ObjectId(project_id)}, {"$set": project.dict()})
    return {"message": "Project updated successfully"}

@app.delete("/projects/{project_id}", response_model=dict, dependencies=[Depends(role_required("admin"))])
async def delete_project(project_id: str):
    project_obj = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.projects.delete_one({"_id": ObjectId(project_id)})
    return {"message": "Project deleted successfully"}

@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "OK"}
