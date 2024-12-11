from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List
from datetime import datetime, timedelta
from model import UserModel, ProjectModel, ProjectOutModel
from mongoengine_models import User, Project
from mongoengine import connect

# Constants
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_SECRET_KEY = "your_secret_key"
MONGO_CONNECTION_STRING = "MongoDB_Connection_String"
MONGO_DB = "fastapi_rbac"

# Database Config (MongoEngine)
connect("fastapi_rbac", host=MONGO_CONNECTION_STRING)

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
async def lifespan(app: FastAPI):
    #  when app starts
    print("Application Started successfully.")
    yield
    # when app stops
    print("Application Stopped successfully.")

app = FastAPI(lifespan=lifespan)
# Routes
@app.post("/register", response_model=dict)
async def register(user: UserModel):
    existing_user = User.objects(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user.password = hash_password(user.password)
    user_obj = User(username=user.username, password=user.password, role=user.role)
    user_obj.save()
    return {"message": "User registered successfully"}

@app.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User.objects(username=form_data.username).first()
    if user and verify_password(form_data.password, user.password):
        token = create_access_token({"username": user.username, "role": user.role})
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/projects", response_model=List[ProjectOutModel], dependencies=[Depends(get_current_user)])
async def get_projects():
    projects = Project.objects.all()
    return [{"id": str(p.id), "name": p.name, "description": p.description} for p in projects]

@app.post("/projects", response_model=dict, dependencies=[Depends(role_required("admin"))])
async def create_project(project: ProjectModel):
    project_obj = Project(name=project.name, description=project.description)
    project_obj.save()
    return {"message": "Project created successfully", "id": str(project_obj.id)}

@app.put("/projects/{project_id}", response_model=dict, dependencies=[Depends(role_required("admin"))])
async def update_project(project_id: str, project: ProjectModel):
    project_obj = Project.objects(id=project_id).first()
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    project_obj.update(name=project.name, description=project.description)
    return {"message": "Project updated successfully"}

@app.delete("/projects/{project_id}", response_model=dict, dependencies=[Depends(role_required("admin"))])
async def delete_project(project_id: str):
    project_obj = Project.objects(id=project_id).first()
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    project_obj.delete()
    return {"message": "Project deleted successfully"}

@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "OK"}
