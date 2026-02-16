# autokdewallet

A Python utility for automatically unlocking KDE Wallet (KWallet) using TPM-backed credentials via `systemd-creds`.

## Project Overview

The `autokdewallet` project aims to provide a seamless login experience for KDE users by automatically unlocking the default wallet (`kdewallet`) using a password securely stored in the system's TPM. It bypasses the manual password prompt by deriving the required PBKDF2-SHA512 hash and sending it directly to `kwalletd6` via D-Bus.

### Key Technologies

- **Python 3**: Core logic for hash derivation and D-Bus communication.
- **D-Bus**: Specifically the `org.kde.KWallet.pamOpen` method on `org.kde.kwalletd6`.
- **systemd-creds**: Used to encrypt and decrypt the wallet password using the TPM.
- **Systemd User Services**: For automating the unlock process during the graphical session startup.

### Architecture

- **`unlock.py`**: The main entry point. It retrieves the password, loads the salt, derives the hash, and calls the KWallet D-Bus interface.
- **`calculate_hash.py`**: Contains the logic to retrieve the password from `systemd-creds` and implement the PBKDF2-SHA512 hashing algorithm (50,000 iterations, 56-byte output) to match KWallet's internal requirements.
- **`get_salt.py`**: Utility to read the binary salt from `~/.local/share/kwalletd/kdewallet.salt`.
- **`justfile`**: A `just` task runner configuration for common operations like installation and credential generation.
- **`kwallet_auto_unlock.service`**: A systemd user service definition to run the script automatically upon login.

## Building and Running

The project uses `just` as a command runner.

### Initial Setup

1.  **Generate Credentials**:
    Encrypt your KWallet password using TPM:
    ```bash
    just generate_password password="your_actual_wallet_password"
    ```
    This creates a `password.cred` file in the project directory.

2.  **Install Service**:
    Copy the systemd service to the user configuration and enable it:
    ```bash
    just install
    ```

### Manual Execution

To test the unlocker manually:
```bash
just run
```

### Cleanup

To remove Python bytecode caches:
```bash
just clean
```

## Development Conventions

- **Dependencies**: Requires `python3` and `dbus-python` (or `dbus-next`).
- **Security**: The `password.cred` file is encrypted for the current user/hardware. Avoid sharing this file.
- **KWallet Version**: Targeted at KDE Plasma 6 (`kwalletd6`). For Plasma 5, the D-Bus service and interface names may need adjustment.
- **Hash Parameters**: Iterations and key size are strictly defined to match KWallet's `kwalletbackend.cpp` source code.
