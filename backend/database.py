"""
MongoDB Database Configuration
This file handles all MongoDB connections and operations
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from urllib.parse import quote_plus
import os

# MongoDB credentials (URL encode special characters)
username = quote_plus("kuldeeprathore1637")
password = quote_plus("Kuldeep@123")

# MongoDB Connection String
MONGODB_URL = f"mongodb+srv://{username}:{password}@cluster0.fubjnog.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "dataviz_pro"

# Global client instance
client: Optional[AsyncIOMotorClient] = None

def get_database():
    """Get database instance"""
    return client[DATABASE_NAME]

async def connect_to_mongodb():
    """Create database connection"""
    global client
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        # Test the connection
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        print(f"📊 Database: {DATABASE_NAME}")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise e

async def close_mongodb_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("🔒 MongoDB connection closed")

# Collection helpers
def get_users_collection():
    """Get users collection"""
    db = get_database()
    return db.users

def get_datasets_collection():
    """Get datasets collection"""
    db = get_database()
    return db.datasets

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        users = get_users_collection()
        datasets = get_datasets_collection()
        
        # Users indexes
        await users.create_index("email", unique=True)
        await users.create_index("created_at")
        
        # Datasets indexes
        await datasets.create_index("user_email")
        await datasets.create_index("upload_date")
        await datasets.create_index([("user_email", 1), ("upload_date", -1)])
        
        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not create indexes: {e}")
