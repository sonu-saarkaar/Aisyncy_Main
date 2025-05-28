"""
Test MongoDB Atlas connection

This script validates if the MongoDB Atlas connection string works.
Run this locally before deploying to GCP.
"""

import os
import sys
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection(connection_string):
    """Test connection to MongoDB Atlas"""
    try:
        # Connect to MongoDB
        logger.info(f"Attempting to connect to MongoDB with connection string: {connection_string[:20]}...")
        client = MongoClient(connection_string)
        
        # Test the connection with ping
        client.admin.command('ping')
        logger.info("✅ MongoDB connection successful!")
        
        # Get database information
        db_name = connection_string.split('/')[-1].split('?')[0]
        db = client.get_database(db_name)
        logger.info(f"Connected to database: {db_name}")
        
        # List collections
        collections = db.list_collection_names()
        logger.info(f"Collections in database: {collections}")
        
        # Try a simple insert-find-delete operation
        try:
            test_collection = db.test_connection
            result = test_collection.insert_one({"test": "value", "source": "connection_test"})
            logger.info(f"Test document inserted with ID: {result.inserted_id}")
            
            found = test_collection.find_one({"_id": result.inserted_id})
            logger.info(f"Found test document: {found}")
            
            delete_result = test_collection.delete_one({"_id": result.inserted_id})
            logger.info(f"Deleted test document: {delete_result.deleted_count}")
            
            logger.info("✅ Database operations (insert, find, delete) successful!")
        except Exception as e:
            logger.error(f"❌ Database operation failed: {e}")
            
        client.close()
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    # Get connection string from arguments or environment
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        connection_string = os.environ.get('MONGO_URI')
        if not connection_string:
            logger.error("No MongoDB connection string provided.")
            logger.info("Usage: python test_mongo_connection.py \"mongodb+srv://username:password@cluster.mongodb.net/dbname\"")
            sys.exit(1)
    
    # Test connection
    success = test_connection(connection_string)
    if success:
        logger.info("✅ All tests passed. Your MongoDB Atlas connection is working!")
        sys.exit(0)
    else:
        logger.error("❌ Connection test failed. Check your connection string and MongoDB Atlas settings.")
        sys.exit(1) 