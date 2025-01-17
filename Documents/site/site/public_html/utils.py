from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def get_encryption_key():
    # Используем секретный ключ из конфигурации
    salt = b'salt_'  # В продакшене используйте случайную соль
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(os.getenv('SECRET_KEY', 'default_key').encode()))
    return Fernet(key)

def encrypt_ip(ip_address):
    if not ip_address:
        return None
    f = get_encryption_key()
    return f.encrypt(ip_address.encode()).decode()

def decrypt_ip(encrypted_ip):
    if not encrypted_ip:
        return None
    f = get_encryption_key()
    return f.decrypt(encrypted_ip.encode()).decode() 