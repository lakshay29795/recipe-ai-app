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
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            logger.info("Firebase app already initialized")
        except ValueError:
            # Initialize Firebase
            cred_dict = get_firebase_credentials()
            
            if not cred_dict.get('project_id'):
                logger.warning("Firebase credentials not configured, initializing with default project")
                # For development, we'll skip the credential verification
                firebase_admin.initialize_app()
                logger.info("Firebase initialized without credentials for development")
            else:
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully with credentials")
        
        self.db = firestore.client()
    
    async def create_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Create a document in Firestore"""
        try:
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            self.db.collection(collection).document(document_id).set(data)
            logger.info("Document created", collection=collection, document_id=document_id)
            return True
        except Exception as e:
            logger.error("Failed to create document", error=str(e), collection=collection)
            return False
    
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore"""
        try:
            doc = self.db.collection(collection).document(document_id).get()
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
            data['updated_at'] = datetime.utcnow()
            self.db.collection(collection).document(document_id).update(data)
            logger.info("Document updated", collection=collection, document_id=document_id)
            return True
        except Exception as e:
            logger.error("Failed to update document", error=str(e), collection=collection)
            return False
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from Firestore"""
        try:
            self.db.collection(collection).document(document_id).delete()
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
            query = self.db.collection(collection)
            
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
            query = self.db.collection(collection)
            
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
            batch = self.db.batch()
            
            for op in operations:
                operation_type = op['type']
                collection = op['collection']
                document_id = op['document_id']
                doc_ref = self.db.collection(collection).document(document_id)
                
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


# Global Firebase service instance
firebase_service = FirebaseService() 