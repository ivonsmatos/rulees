"""
BYOK service — envelope encryption com chave do cliente.

Padrão: AES-256-GCM para cifrar dados (DEK), XOR/PBKDF2 para cifrar DEK com KEK local.
Em produção real com AWS KMS: usar boto3.kms.encrypt/decrypt.

Dependência opcional: cryptography (add a requirements.txt).
"""

import base64
import os
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.byok.models import CustomerKey

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # type: ignore
    from cryptography.hazmat.primitives import hashes  # type: ignore
    _HAS_CRYPTOGRAPHY = True
except ImportError:
    _HAS_CRYPTOGRAPHY = False


# ── Key derivation (local mode) ───────────────────────────────────────────────

def _derive_key(master_key: bytes, salt: bytes) -> bytes:
    """Deriva uma chave AES-256 a partir de uma KEK master usando PBKDF2."""
    if _HAS_CRYPTOGRAPHY:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100_000)
        return kdf.derive(master_key)
    # fallback determinístico (não usar em produção sem cryptography)
    import hashlib
    return hashlib.pbkdf2_hmac("sha256", master_key, salt, 100_000, dklen=32)


def _aes_gcm_encrypt(key: bytes, plaintext: bytes) -> bytes:
    """AES-256-GCM: retorna nonce(12) + ciphertext+tag."""
    if _HAS_CRYPTOGRAPHY:
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ct = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ct
    # sem cryptography: XOR simples (DEMO ONLY — NÃO É SEGURO)
    nonce = os.urandom(12)
    import hashlib
    keystream = hashlib.sha256(key + nonce).digest()
    ct = bytes(b ^ keystream[i % 32] for i, b in enumerate(plaintext))
    return nonce + ct


def _aes_gcm_decrypt(key: bytes, data: bytes) -> bytes:
    nonce, ciphertext = data[:12], data[12:]
    if _HAS_CRYPTOGRAPHY:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    import hashlib
    keystream = hashlib.sha256(key + nonce).digest()
    return bytes(b ^ keystream[i % 32] for i, b in enumerate(ciphertext))


# ── CustomerKey CRUD ──────────────────────────────────────────────────────────

def provision_customer_key(
    db: Session,
    *,
    tenant_id: str,
    created_by: str,
    kms_provider: str = "local",
    kms_key_arn: str | None = None,
    key_label: str = "primary",
    master_key_b64: str | None = None,
) -> CustomerKey:
    """
    Provisiona BYOK para o tenant.
    Gera DEK aleatório, cifra com KEK e armazena encrypted_dek.
    """
    existing = db.query(CustomerKey).filter(
        CustomerKey.tenant_id == tenant_id,
        CustomerKey.is_active == True,  # noqa: E712
    ).first()
    if existing:
        return existing

    # Gera DEK
    dek = os.urandom(32)

    if kms_provider == "local":
        if not master_key_b64:
            raise ValueError("master_key_b64 obrigatório para provider 'local'")
        master = base64.b64decode(master_key_b64)
        salt = os.urandom(16)
        kek = _derive_key(master, salt)
        encrypted = _aes_gcm_encrypt(kek, dek)
        # armazena: salt(16) + encrypted
        payload = base64.b64encode(salt + encrypted).decode()
    else:
        # Para AWS/GCP/Azure: chamar SDK externo aqui
        # ex: boto3.client("kms").encrypt(KeyId=kms_key_arn, Plaintext=dek)
        # Stub para interface:
        payload = base64.b64encode(dek).decode() + ":kms_stub"

    ck = CustomerKey(
        tenant_id=tenant_id,
        kms_provider=kms_provider,
        kms_key_arn=kms_key_arn,
        encrypted_dek=payload,
        key_label=key_label,
        created_by=created_by,
    )
    db.add(ck)
    db.flush()
    return ck


def get_customer_key(db: Session, *, tenant_id: str) -> CustomerKey | None:
    return db.query(CustomerKey).filter(
        CustomerKey.tenant_id == tenant_id,
        CustomerKey.is_active == True,  # noqa: E712
    ).first()


def encrypt_for_tenant(
    db: Session,
    *,
    tenant_id: str,
    plaintext: str,
    master_key_b64: str,
) -> str:
    """Cifra plaintext com a DEK do tenant. Retorna base64."""
    ck = get_customer_key(db, tenant_id=tenant_id)
    if ck is None:
        raise ValueError("BYOK não configurado para este tenant")
    dek = _recover_dek(ck, master_key_b64)
    ct = _aes_gcm_encrypt(dek, plaintext.encode())
    return base64.b64encode(ct).decode()


def decrypt_for_tenant(
    db: Session,
    *,
    tenant_id: str,
    ciphertext_b64: str,
    master_key_b64: str,
) -> str:
    """Decifra ciphertext_b64 com a DEK do tenant. Retorna plaintext."""
    ck = get_customer_key(db, tenant_id=tenant_id)
    if ck is None:
        raise ValueError("BYOK não configurado para este tenant")
    dek = _recover_dek(ck, master_key_b64)
    ct = base64.b64decode(ciphertext_b64)
    return _aes_gcm_decrypt(dek, ct).decode()


def _recover_dek(ck: CustomerKey, master_key_b64: str) -> bytes:
    if ck.kms_provider == "local":
        raw = base64.b64decode(ck.encrypted_dek)
        salt, encrypted = raw[:16], raw[16:]
        master = base64.b64decode(master_key_b64)
        kek = _derive_key(master, salt)
        return _aes_gcm_decrypt(kek, encrypted)
    # KMS externo: stub
    raise NotImplementedError(f"KMS provider '{ck.kms_provider}' requer SDK externo")


def rotate_key(
    db: Session,
    *,
    tenant_id: str,
    old_master_key_b64: str,
    new_master_key_b64: str,
) -> CustomerKey:
    """Rotação de chave: re-cifra DEK com nova KEK."""
    ck = get_customer_key(db, tenant_id=tenant_id)
    if ck is None:
        raise ValueError("BYOK não configurado para este tenant")
    dek = _recover_dek(ck, old_master_key_b64)

    new_salt = os.urandom(16)
    new_master = base64.b64decode(new_master_key_b64)
    new_kek = _derive_key(new_master, new_salt)
    new_encrypted = _aes_gcm_encrypt(new_kek, dek)
    ck.encrypted_dek = base64.b64encode(new_salt + new_encrypted).decode()
    ck.rotated_at = datetime.now(timezone.utc)
    db.add(ck)
    return ck
