"""get salt from KWallet's `kdewallet` library"""

from pathlib import Path

# Default salt path of KWallet's `kdewallet` library
KWALLET_DEFAULT_SALT_PATH: Path = Path.home() / ".local/share/kwalletd/kdewallet.salt"


def load_binary_salt(salt_path: Path = KWALLET_DEFAULT_SALT_PATH) -> bytes:
    """Read the 56-byte binary salt from the KWallet library"""
    if not salt_path.exists():
        raise FileNotFoundError(f"Salt file not found: {salt_path}")

    with open(salt_path, "rb") as f:
        salt_data = f.read()

    # valdivate salt length is 56 bytes
    if len(salt_data) != 56:
        print(f"Exccept the salt length is 56, but got {len(salt_data)}.")

    return salt_data


if __name__ == "__main__":
    try:
        salt = load_binary_salt()
        print(f"Salt path: {KWALLET_DEFAULT_SALT_PATH}")
        print(f"Read salt: {salt.hex()}")
        print(f"Salt length: {len(salt)}")
    except Exception as e:
        print(f"Error while reading salt: {e}")
