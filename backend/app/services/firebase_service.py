"""
Firebase service for database operations
"""

import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import structlog
from app.core.config import settings, get_firebase_credentials

logger = structlog.get_logger(__name__)


class FirebaseService:
    """Firebase Firestore service for database operations"""
    
    def __init__(self):
        self.db = None
        self._initialized = False
        self._init_error = None
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK lazily"""
        if self._initialized:
            return self.db is not None
            
        try:
            # Check if Firebase is already initialized
            try:
                firebase_admin.get_app()
                logger.info("Firebase app already initialized")
            except ValueError:
                # Initialize Firebase
                cred_dict = get_firebase_credentials()
                
                # Check if we have the minimum required configuration
                if not cred_dict.get('project_id'):
                    logger.warning("Firebase credentials not properly configured, skipping Firebase initialization")
                    self._init_error = "Firebase credentials not configured"
                    self._initialized = True
                    return False
                
                # Handle missing private key gracefully
                if not cred_dict.get('private_key'):
                    logger.warning("Firebase private key not configured, skipping Firebase initialization")
                    self._init_error = "Firebase private key not configured"
                    self._initialized = True
                    return False
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully with credentials")
            
            self.db = firestore.client()
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Firebase", error=str(e))
            self._init_error = str(e)
            self._initialized = True
            return False
    
    def _get_db(self):
        """Get Firestore database client"""
        if not self._initialize_firebase():
            raise Exception(f"Firebase not available: {self._init_error}")
        return self.db
    
    async def create_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Create a document in Firestore"""
        try:
            db = self._get_db()
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            db.collection(collection).document(document_id).set(data)
            logger.info("Document created", collection=collection, document_id=document_id)
            return True
        except Exception as e:
            logger.error("Failed to create document", error=str(e), collection=collection)
            return False
    
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore"""
        try:
            db = self._get_db()
            doc = db.collection(collection).document(document_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error("Failed to get document", error=str(e), collection=collection, document_id=document_id)
            return None
    
    async def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Update a document in Firestore"""
        try:
            db = self._get_db()
            data['updated_at'] = datetime.utcnow()
            db.collection(collection).document(document_id).update(data)
            logger.info("Document updated", collection=collection, document_id=document_id)
            return True
        except Exception as e:
            logger.error("Failed to update document", error=str(e), collection=collection)
            return False
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from Firestore"""
        try:
            db = self._get_db()
            db.collection(collection).document(document_id).delete()
            logger.info("Document deleted", collection=collection, document_id=document_id)
            return True
        except Exception as e:
            logger.error("Failed to delete document", error=str(e), collection=collection)
            return False
    
    async def query_collection(
        self, 
        collection: str, 
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query a collection with optional filters"""
        try:
            db = self._get_db()
            query = db.collection(collection)
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            logger.error("Failed to query collection", error=str(e), collection=collection)
            return []
    
    async def get_collection_count(self, collection: str, filters: Optional[List[tuple]] = None) -> int:
        """Get count of documents in a collection"""
        try:
            db = self._get_db()
            query = db.collection(collection)
            
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            docs = query.stream()
            return len(list(docs))
        except Exception as e:
            logger.error("Failed to get collection count", error=str(e), collection=collection)
            return 0
    
    async def batch_write(self, operations: List[Dict[str, Any]]) -> bool:
        """Perform batch write operations"""
        try:
            db = self._get_db()
            batch = db.batch()
            
            for op in operations:
                operation_type = op['type']
                collection = op['collection']
                document_id = op['document_id']
                doc_ref = db.collection(collection).document(document_id)
                
                if operation_type == 'set':
                    batch.set(doc_ref, op['data'])
                elif operation_type == 'update':
                    batch.update(doc_ref, op['data'])
                elif operation_type == 'delete':
                    batch.delete(doc_ref)
            
            batch.commit()
            logger.info("Batch write completed", operations_count=len(operations))
            return True
        except Exception as e:
            logger.error("Failed to perform batch write", error=str(e))
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check Firebase service health"""
        try:
            if self._initialize_firebase():
                return {"status": "healthy", "service": "firebase"}
            else:
                return {"status": "unavailable", "service": "firebase", "error": self._init_error}
        except Exception as e:
            return {"status": "error", "service": "firebase", "error": str(e)}


# Global Firebase service instance - will not initialize on import
firebase_service = FirebaseService() 