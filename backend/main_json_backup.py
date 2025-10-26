from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import pandas as pd
import io
import os
import json
from pydantic import BaseModel, EmailStr

# Configuration
SECRET_KEY = "your-secret-key-change-in-production-12345678"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# File paths for local storage
USERS_FILE = "users.json"
DATASETS_FILE = "datasets.json"

# Initialize storage files
def init_storage():
    """Initialize JSON storage files if they don't exist"""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(DATASETS_FILE):
        with open(DATASETS_FILE, 'w') as f:
            json.dump({}, f)

init_storage()

# Initialize FastAPI
app = FastAPI(title="DataViz Pro API", version="1.0.0")

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

# Helper Functions - Storage
def read_users():
    """Read users from JSON file"""
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def write_users(users):
    """Write users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def read_datasets():
    """Read datasets from JSON file"""
    with open(DATASETS_FILE, 'r') as f:
        return json.load(f)

def write_datasets(datasets):
    """Write datasets to JSON file"""
    with open(DATASETS_FILE, 'w') as f:
        json.dump(datasets, f, indent=2)

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
    
    users = read_users()
    if email not in users:
        raise credentials_exception
    
    user_data = users[email]
    return {"email": email, "role": user_data["role"]}

# Routes - Health Check
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "DataViz Pro API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

# Routes - Authentication
@app.post("/auth/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    """Create a new user account"""
    users = read_users()
    
    # Check if user already exists
    if user.email in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    users[user.email] = {
        "hashed_password": hashed_password,
        "role": user.role,
        "created_at": datetime.utcnow().isoformat()
    }
    
    write_users(users)
    
    return UserResponse(email=user.email, role=user.role)

@app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get JWT token"""
    users = read_users()
    
    # Check if user exists
    if form_data.username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = users[form_data.username]
    
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
        data={"sub": form_data.username}, 
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
    
    # Store in local file
    datasets = read_datasets()
    dataset_id = str(len(datasets) + 1)
    
    datasets[dataset_id] = {
        "filename": file.filename,
        "user_email": current_user["email"],
        "upload_date": datetime.utcnow().isoformat(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": df.columns.tolist(),
        "file_size": len(contents),
        "data": data_dict
    }
    
    write_datasets(datasets)
    
    return {
        "message": "File uploaded successfully",
        "dataset_id": dataset_id,
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns)
    }

@app.get("/data/datasets")
async def get_datasets(current_user: dict = Depends(get_current_user)):
    """Get all datasets for current user"""
    datasets = read_datasets()
    
    user_datasets = []
    for dataset_id, data in datasets.items():
        if data["user_email"] == current_user["email"]:
            user_datasets.append({
                "id": dataset_id,
                "filename": data["filename"],
                "upload_date": data["upload_date"],
                "row_count": data["row_count"],
                "column_count": data["column_count"],
                "file_size": data["file_size"]
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
    datasets = read_datasets()
    
    if dataset_id not in datasets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    dataset = datasets[dataset_id]
    
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
    datasets = read_datasets()
    
    if dataset_id not in datasets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    dataset = datasets[dataset_id]
    
    if dataset["user_email"] != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this dataset"
        )
    
    return {
        "id": dataset_id,
        "filename": dataset["filename"],
        "upload_date": dataset["upload_date"],
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
    datasets = read_datasets()
    
    if dataset_id not in datasets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    dataset = datasets[dataset_id]
    
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
    datasets = read_datasets()
    
    if dataset_id not in datasets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    dataset = datasets[dataset_id]
    
    if dataset["user_email"] != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this dataset"
        )
    
    # Delete from local storage
    del datasets[dataset_id]
    write_datasets(datasets)
    
    return {"message": "Dataset deleted successfully"}

# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
