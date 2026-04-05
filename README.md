
# 🔐 Quantum Vault (PQC-CLI)

**Quantum Vault** is a high-security Command Line Interface (CLI) designed to protect files against both classical and future quantum computing threats. It uses a **Hybrid Encryption** approach, combining Post-Quantum Cryptography (PQC) for key exchange and AES-256 for high-speed data encryption.

---

##  Key Features

* **Quantum-Resistant:** Utilizes Post-Quantum Cryptography (PQC) algorithms to ensure your data remains secure even in the era of quantum computers.
* **Hybrid Encryption:** Uses PQC to generate a shared secret, which is then used as a key for AES-256 encryption.
* **PQC Key Encapsulation:** Securely encrypts and transfers the AES key using Post-Quantum Cryptography mechanisms.
* **AES-256-GCM Encryption:** Provides confidentiality + integrity using nonce-based authenticated encryption.
* **Digital Signatures:** Automatically signs every vaulted file and verifies integrity during audits.
* **Automated Backups:** Creates redundant copies of your encrypted bundles in a dedicated backup directory.
* **Vault Auditing:** Detects missing, valid, and tampered signatures using verification logic.
* **File Management Commands:** Add, Extract, Delete, Restore supported via CLI.
* **Rich Terminal UI:** Beautiful, color-coded interface powered by the `rich` library.


## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/webgo-oss/quantum-vault.git
   cd quantum-vault
   ```

2. **Install dependencies:**
   ```bash
   
   pip install click rich
   
   ```
   *(Ensure you have your custom `crypto` and `vault` modules in the project path.)*


##  Usage

### 1. Initialize the Vault
Generate your quantum-resistant keys , signature pairs and set master password. **Run this first.** 
```bash

python main.py init

```

### 2. Secure a File (Add)
Encrypts a file, generates a signature, and creates a backup.
```bash

python main.py add "my_secret_data.txt"

```

### 3. Recover a File (Extract)
Decrypts the vault bundle using PQC and AES, then moves the original file to the `recovered/` folder.
```bash

python main.py extract "my_secret_data.txt"

```

### 4. Audit the Vault
Check the status of all encrypted files, including their size, last modified date, and cryptographic signature validity.
```bash

python main.py audit

```

### 5. Restore from Backup
If a vault file is accidentally deleted, restore it from the backup directory.
```bash

python main.py restore "my_secret_data.txt"

```


## make the below folders (Project Structure)

* `encrypted/`: Stores the `.vault` bundles (encrypted data + headers).
* `signatures/`: Stores cryptographic signatures for integrity verification.
* `vault_backup/`: Automated redundant copies of your vault files.
* `recovered/`: Destination for decrypted/extracted files.
~~~text
quantum-vault/
│
├── main.py
├── crypto/
├── keys/
│
├── encrypted/       # Encrypted vault files (.vault)
├── signatures/      # Digital signatures (.sig)
├── vault_backup/    # Backup files
├── recovered/       # Decrypted output files
├── uploads/         # your uploads 
~~~



##  Security Architecture
The vault follows a strict security pipeline:

1. **Normalization:**  
   Removes spaces from filenames to prevent CLI issues.

2. **Key Encapsulation (PQC):**  
   - Generates a secure **shared secret** using Post-Quantum Cryptography  
   - This shared secret is later used as the key for AES encryption  

3. **AES-256-GCM Encryption:**  
   - Encrypts file using the shared secret generated from PQC  
   - Uses nonce for randomness  
   - Ensures both confidentiality and integrity  

4. **Bundling:**  
   - Combines:
     - Encrypted file data  
     - PQC ciphertext (encrypted key)  
     - AES nonce  
   - Stored as `.vault` file  

5. **Digital Signing:**  
   - Entire bundle is signed  
   - Used later for verification during audit

   
##  Disclaimer
This project uses experimental Post-Quantum Cryptography. Ensure you back up your private keys in a secure, offline location. Loss of keys will result in permanent loss of data.
