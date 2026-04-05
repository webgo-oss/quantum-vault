import os
import shutil
import click
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from crypto.pqc_keygen import generate_keys
from crypto.aes_encrypt import encrypt_file
from crypto.pqc_encrypt import generate_shared_secret
from crypto.aes_decrypt import decrypt_file
from crypto.pqc_decrypt import decrypt_aes_key
from crypto.signature import generate_signature_keys, generate_signature, verify_signature
from vault.bundle import create_bundle
from vault.load_bundle import load_bundle
from vault.backup import backup_file

console = Console()

VAULT_DIR = "encrypted"
BACKUP_DIR = "vault_backup"
SIG_DIR = "signatures"


def logo():
    console.print()
    console.print(
"""[bold blue]██╗   ██╗ █████╗ ██╗   ██╗██╗   ████████╗
██║   ██║██╔══██╗██║   ██║██║   ╚══██╔══╝
██║   ██║███████║██║   ██║██║      ██║   
╚██╗ ██╔╝██╔══██║██║   ██║██║      ██║   
 ╚████╔╝ ██║  ██║╚██████╔╝███████╗ ██║   
  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚═╝[/bold blue]"""
    )


def info(msg):
    console.print(f"[blue]→ {msg}[/blue]")


def success(msg):
    console.print(f"[green]✔ {msg}[/green]")


def error(msg):
    console.print(f"[red]✖ {msg}[/red]")


def warn(msg):
    console.print(f"[yellow]⚠ {msg}[/yellow]")


@click.group()
def cli():
    logo()

def normalize_filename(name):
    """Remove spaces from file name"""
    return name.replace(" ", "")

@cli.command()
def init():
    """Initialize vault"""
    console.print("\n[bold cyan]INIT VAULT[/bold cyan]")
    generate_keys()
    generate_signature_keys()
    success("Vault initialized")


@cli.command()
@click.argument("file", nargs=-1)
def add(file):
    """Add file to vault"""
    file_path = " ".join(file)  

    if not os.path.exists(file_path):
        error("File not found")
        return

    console.print("\n[bold cyan]ADD FILE[/bold cyan]")

    file_name = normalize_filename(os.path.basename(file_path))

    os.makedirs(VAULT_DIR, exist_ok=True)
    vault_file = f"{VAULT_DIR}/{file_name}.vault"

    info("Encrypting file")
    ciphertext, shared_secret = generate_shared_secret()
    encrypted_data, nonce = encrypt_file(file_path, shared_secret)

    info("Creating bundle")
    create_bundle(encrypted_data, ciphertext, nonce, vault_file)

    info("Generating signature")
    with open(vault_file, "rb") as f:
        data = f.read()
    signature = generate_signature(data)

    os.makedirs(SIG_DIR, exist_ok=True)
    info("Saving signature")
    with open(f"{SIG_DIR}/{file_name}.sig", "wb") as f:
        f.write(signature)

    info("Creating backup")
    backup_file(vault_file)

    success(f"File secured: {file_name}")


@cli.command()
@click.argument("file", nargs=-1)
def extract(file):
    """Extract file"""
    file_path = " ".join(file)
    file_name = normalize_filename(file_path)
    vault_file = f"{VAULT_DIR}/{file_name}.vault"

    if not os.path.exists(vault_file):
        error("File not found")
        return

    console.print("\n[bold cyan]EXTRACT FILE[/bold cyan]")

    info("Loading vault")
    encrypted_key, nonce, encrypted_file = load_bundle(vault_file)

    info("Decrypting file")
    shared_secret = decrypt_aes_key(encrypted_key)
    original_data = decrypt_file(encrypted_file, nonce, shared_secret)

    os.makedirs("recovered", exist_ok=True)
    output_path = f"recovered/{file_name}"

    info("Writing file")
    with open(output_path, "wb") as f:
        f.write(original_data)

    os.remove(vault_file)

    success(f"Recovered: {file_name}")


@cli.command()
@click.argument("file", nargs=-1)
def delete(file):
    """Delete file"""
    file_path = " ".join(file)
    file_name = normalize_filename(file_path)
    vault_file = f"{VAULT_DIR}/{file_name}.vault"

    if not os.path.exists(vault_file):
        error("File not found")
        return

    console.print("\n[bold cyan]DELETE FILE[/bold cyan]")

    os.remove(vault_file)

    success(f"Deleted: {file_name}")


@cli.command()
@click.argument("file", nargs=-1)
def restore(file):
    """Restore file"""
    file_path = " ".join(file)
    file_name = normalize_filename(file_path)
    backup_file_path = f"{BACKUP_DIR}/{file_name}.vault"
    restore_path = f"{VAULT_DIR}/{file_name}.vault"

    if not os.path.exists(backup_file_path):
        error("Backup not found")
        return

    console.print("\n[bold cyan]RESTORE FILE[/bold cyan]")

    os.makedirs(VAULT_DIR, exist_ok=True)
    shutil.copy(backup_file_path, restore_path)

    success(f"Restored: {file_name}")

@cli.command()
def audit():
    """Audit vault"""
    console.print("\n[bold cyan]VAULT AUDIT[/bold cyan]")

    os.makedirs(VAULT_DIR, exist_ok=True)
    files = [f for f in os.listdir(VAULT_DIR) if f.endswith(".vault")]

    if not files:
        warn("Vault is empty")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Size")
    table.add_column("Last Modified")
    table.add_column("Signature")
    table.add_column("Status")

    for file in files:
        vault_path = f"{VAULT_DIR}/{file}"
        sig_path = f"{SIG_DIR}/{file.replace('.vault','')}.sig"

        name = file.replace(".vault", "")
        size = f"{os.path.getsize(vault_path)/1024:.1f} KB"

        mod_time = datetime.fromtimestamp(
            os.path.getmtime(vault_path)
        ).strftime("%Y-%m-%d %H:%M")

        if not os.path.exists(sig_path):
            sig = "[yellow]MISSING[/yellow]"
            status = "[yellow]UNVERIFIED[/yellow]"
        else:
            with open(vault_path, "rb") as f:
                data = f.read()
            with open(sig_path, "rb") as f:
                signature = f.read()

            if verify_signature(data, signature):
                sig = "[green]VALID[/green]"
                status = "[green]SAFE[/green]"
            else:
                sig = "[red]INVALID[/red]"
                status = "[red]TAMPERED[/red]"

        table.add_row(name, size, mod_time, sig, status)

    console.print(table)


if __name__ == "__main__":
    cli()