"""
Authentication for version discovery endpoints (FR-022).

This module provides API key and OAuth token validation for securing
version discovery endpoints.
"""

import hashlib
import hmac
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AuthMethod(str, Enum):
    """Authentication method used."""
    
    API_KEY  = "API_KEY"
    OAUTH    = "OAUTH"
    NONE     = "NONE"


@dataclass
class AuthResult:
    """
    Result of authentication attempt.
    
    Attributes:
        authenticated: Whether authentication succeeded
        method: Authentication method used
        consumer_id: Authenticated consumer identifier
        error_message: Error message if authentication failed
    """
    
    authenticated:  bool
    method:         AuthMethod
    consumer_id:    Optional[str] = None
    error_message:  Optional[str] = None


class APIKeyAuthenticator:
    """
    API key authentication (FR-022).
    
    Validates API keys from X-API-Key header against a secure store.
    Production implementations should use a database or secrets manager.
    
    Example:
        >>> auth = APIKeyAuthenticator({"key_abc123": "consumer_1"})
        >>> result = auth.authenticate(b"key_abc123")
        >>> print(result.authenticated)
        True
    """
    
    def __init__(self, api_keys: dict[str, str]):
        """
        Initialize API key authenticator.
        
        Args:
            api_keys: Mapping of API key -> consumer ID
        """
        # Store hashed keys for security (production should use database)
        self.api_keys = {
            self._hash_key(key): consumer_id
            for key, consumer_id in api_keys.items()
        }
    
    def authenticate(self, api_key: bytes) -> AuthResult:
        """
        Authenticate API key.
        
        Args:
            api_key: API key from X-API-Key header
        
        Returns:
            AuthResult with authentication status
        """
        if not api_key:
            return AuthResult(
                authenticated=False,
                method=AuthMethod.API_KEY,
                error_message="Missing API key"
            )
        
        # Decode and hash key
        key_str = api_key.decode("utf-8", errors="ignore")
        key_hash = self._hash_key(key_str)
        
        # Look up consumer
        consumer_id = self.api_keys.get(key_hash)
        if consumer_id:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                consumer_id=consumer_id
            )
        
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error_message="Invalid API key"
        )
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash API key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()


class OAuthAuthenticator:
    """
    OAuth token authentication (FR-022).
    
    Validates OAuth Bearer tokens. Production implementations should
    verify JWT signatures and claims.
    
    Example:
        >>> auth = OAuthAuthenticator()
        >>> result = auth.authenticate(b"Bearer valid_token")
        >>> print(result.authenticated)
        True
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize OAuth authenticator.
        
        Args:
            secret_key: Secret key for JWT verification (production)
        """
        self.secret_key = secret_key
    
    def authenticate(self, authorization_header: bytes) -> AuthResult:
        """
        Authenticate OAuth Bearer token.
        
        Args:
            authorization_header: Authorization header value
        
        Returns:
            AuthResult with authentication status
        """
        if not authorization_header:
            return AuthResult(
                authenticated=False,
                method=AuthMethod.OAUTH,
                error_message="Missing Authorization header"
            )
        
        # Decode header
        auth_str = authorization_header.decode("utf-8", errors="ignore")
        
        # Check Bearer scheme
        if not auth_str.startswith("Bearer "):
            return AuthResult(
                authenticated=False,
                method=AuthMethod.OAUTH,
                error_message="Invalid authorization scheme"
            )
        
        # Extract token
        token = auth_str[7:].strip()
        
        # Validate token (simplified - production should verify JWT)
        if self._validate_token(token):
            # Extract consumer ID from token
            consumer_id = self._extract_consumer_id(token)
            return AuthResult(
                authenticated=True,
                method=AuthMethod.OAUTH,
                consumer_id=consumer_id
            )
        
        return AuthResult(
            authenticated=False,
            method=AuthMethod.OAUTH,
            error_message="Invalid or expired token"
        )
    
    def _validate_token(self, token: str) -> bool:
        """
        Validate OAuth token.
        
        Production implementation should:
        - Verify JWT signature
        - Check expiration
        - Validate issuer and audience
        - Check token revocation
        """
        # Simplified validation for demo
        return len(token) >= 20 and not token.startswith("invalid_")
    
    def _extract_consumer_id(self, token: str) -> str:
        """
        Extract consumer ID from token.
        
        Production implementation should parse JWT claims.
        """
        # Simplified extraction for demo
        return f"oauth_{hashlib.sha256(token.encode()).hexdigest()[:16]}"


def extract_credentials_from_headers(
    headers: dict[bytes, bytes]
) -> tuple[Optional[bytes], Optional[bytes]]:
    """
    Extract authentication credentials from request headers.
    
    Args:
        headers: Request headers
    
    Returns:
        Tuple of (api_key, authorization_header)
    """
    api_key = None
    authorization = None
    
    for header_name, header_value in headers.items():
        lower_name = header_name.lower()
        
        if lower_name == b"x-api-key":
            api_key = header_value
        elif lower_name == b"authorization":
            authorization = header_value
    
    return api_key, authorization


def authenticate_request(
    headers: dict[bytes, bytes],
    api_key_auth: Optional[APIKeyAuthenticator] = None,
    oauth_auth: Optional[OAuthAuthenticator] = None
) -> AuthResult:
    """
    Authenticate request using available methods.
    
    Priority: API Key > OAuth > None
    
    Args:
        headers: Request headers
        api_key_auth: API key authenticator (optional)
        oauth_auth: OAuth authenticator (optional)
    
    Returns:
        AuthResult with authentication status
    """
    api_key, authorization = extract_credentials_from_headers(headers)
    
    # Try API key first
    if api_key and api_key_auth:
        result = api_key_auth.authenticate(api_key)
        if result.authenticated:
            return result
    
    # Try OAuth
    if authorization and oauth_auth:
        result = oauth_auth.authenticate(authorization)
        if result.authenticated:
            return result
    
    # No authentication
    return AuthResult(
        authenticated=False,
        method=AuthMethod.NONE,
        error_message="No valid credentials provided"
    )
