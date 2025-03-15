import hashlib

def validate_pin(user_pin: str, stored_pin_hash: str) -> bool:
    """
    Validates the user's PIN by comparing hashes.

    :param user_pin: The user-entered PIN as a string.
    :param stored_pin_hash: The hashed PIN for comparison.
    :return: True if the PIN is correct, False otherwise.
    """
    user_pin_hash = hashlib.sha256(user_pin.encode()).hexdigest()
    return user_pin_hash == stored_pin_hash

if __name__ == "__main__":
    stored_hash = hashlib.sha256("1234".encode()).hexdigest()  # Example stored PIN
    user_input = input("Enter your PIN: ")
    if validate_pin(user_input, stored_hash):
        print("PIN Authentication Successful")
    else:
        print("PIN Authentication Failed")