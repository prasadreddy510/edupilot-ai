"""
Firebase Admin SDK service for authentication
"""

import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional
import os
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FirebaseService:
    """Firebase Admin SDK service"""

    _instance: Optional['FirebaseService'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                cred_path = settings.FIREBASE_CREDENTIALS_PATH

                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin SDK initialized successfully")
                else:
                    logger.warning(f"Firebase credentials not found at {cred_path}")
                    logger.warning("Firebase authentication will not work")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise

    def verify_id_token(self, id_token: str) -> dict:
        """
        Verify Firebase ID token

        Args:
            id_token: Firebase ID token from client

        Returns:
            Decoded token with user information

        Raises:
            ValueError: If token is invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except auth.InvalidIdTokenError:
            raise ValueError("Invalid Firebase ID token")
        except auth.ExpiredIdTokenError:
            raise ValueError("Firebase ID token has expired")
        except Exception as e:
            logger.error(f"Error verifying Firebase token: {str(e)}")
            raise ValueError(f"Failed to verify token: {str(e)}")

    def get_user_by_phone(self, phone_number: str) -> Optional[auth.UserRecord]:
        """
        Get Firebase user by phone number

        Args:
            phone_number: Phone number with country code (e.g., +911234567890)

        Returns:
            Firebase UserRecord if found, None otherwise
        """
        try:
            user = auth.get_user_by_phone_number(phone_number)
            return user
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting user by phone: {str(e)}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[auth.UserRecord]:
        """
        Get Firebase user by UID

        Args:
            uid: Firebase user UID

        Returns:
            Firebase UserRecord if found, None otherwise
        """
        try:
            user = auth.get_user(uid)
            return user
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting user by UID: {str(e)}")
            return None

    def create_custom_token(self, uid: str, additional_claims: Optional[dict] = None) -> str:
        """
        Create a custom Firebase token

        Args:
            uid: Firebase user UID
            additional_claims: Additional claims to include in token

        Returns:
            Custom token string
        """
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            return custom_token.decode('utf-8')
        except Exception as e:
            logger.error(f"Error creating custom token: {str(e)}")
            raise ValueError(f"Failed to create custom token: {str(e)}")


# Global instance
firebase_service = FirebaseService()
