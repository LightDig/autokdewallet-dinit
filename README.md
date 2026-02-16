# AutoKDEWallet

**AutoKDEWallet** is a Python utility that automatically unlocks your KDE Wallet (KWallet) upon login using secure credentials stored in your system's TPM (Trusted Platform Module).

It eliminates the need to manually enter your wallet password every time you log in, while maintaining a high level of security by leveraging `systemd-creds` for hardware-bound encryption.

## How It Works

1.  **Secure Storage**: Your KWallet password is encrypted using `systemd-creds` and stored in a `password.cred` file. This file can only be decrypted by your specific user on your specific hardware (bound to the TPM).
2.  **Automatic Unlock**: A systemd user service triggers the unlock script (`unlock.py`) when your graphical session starts.
3.  **Hash Derivation**: The script reads the encrypted password, retrieves your wallet's salt, and calculates the specific PBKDF2-SHA512 hash required by KWallet.
4.  **D-Bus Communication**: The calculated hash is sent directly to `kwalletd6` via the D-Bus `pamOpen` method, transparently unlocking the wallet.

## Prerequisites

- **Linux with systemd** (v248 or newer recommended for `systemd-creds`).
- **KDE Plasma 6** (Targeting `kwalletd6`).
- **TPM 2.0** enabled in your BIOS/UEFI.
- **Python 3**.
- **Python Libraries**: `dbus-python`.
- **Just** (Command runner, optional but recommended).

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/autokdewallet.git
cd autokdewallet
```
use `just -l` to see all available commands.
```bash
just -l
Available recipes:
    all
    clean
    generate_password password="" # use systemd-creds to generate password.cred
    install                       # install systemd service(user scope)
    run
```
### 2. Generate Encrypted Credentials
You need to encrypt your KWallet password. Replace `YOUR_KWALLET_PASSWORD` with your real wallet password.

Using `just`:
```bash
just generate_password "YOUR_KWALLET_PASSWORD"
```

Or manually:
```bash
echo -n "YOUR_KWALLET_PASSWORD" | systemd-creds encrypt --user - password.cred
```

> **Note**: This creates a `password.cred` file. This file is encrypted and bound to your TPM and user. It cannot be used on another machine.

### 3. Install the Service
This installs the systemd service to `~/.config/systemd/user/` and enables it.

Using `just`:
```bash
just install
```

Or manually:
```bash
mkdir -p ~/.config/systemd/user/
cp kwallet_auto_unlock.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now kwallet_auto_unlock.service
```

## Usage

Once installed, the service will run automatically every time you log in. You should no longer be prompted for your KWallet password.

### Manual Testing
You can run the unlock script manually to verify it works:

```bash
just run
# or
python3 unlock.py
```

### Cleaning Up
To remove Python cache files:
```bash
just clean
```

## Troubleshooting

If your wallet does not unlock automatically:

1.  **Check Service Status**:
    ```bash
    systemctl --user status kwallet_auto_unlock.service
    ```
2.  **Check Logs**:
    ```bash
    journalctl --user -u kwallet_auto_unlock.service
    ```
3.  **Verify TPM/Credentials**:
    Try decrypting the credential manually to ensure `systemd-creds` is working:
    ```bash
    systemd-creds decrypt --user password.cred -
    ```

## Files Structure

- **`unlock.py`**: Main script that orchestrates the unlocking.
- **`calculate_hash.py`**: Handles password decryption and KWallet-compatible hash generation.
- **`get_salt.py`**: Reads the KWallet salt from disk.
- **`kwallet_auto_unlock.service`**: Systemd service file.
- **`justfile`**: Command runner configuration.
