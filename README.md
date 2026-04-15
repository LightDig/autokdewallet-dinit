# AutoKDEWallet

**AutoKDEWallet-dinit** is a Python utility that automatically unlocks your KDE Wallet (KWallet) upon login using secure credentials stored in your system's TPM (Trusted Platform Module).

It eliminates the need to manually enter your wallet password every time you log in, while maintaining a high level of security by leveraging `clevis` for hardware-bound encryption. A dinit service file is included, however it is possible to run this script under any init as long as an appropriate service file is written.

## How It Works

1.  **Secure Storage**: Your KWallet password is encrypted using `clevis` and stored in a `password.cred` file. This file can only be decrypted on your specific hardware (bound to the TPM).
2.  **Automatic Unlock**: A dinit user service triggers the unlock script (`unlock.py`) when you log in.
3.  **Hash Derivation**: The script reads the encrypted password, retrieves your wallet's salt, and calculates the specific PBKDF2-SHA512 hash required by KWallet.
4.  **D-Bus Communication**: The calculated hash is sent directly to `kwalletd6` via the D-Bus `pamOpen` method, transparently unlocking the wallet.

## Prerequisites

- **Dinit**
- **Dinit user services** (e.g. `turnstiled` or `dinit-user-spawn`)
- **KDE Plasma 6** (Targeting `kwalletd6`).
- **TPM 2.0** enabled in your BIOS/UEFI.
- **Python 3**.
- **Python Libraries**: `dbus-python`.
- **Just** (Command runner, optional but recommended).

Additionally, you might have to add your user to the tss group and relog/reboot to access the tpm without root access.
```bash
sudo usermod -aG tss $USER
```

## Installation

### 1. Clone the Repository
```bash
cd $HOME/.config
git clone https://github.com/LightDig/autokdewallet-dinit
cd autokdewallet-dinit
```

> **Note**: if you want to store these files anywhere other than `$HOME/.config/autokdewallet-dinit`, you will have to manually adjust the filepaths in the service file.

use `just -l` to see all available commands.
```bash
> just -l
Available recipes:
    all
    clean
    enable                        # enable systemd service (user scope)
    generate_password password="" # use clevis to generate password.cred
    install                       # install dinit service (user scope)
    run
    setup                         # install and enable service
```
### 2. Generate Encrypted Credentials
You need to encrypt your KWallet password use `systemd-creds`. Replace `YOUR_KWALLET_PASSWORD` with your real wallet password.

Using `just`:
```bash
just generate_password "YOUR_KWALLET_PASSWORD"
```

Or manually:
```bash
clevis encrypt tpm2 '{}' <<< "YOUR_KWALLET_PASSWORD" > password.cred
```

> **Note**: This creates a `password.cred` file, which is encrypted and bound to your TPM. It cannot be used on another machine.

### 3. Install the Service
This installs the dinit service to `~/.config/dinit.d/` and enables it.

Using `just`:
```bash
just setup
```

Or manually:
```bash
mkdir -p ~/.config/dinit.d/
cp kwallet_auto_unlock ~/.config/dinit.d/
dinitctl enable kwallet_auto_unlock
```

## Usage

Make sure kwallet's pam module is disabled, otherwise pam will conflict with this project. Once installed, the service will run automatically every time you log in. You should no longer be prompted for your KWallet password.

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
    dinitctl status kwallet_auto_unlock
    ```
2.  **Enable Logging**:
    ```bash
    sed -Ei 's/^# (logfile)/\1/' $HOME/.config/dinit.d/kwallet_auto_unlock
    ```
    After that try rebooting or restarting the service and reading the log file at `$HOME/.config/autokdewallet-dinit/autokdewallet.log`
    Turn logging back off again when the problem has been resolved
    ```bash
    sed -Ei 's/^(logfile)/# \1/' $HOME/.config/dinit.d/kwallet_auto_unlock
    ```
3.  **Verify TPM/Credentials**:
    Try decrypting the credential manually to ensure `systemd-creds` is working
    and the password is correct:
    ```bash
    clevis decrypt < password.cred
    ```

## Files Structure

- **`unlock.py`**: Main script that orchestrates the unlocking.
- **`calculate_hash.py`**: Handles password decryption and KWallet-compatible hash generation.
- **`get_salt.py`**: Reads the KWallet salt from disk.
- **`kwallet_auto_unlock`**: Dinit service file.
- **`justfile`**: Command runner configuration.
