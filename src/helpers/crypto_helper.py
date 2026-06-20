import os
import logging
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _resolve_fernet_key() -> bytes:
    """
    Carrega AES_SECRET_KEY do .env ou gera chave efêmera para desenvolvimento.
    Ignora valores inválidos (Fernet exige 32 bytes em base64 url-safe).
    """
    raw = (os.getenv("AES_SECRET_KEY") or "").strip()
    if raw:
        try:
            Fernet(raw.encode())
            return raw.encode()
        except (ValueError, TypeError):
            logger.warning(
                "AES_SECRET_KEY inválida no .env; usando chave efêmera. "
                "Gere uma com: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
    return Fernet.generate_key()


_fernet = Fernet(_resolve_fernet_key())


def encrypt_data(data: str) -> str:
    """Criptografa uma string usando Fernet (AES-128-CBC + HMAC)."""
    if not data:
        return data
    return _fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Descriptografa uma string criptografada com encrypt_data."""
    if not encrypted_data:
        return encrypted_data
    try:
        return _fernet.decrypt(encrypted_data.encode()).decode()
    except InvalidToken:
        logger.warning("Falha ao descriptografar: chave diferente da usada na criptografia.")
        raise


import hashlib
import hmac

def hash_password(password: str) -> str:
    """Gera o hash PBKDF2-SHA256 de uma senha para armazenamento seguro."""
    salt = os.urandom(16)
    rounds = 100000
    db_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, rounds)
    return f"pbkdf2_sha256${rounds}${salt.hex()}${db_hash.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha coincide com o hash fornecido."""
    try:
        parts = hashed.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        rounds = int(parts[1])
        salt = bytes.fromhex(parts[2])
        original_hash = bytes.fromhex(parts[3])
        db_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, rounds)
        return hmac.compare_digest(original_hash, db_hash)
    except Exception:
        return False
