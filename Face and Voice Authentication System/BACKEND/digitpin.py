# digitpin.py
import hashlib
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
)

def validate_pin(user_pin: Optional[str], stored_pin_hash: Optional[str]) -> bool:
    """Validates a PIN by comparing hashes."""
    if not isinstance(user_pin, str) or not isinstance(stored_pin_hash, str):
        logging.warning("Invalid PIN input types")
        return False
    
    if not user_pin or not stored_pin_hash:
        logging.warning("Empty PIN or hash provided")
        return False
    
    try:
        user_pin_hash = hashlib.sha256(user_pin.encode()).hexdigest()
        result = user_pin_hash == stored_pin_hash
        logging.debug(f"PIN hash comparison: {'match' if result else 'no match'}")
        return result
    except Exception as e:
        logging.error(f"PIN validation error: {e}")
        return False