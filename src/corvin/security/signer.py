import hashlib
import hmac
import secrets

class SecurityException(Exception):
    """Base exception for Ravens security violations."""
    pass


class InvalidUserSignatureException(SecurityException):
    """Raised when a user ID signature is missing, forged, or tampered with."""
    pass


class UserIdentitySigner:
    """
    Cryptographic HMAC-SHA256 User ID Signer and Validator.
    
    Prevents attackers from spoofing legitimate user IDs to exhaust
    another user's patience quota or cause malicious strike bans.
    """

    def __init__(self, secret_key: str):
        if not secret_key or len(secret_key) < 16:
            raise ValueError("secret_key must be at least 16 characters long for cryptographic security.")
        self.secret_key = secret_key.encode("utf-8")

    def sign_id(self, user_id: str) -> str:
        """
        Generates a tamper-proof signed user token.
        Format: '{user_id}.{hex_hmac_signature}'
        """
        clean_id = user_id.strip()
        signature = hmac.new(
            self.secret_key,
            clean_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"{clean_id}.{signature}"

    def verify_id(self, signed_token: str) -> str:
        """
        Validates the signature on a signed user token and extracts the clean user_id.
        Raises InvalidUserSignatureException if tampered or invalid.
        """
        if not signed_token or "." not in signed_token:
            raise InvalidUserSignatureException("Token format invalid: missing signature separator '.'")

        parts = signed_token.rsplit(".", 1)
        user_id, signature = parts[0], parts[1]

        expected_sig = hmac.new(
            self.secret_key,
            user_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(signature, expected_sig):
            raise InvalidUserSignatureException(
                f"Signature verification failed for user '{user_id}'. Identity spoofing attempt detected."
            )

        return user_id

