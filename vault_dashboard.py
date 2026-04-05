from flask import Flask, render_template
import os
from datetime import datetime
from crypto.signature import verify_signature

VAULT_DIR = "encrypted"
BACKUP_DIR = "vault_backup"
SIG_DIR = "signatures"
RECOVERED_DIR = "recovered" 

app = Flask(__name__)

def get_files_info():
    vault_files, backup_files, sig_files, recovered_files = [], [], [], []

    if os.path.exists(VAULT_DIR):
        for file in os.listdir(VAULT_DIR):
            path = os.path.join(VAULT_DIR, file)
            size = os.path.getsize(path) / 1024
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
            sig_path = os.path.join(SIG_DIR, file.replace(".vault", ".sig"))

            if not os.path.exists(sig_path):
                sig_status = "MISSING"
                safe_status = "UNVERIFIED"
            else:
                with open(path, "rb") as f:
                    data = f.read()
                with open(sig_path, "rb") as f:
                    signature = f.read()
                if verify_signature(data, signature):
                    sig_status = "VALID"
                    safe_status = "SAFE"
                else:
                    sig_status = "INVALID"
                    safe_status = "TAMPERED"

            vault_files.append({
                "name": file,
                "path": path,
                "size": f"{size:.1f} KB",
                "modified": modified,
                "signature": sig_status,
                "status": safe_status
            })

    if os.path.exists(BACKUP_DIR):
        for file in os.listdir(BACKUP_DIR):
            path = os.path.join(BACKUP_DIR, file)
            size = os.path.getsize(path) / 1024
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
            backup_files.append({
                "name": file,
                "path": path,
                "size": f"{size:.1f} KB",
                "modified": modified
            })

    if os.path.exists(SIG_DIR):
        for file in os.listdir(SIG_DIR):
            key_name = os.path.splitext(file)[0]
            sig_files.append({"name": key_name})

    if os.path.exists(RECOVERED_DIR):
        for file in os.listdir(RECOVERED_DIR):
            path = os.path.join(RECOVERED_DIR, file)
            size = os.path.getsize(path) / 1024
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
            recovered_files.append({
                "name": file,
                "path": path,
                "size": f"{size:.1f} KB",
                "modified": modified
            })

    return vault_files, backup_files, sig_files, recovered_files

@app.route("/")
def dashboard():
    vault_files, backup_files, sig_keys, recovered_files = get_files_info()
    return render_template("dashboard.html",
                           vault_files=vault_files,
                           backup_files=backup_files,
                           sig_keys=sig_keys,
                           recovered_files=recovered_files,
                           total_vault=len(vault_files),
                           total_backup=len(backup_files),
                           total_keys=len(sig_keys),
                           total_recovered=len(recovered_files))

if __name__ == "__main__":
    app.run(debug=True)