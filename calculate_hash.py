import hashlib
import subprocess
from get_salt import load_binary_salt

# PBKDF2 parameters in the source code,
# see https://github.com/KDE/kwallet/blob/master/src/backend/kwalletbackend.cpp#L100 for details
ITERATIONS = 50000
KEY_SIZE = 56
HASH_ALGO = "sha512"


def get_tpm_password(cred_file="message.cred"):
    """use systemd-creds to decrypt the password from the TPM"""

    result = subprocess.run(
        ["systemd-creds", "decrypt", cred_file, "-"], capture_output=True, check=True
    )
    # Remove the trailing newline character and return bytes
    return result.stdout.strip()


def derive_kwallet_hash(password: bytes, salt: bytes):
    """Calculate the PBKDF2-SHA512 hash compatible with KWallet PAM interface"""
    return hashlib.pbkdf2_hmac(HASH_ALGO, password, salt, ITERATIONS, KEY_SIZE)


if __name__ == "__main__":
    try:
        # Load the salt from the KWallet library
        current_salt = load_binary_salt()

        # Get the password from the TPM
        password_plain = get_tpm_password("message.cred")

        hash = derive_kwallet_hash(password_plain, current_salt)

        print(f"计算完成！56字节哈希为:\n{hash.hex()}")

    except subprocess.CalledProcessError:
        print("TPM 解密失败，请检查 hardware 状态或 Secure Boot 是否开启。")
    except Exception as e:
        print(f"执行出错: {e}")
