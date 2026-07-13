from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hashing_roundtrip():
    password = "ComplexPass@123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_access_token_contains_type_and_subject():
    token = create_access_token("user-1")
    payload = decode_token(token)
    assert payload["sub"] == "user-1"
    assert payload["type"] == "access"
    assert "jti" in payload
