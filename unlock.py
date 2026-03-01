"""Unlock the wallet with the password from the TPM"""

import dbus
from get_salt import load_binary_salt
from calculate_hash import derive_kwallet_hash, get_tpm_password

SALT = load_binary_salt()
PASSWORD = get_tpm_password()

hash = derive_kwallet_hash(PASSWORD, SALT)


def pam_open_wallet(
    hash_bytes: dbus.ByteArray, wallet_name: str = "kdewallet", timeout: int = 0
) -> bool:
    """
    Unlock kwallet with D-Bus's pamOpen() method

	method Q_NOREPLY: void org.kde.KWallet.pamOpen(QString wallet, QByteArray passwordHash, int sessionTimeout)

    Args:
        wallet_name: Wallet name
        hash_bytes: 56 bytes PBKDF2 hash
    """
    try:
        bus = dbus.SessionBus()
        proxy = bus.get_object("org.kde.kwalletd6", "/modules/kwalletd6")
        interface = dbus.Interface(proxy, "org.kde.KWallet")

        #  warp bytes to dbus.ByteArray to match QByteArray signature
        password_array = dbus.ByteArray(hash_bytes)

        # pamOpen(QString wallet, QByteArray passwordHash, int sessionTimeout)
        # sessionTimeout = 0 means Wallet will never time out during this session
        interface.pamOpen(wallet_name, password_array, timeout)

        print(f"Successfully sent unlock signal to wallet: {wallet_name}")
        return True
    except dbus.DBusException as e:
        print(f"Faile to call D-Bus: {e}")
        return False


if __name__ == "__main__":
    # print(f"Hash: {hash.hex()}") # disable for security reasons
    pam_open_wallet(hash)
