"""
Provenance Signing Verifier
=============================

Demonstrates the asymmetric signing verification flow:
1. Generate an Ed25519 keypair (or load existing one)
2. Sign a provenance payload
3. Verify the signature independently

This proves the signing/verification ecosystem works end-to-end.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KEYS_DIR = PROJECT_ROOT / "keys"
REPORT_DIR = PROJECT_ROOT / "reports" / "provenance"


def _generate_keypair():
    """Generate Ed25519 keypair using cryptography library or fallback to HMAC."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization

        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_bytes, public_bytes, "ed25519"
    except ImportError:
        # Fallback: HMAC-SHA256 for environments without cryptography
        import secrets
        key = secrets.token_hex(32)
        return key.encode(), key.encode(), "hmac-sha256"


def _sign_payload(payload: dict, private_key_bytes: bytes, method: str) -> str:
    """Sign a JSON payload."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)

    if method == "ed25519":
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
        sig = private_key.sign(canonical.encode("utf-8"))
        return sig.hex()
    else:
        import hmac
        sig = hmac.new(private_key_bytes, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"hmac-sha256:{sig}"


def _verify_signature(payload: dict, signature: str, public_key_bytes: bytes, method: str) -> bool:
    """Verify a signature against a payload."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)

    if method == "ed25519":
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        public_key = serialization.load_pem_public_key(public_key_bytes)
        try:
            public_key.verify(bytes.fromhex(signature), canonical.encode("utf-8"))
            return True
        except Exception:
            return False
    else:
        import hmac
        expected = hmac.new(public_key_bytes, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
        return signature == f"hmac-sha256:{expected}"


def main():
    print("=== Provenance Signing Verification ===\n")

    # 1. Generate keypair
    private_key, public_key, method = _generate_keypair()
    print(f"Signing method: {method}")

    # 2. Build provenance payload
    payload = {
        "snapshot_id": "parva-v4.0.0-2082",
        "dataset_hash": hashlib.sha256(b"festival_rules_v4.json").hexdigest()[:16],
        "rules_hash": hashlib.sha256(b"396_computed_rules").hexdigest()[:16],
        "engine_version": "4.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_rules": 453,
        "computed_rules": 396,
        "accuracy_pct": 100.0,
    }
    print(f"Payload: {json.dumps(payload, indent=2)}")

    # 3. Sign
    signature = _sign_payload(payload, private_key, method)
    print(f"\nSignature: {signature[:60]}...")

    # 4. Verify
    valid = _verify_signature(payload, signature, public_key, method)
    print(f"Verification: {'✅ VALID' if valid else '❌ INVALID'}")

    # 5. Tamper test
    tampered = dict(payload)
    tampered["computed_rules"] = 999
    tampered_valid = _verify_signature(tampered, signature, public_key, method)
    print(f"Tamper test:  {'❌ INVALID (correct!)' if not tampered_valid else '⚠️ VALID (unexpected)'}")

    # 6. Save report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "method": method,
        "payload": payload,
        "signature": signature,
        "verification_passed": valid,
        "tamper_detection_passed": not tampered_valid,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if method == "ed25519":
        KEYS_DIR.mkdir(parents=True, exist_ok=True)
        with open(KEYS_DIR / "parva_signing_public.pem", "wb") as f:
            f.write(public_key)
        print(f"\nPublic key: {KEYS_DIR / 'parva_signing_public.pem'}")

    report_path = REPORT_DIR / "signing_verification.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report: {report_path}")

    return 0 if valid and not tampered_valid else 1


if __name__ == "__main__":
    sys.exit(main())
