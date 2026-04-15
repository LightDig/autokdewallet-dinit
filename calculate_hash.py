import hashlib
from pathlib import Path
import subprocess
from get_salt import load_binary_salt

# PBKDF2 parameters in the source code,
# see https://github.com/KDE/kwallet/blob/master/src/backend/kwalletbackend.cpp#L100 for details
ITERATIONS = 50000
KEY_SIZE = 56
HASH_ALGO = "sha512"


def get_tpm_password(
    cred_file: str | Path = Path(__file__).parent / "password.cred",
) -> bytes:
    # cat the password.cred file, pipe it into clevis decrypt, return the result.
    p1 = subprocess.Popen(["cat",cred_file], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["clevis", "decrypt"],stdin=p1.stdout,stdout=subprocess.PIPE)
    p1.stdout.close()
    result = p2.communicate()[0]
    # Remove the trailing newline character and return bytes
    return result.strip()


def derive_kwallet_hash(password: bytes, salt: bytes) -> bytes:
    """Calculate the PBKDF2-SHA512 hash compatible with KWallet PAM interface"""
    return hashlib.pbkdf2_hmac(HASH_ALGO, password, salt, ITERATIONS, KEY_SIZE)


if __name__ == "__main__":
    try:
        # Load the salt from the KWallet library
        current_salt = load_binary_salt()

        # Get the password from the TPM
        password_plain = get_tpm_password()

        hash = derive_kwallet_hash(password_plain, current_salt)

        print(f"Hashing complete:\n{hash.hex()}")

    except subprocess.CalledProcessError:
        print("TPM decryption failed. Please check the hardware status or whether Secure Boot is enabled.")
    except Exception as e:
        print(f"Error: {e}")
