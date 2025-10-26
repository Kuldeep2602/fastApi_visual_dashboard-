"""
Migration script to import data from JSON files to MongoDB
Run this once to migrate existing users and datasets
"""
import asyncio
import json
from datetime import datetime
from database import connect_to_mongodb, get_users_collection, get_datasets_collection, close_mongodb_connection

async def migrate_data():
    """Migrate users and datasets from JSON to MongoDB"""
    print("🚀 Starting data migration...")
    
    # Connect to MongoDB
    await connect_to_mongodb()
    
    users_collection = get_users_collection()
    datasets_collection = get_datasets_collection()
    
    # Migrate Users
    print("\n📝 Migrating users...")
    try:
        with open('users.json', 'r') as f:
            users_data = json.load(f)
        
        if users_data:
            migrated_users = 0
            for email, user_info in users_data.items():
                # Check if user already exists
                existing = await users_collection.find_one({"email": email})
                if existing:
                    print(f"   ⚠️  User {email} already exists, skipping...")
                    continue
                
                # Convert created_at to datetime
                created_at = datetime.fromisoformat(user_info['created_at']) if 'created_at' in user_info else datetime.utcnow()
                
                # Create user document
                user_doc = {
                    "email": email,
                    "hashed_password": user_info['hashed_password'],
                    "role": user_info.get('role', 'user'),
                    "created_at": created_at
                }
                
                await users_collection.insert_one(user_doc)
                migrated_users += 1
                print(f"   ✅ Migrated user: {email}")
            
            print(f"\n✨ Successfully migrated {migrated_users} user(s)")
        else:
            print("   ℹ️  No users to migrate")
    except FileNotFoundError:
        print("   ⚠️  users.json not found")
    except Exception as e:
        print(f"   ❌ Error migrating users: {e}")
    
    # Migrate Datasets
    print("\n📊 Migrating datasets...")
    try:
        with open('datasets.json', 'r') as f:
            datasets_data = json.load(f)
        
        if datasets_data:
            migrated_datasets = 0
            for dataset_id, dataset_info in datasets_data.items():
                # Check if dataset already exists (by filename and user_email)
                existing = await datasets_collection.find_one({
                    "filename": dataset_info['filename'],
                    "user_email": dataset_info['user_email']
                })
                if existing:
                    print(f"   ⚠️  Dataset {dataset_info['filename']} already exists, skipping...")
                    continue
                
                # Convert upload_date to datetime
                upload_date = datetime.fromisoformat(dataset_info['upload_date']) if 'upload_date' in dataset_info else datetime.utcnow()
                
                # Create dataset document
                dataset_doc = {
                    "filename": dataset_info['filename'],
                    "user_email": dataset_info['user_email'],
                    "upload_date": upload_date,
                    "row_count": dataset_info['row_count'],
                    "column_count": dataset_info['column_count'],
                    "columns": dataset_info['columns'],
                    "file_size": dataset_info['file_size'],
                    "data": dataset_info['data']
                }
                
                result = await datasets_collection.insert_one(dataset_doc)
                migrated_datasets += 1
                print(f"   ✅ Migrated dataset: {dataset_info['filename']} (ID: {result.inserted_id})")
            
            print(f"\n✨ Successfully migrated {migrated_datasets} dataset(s)")
        else:
            print("   ℹ️  No datasets to migrate")
    except FileNotFoundError:
        print("   ⚠️  datasets.json not found")
    except Exception as e:
        print(f"   ❌ Error migrating datasets: {e}")
    
    # Close connection
    await close_mongodb_connection()
    
    print("\n🎉 Migration completed!")
    print("\n📌 Next steps:")
    print("   1. Test the MongoDB API at http://localhost:8001")
    print("   2. Update frontend API URL to http://localhost:8001")
    print("   3. Switch to MongoDB version permanently")

if __name__ == "__main__":
    asyncio.run(migrate_data())
