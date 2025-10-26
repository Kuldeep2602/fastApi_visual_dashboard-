from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import jwt
import bcrypt
import pandas as pd
import io
import os
from pydantic import BaseModel, EmailStr

# Import database configuration
from database import (
    connect_to_mongodb,
    close_mongodb_connection,
    get_users_collection,
    get_datasets_collection,
    create_indexes
)

# Configuration
SECRET_KEY = "your-secret-key-change-in-production-12345678"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI
app = FastAPI(title="DataViz Pro API - MongoDB", version="2.0.0")

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup"""
    await connect_to_mongodb()
    await create_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    await close_mongodb_connection()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    email: EmailStr
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Helper Functions - Authentication
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from MongoDB
    users = get_users_collection()
    user = await users.find_one({"email": email})
    
    if not user:
        raise credentials_exception
    
    return {"email": user["email"], "role": user["role"]}

# Routes - Health Check
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "DataViz Pro API is running with MongoDB",
        "version": "2.0.0",
        "status": "healthy",
        "database": "MongoDB Atlas"
    }

# Routes - Authentication
@app.post("/auth/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    """Create a new user account"""
    users = get_users_collection()
    
    # Check if user already exists
    existing_user = await users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user document
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "email": user.email,
        "hashed_password": hashed_password,
        "role": user.role,
        "created_at": datetime.utcnow()
    }
    
    # Insert into MongoDB
    result = await users.insert_one(user_doc)
    
    return UserResponse(email=user.email, role=user.role)

@app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get JWT token"""
    users = get_users_collection()
    
    # Find user in MongoDB
    user = await users.find_one({"email": form_data.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        email=current_user["email"],
        role=current_user["role"]
    )

# Routes - Data Management
@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and parse CSV/Excel file"""
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV and Excel files are allowed."
        )
    
    # Read file content
    contents = await file.read()
    
    # Parse file with pandas
    try:
        if file_ext == '.csv':
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing file: {str(e)}"
        )
    
    # Convert DataFrame to dict (convert timestamps and other non-serializable types to strings)
    df = df.fillna('')  # Replace NaN with empty string
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
    
    data_dict = df.to_dict('records')
    
    # Create dataset document for MongoDB
    dataset_doc = {
        "filename": file.filename,
        "user_email": current_user["email"],
        "upload_date": datetime.utcnow(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": df.columns.tolist(),
        "file_size": len(contents),
        "data": data_dict
    }
    
    # Insert into MongoDB
    datasets = get_datasets_collection()
    result = await datasets.insert_one(dataset_doc)
    
    return {
        "message": "File uploaded successfully",
        "dataset_id": str(result.inserted_id),
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns)
    }

@app.get("/data/datasets")
async def get_datasets(current_user: dict = Depends(get_current_user)):
    """Get all datasets for current user"""
    datasets = get_datasets_collection()
    
    # Find all datasets for current user
    cursor = datasets.find(
        {"user_email": current_user["email"]},
        {"data": 0}  # Exclude the data field for performance
    ).sort("upload_date", -1)  # Sort by newest first
    
    user_datasets = []
    async for dataset in cursor:
        user_datasets.append({
            "id": str(dataset["_id"]),
            "filename": dataset["filename"],
            "upload_date": dataset["upload_date"].isoformat(),
            "row_count": dataset["row_count"],
            "column_count": dataset["column_count"],
            "file_size": dataset["file_size"]
        })
    
    return user_datasets

@app.get("/data/{dataset_id}")
async def get_dataset_data(
    dataset_id: str,
    page: int = 1,
    page_size: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get paginated dataset data"""
    datasets = get_datasets_collection()
    
    # Convert string ID to ObjectId
    try:
        obj_id = ObjectId(dataset_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dataset ID format"
        )
    
    # Find dataset
    dataset = await datasets.find_one({"_id": obj_id})
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Verify ownership
    if dataset["user_email"] != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this dataset"
        )
    
    # Paginate data
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_data = dataset["data"][start_idx:end_idx]
    
    return {
        "data": paginated_data,
        "total_rows": dataset["row_count"],
        "page": page,
        "page_size": page_size,
        "total_pages": (dataset["row_count"] + page_size - 1) // page_size
    }

@app.get("/data/{dataset_id}/metadata")
async def get_dataset_metadata(
    dataset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get dataset metadata without data"""
    datasets = get_datasets_collection()
    
    # Convert string ID to ObjectId
    try:
        obj_id = ObjectId(dataset_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dataset ID format"
        )
    
    # Find dataset (exclude data field)
    dataset = await datasets.find_one({"_id": obj_id}, {"data": 0})
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    if dataset["user_email"] != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this dataset"
        )
    
    return {
        "id": str(dataset["_id"]),
        "filename": dataset["filename"],
        "upload_date": dataset["upload_date"].isoformat(),
        "row_count": dataset["row_count"],
        "column_count": dataset["column_count"],
        "columns": dataset["columns"],
        "file_size": dataset["file_size"]
    }

@app.get("/data/{dataset_id}/summary")
async def get_dataset_summary(
    dataset_id: str,
    column: str,
    aggregation: str = "count",
    value_column: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get aggregated data for charts"""
    datasets = get_datasets_collection()
    
    # Convert string ID to ObjectId
    try:
        obj_id = ObjectId(dataset_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dataset ID format"
        )
    
    # Find dataset
    dataset = await datasets.find_one({"_id": obj_id})
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    if dataset["user_email"] != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this dataset"
        )
    
    # Convert to DataFrame for aggregation
    df = pd.DataFrame(dataset["data"])
    
    if column not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{column}' not found in dataset"
        )
    
    # Perform aggregation
    try:
        if aggregation == "count":
            # Count occurrences of each unique value
            result = df[column].value_counts().to_dict()
        else:
            # For sum, avg, min, max - need a value column
            if not value_column:
                # If no value column specified, try to find a numeric column
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if not numeric_cols:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No numeric columns found for aggregation"
                    )
                value_column = numeric_cols[0]
            
            if value_column not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Value column '{value_column}' not found in dataset"
                )
            
            # Group by column and aggregate value_column
            if aggregation == "sum":
                result = df.groupby(column)[value_column].sum().to_dict()
            elif aggregation == "average" or aggregation == "avg":
                result = df.groupby(column)[value_column].mean().to_dict()
            elif aggregation == "min":
                result = df.groupby(column)[value_column].min().to_dict()
            elif aggregation == "max":
                result = df.groupby(column)[value_column].max().to_dict()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid aggregation type"
                )
        
        # Convert to chart-friendly format
        chart_data = [
            {"name": str(k), "value": float(v) if isinstance(v, (int, float)) else v} 
            for k, v in result.items()
        ]
        
        return chart_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error performing aggregation: {str(e)}"
        )

@app.delete("/data/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a dataset"""
    datasets = get_datasets_collection()
    
    # Convert string ID to ObjectId
    try:
        obj_id = ObjectId(dataset_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dataset ID format"
        )
    
    # Find dataset first to verify ownership
    dataset = await datasets.find_one({"_id": obj_id})
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    if dataset["user_email"] != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this dataset"
        )
    
    # Delete from MongoDB
    await datasets.delete_one({"_id": obj_id})
    
    return {"message": "Dataset deleted successfully"}

# Run with: uvicorn main_mongodb:app --reload --port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
