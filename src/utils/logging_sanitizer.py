"""
Logging Sanitizer - PII Removal for Security Compliance

Implements M-1 security requirement: Remove personally identifiable
information (PII) from logs to comply with privacy regulations (GDPR, CCPA).

Security Impact:
- Prevents PII leakage in logs
- Complies with data minimization principle
- Reduces risk of data breaches via log files
- Enables safer log aggregation and analysis
"""

import hashlib
import logging
import re
from typing import Any, Dict, Optional
from uuid import UUID


# PII patterns to detect and sanitize
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
IP_ADDRESS_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

# API keys and tokens
API_KEY_PATTERN = re.compile(r'\b(sk-[a-zA-Z0-9]{48}|sk-ant-[a-zA-Z0-9-_]{40,})\b')
JWT_PATTERN = re.compile(r'\beyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\b')

# Sensitive field names (case-insensitive)
SENSITIVE_FIELDS = {
    'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
    'access_token', 'refresh_token', 'private_key', 'ssh_key',
    'email', 'phone', 'ssn', 'credit_card', 'cc_number',
    'first_name', 'last_name', 'full_name', 'address', 'postal_code', 'zip_code'
}


class LoggingSanitizer:
    """
    Sanitize sensitive information from log messages.

    Features:
    - Pattern-based PII detection (email, phone, SSN, credit cards)
    - Field-based sanitization (passwords, tokens, API keys)
    - UUID anonymization (hash UUIDs for tracking without exposing)
    - IP address masking
    - Customizable redaction strategies
    """

    def __init__(
        self,
        hash_uuids: bool = True,
        mask_emails: bool = True,
        mask_ips: bool = True,
        redaction_text: str = "[REDACTED]"
    ):
        """
        Initialize sanitizer with configuration.

        Args:
            hash_uuids: If True, hash UUIDs instead of redacting
            mask_emails: If True, mask email addresses
            mask_ips: If True, mask IP addresses
            redaction_text: Text to use for redacted content
        """
        self.hash_uuids = hash_uuids
        self.mask_emails = mask_emails
        self.mask_ips = mask_ips
        self.redaction_text = redaction_text

    def sanitize_message(self, message: str) -> str:
        """
        Sanitize a log message string.

        Args:
            message: Log message to sanitize

        Returns:
            Sanitized message with PII removed/masked
        """
        if not isinstance(message, str):
            message = str(message)

        # Redact API keys and tokens (highest priority)
        message = API_KEY_PATTERN.sub(self.redaction_text, message)
        message = JWT_PATTERN.sub(self.redaction_text, message)

        # Redact credit card numbers
        message = CREDIT_CARD_PATTERN.sub(self.redaction_text, message)

        # Redact SSN
        message = SSN_PATTERN.sub(self.redaction_text, message)

        # Mask or redact emails
        if self.mask_emails:
            message = EMAIL_PATTERN.sub(self._mask_email, message)
        else:
            # If not masking, completely redact emails
            message = EMAIL_PATTERN.sub(self.redaction_text, message)

        # Redact phone numbers
        message = PHONE_PATTERN.sub(self.redaction_text, message)

        # Mask IP addresses
        if self.mask_ips:
            message = IP_ADDRESS_PATTERN.sub(self._mask_ip, message)
        else:
            # If not masking, completely redact IPs
            message = IP_ADDRESS_PATTERN.sub(self.redaction_text, message)

        return message

    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a dictionary (e.g., structured log extra fields).

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary with PII removed/masked
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Check if key is sensitive field
            if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
                sanitized[key] = self.redaction_text
                continue

            # Special handling for UUIDs
            if key.endswith('_id') or key == 'session_id' or key == 'user_id':
                if isinstance(value, (str, UUID)):
                    sanitized[key] = self._anonymize_uuid(str(value))
                else:
                    sanitized[key] = value
                continue

            # Recursively sanitize nested dicts
            if isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_dict(item) if isinstance(item, dict) else self._sanitize_value(item)
                    for item in value
                ]
            else:
                sanitized[key] = self._sanitize_value(value)

        return sanitized

    def _sanitize_value(self, value: Any) -> Any:
        """
        Sanitize a single value (string, number, etc.).

        Args:
            value: Value to sanitize

        Returns:
            Sanitized value
        """
        if isinstance(value, str):
            return self.sanitize_message(value)
        return value

    def _mask_email(self, match: re.Match) -> str:
        """
        Mask email address while preserving domain.

        Example: john.doe@example.com → j***@example.com

        Args:
            match: Regex match object

        Returns:
            Masked email
        """
        email = match.group(0)
        parts = email.split('@')

        if len(parts) != 2:
            return self.redaction_text

        local, domain = parts

        # Show first character + asterisks
        if len(local) > 0:
            masked_local = local[0] + '***'
        else:
            masked_local = '***'

        return f"{masked_local}@{domain}"

    def _mask_ip(self, match: re.Match) -> str:
        """
        Mask IP address, preserving first two octets.

        Example: 192.168.1.100 → 192.168.***.***

        Args:
            match: Regex match object

        Returns:
            Masked IP address
        """
        ip = match.group(0)
        parts = ip.split('.')

        if len(parts) != 4:
            return self.redaction_text

        return f"{parts[0]}.{parts[1]}.***. ***"

    def _anonymize_uuid(self, uuid_str: str) -> str:
        """
        Anonymize UUID using SHA-256 hash (first 16 chars).

        This allows correlation in logs without exposing actual UUIDs.

        Example: 550e8400-e29b-41d4-a716-446655440000 → hash:a1b2c3d4e5f6g7h8

        Args:
            uuid_str: UUID string to anonymize

        Returns:
            Hashed UUID or redaction text
        """
        if not self.hash_uuids:
            return self.redaction_text

        try:
            # Create deterministic hash (same UUID always hashes to same value)
            hash_digest = hashlib.sha256(uuid_str.encode()).hexdigest()
            return f"hash:{hash_digest[:16]}"
        except Exception:
            return self.redaction_text


# Global sanitizer instance
_sanitizer = LoggingSanitizer()


def sanitize_log_message(message: str) -> str:
    """
    Sanitize a log message (convenience function).

    Args:
        message: Log message to sanitize

    Returns:
        Sanitized message
    """
    return _sanitizer.sanitize_message(message)


def sanitize_log_extra(extra: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize log extra fields (convenience function).

    Args:
        extra: Dictionary of extra fields

    Returns:
        Sanitized extra fields
    """
    return _sanitizer.sanitize_dict(extra)


class SanitizingFilter(logging.Filter):
    """
    Logging filter that automatically sanitizes log records.

    Usage:
        import logging
        from src.utils.logging_sanitizer import SanitizingFilter

        logger = logging.getLogger(__name__)
        logger.addFilter(SanitizingFilter())

        # PII will be automatically sanitized
        logger.info("User john.doe@example.com logged in", extra={"email": "john.doe@example.com"})
        # Logged as: "User j***@example.com logged in", extra={"email": "[REDACTED]"}
    """

    def __init__(self, sanitizer: Optional[LoggingSanitizer] = None):
        """
        Initialize filter with optional custom sanitizer.

        Args:
            sanitizer: Custom sanitizer instance (uses global if None)
        """
        super().__init__()
        self.sanitizer = sanitizer or _sanitizer

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Sanitize log record before emission.

        Args:
            record: Log record to filter

        Returns:
            True (always allow record, just sanitize it)
        """
        # Sanitize message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self.sanitizer.sanitize_message(record.msg)

        # Sanitize args (for %s formatting)
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = self.sanitizer.sanitize_dict(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self.sanitizer.sanitize_message(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        # Sanitize extra fields (structured logging)
        if hasattr(record, '__dict__'):
            # Don't sanitize standard logging attributes
            standard_attrs = {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info'
            }

            extra_fields = {
                key: value
                for key, value in record.__dict__.items()
                if key not in standard_attrs
            }

            if extra_fields:
                sanitized_extra = self.sanitizer.sanitize_dict(extra_fields)
                for key, value in sanitized_extra.items():
                    setattr(record, key, value)

        return True


def setup_sanitized_logging(logger: logging.Logger) -> None:
    """
    Configure logger with PII sanitization.

    Args:
        logger: Logger to configure
    """
    logger.addFilter(SanitizingFilter())


def configure_root_logger_sanitization() -> None:
    """
    Configure root logger with PII sanitization filter.

    Call this at application startup to sanitize all logs.
    """
    root_logger = logging.getLogger()
    root_logger.addFilter(SanitizingFilter())


# Example usage and testing
if __name__ == "__main__":
    # Configure logging with sanitization
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    setup_sanitized_logging(logger)

    # Test cases
    logger.info("User john.doe@example.com logged in from 192.168.1.100")
    # Output: User j***@example.com logged in from 192.168.***.***

    logger.info(
        "Session created",
        extra={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user@example.com",
            "email": "john.doe@example.com",
            "password": "secret123"
        }
    )
    # Output: Session created (with sanitized extra fields)

    logger.warning("API key exposed: sk-1234567890abcdefghijklmnopqrstuvwxyz123456789012")
    # Output: API key exposed: [REDACTED]

    logger.error("Credit card: 4532-1234-5678-9010 charged for $500")
    # Output: Credit card: [REDACTED] charged for $500
