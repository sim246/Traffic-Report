import pytest
from asymetric_keys import sign, verify
from pathlib import Path
from cryptography.hazmat.primitives import serialization

@pytest.fixture
def read_keys_from_files():
    try:
        private_pem_bytes = Path("./private_key.pem").read_bytes()
        public_pem_bytes = Path("./public_key.pem").read_bytes()
        
        private_key_from_pem = serialization.load_pem_private_key(
            private_pem_bytes,
            password=b"my secret",
        )
        public_key_from_pem = serialization.load_pem_public_key(public_pem_bytes)
        
        return private_key_from_pem, public_key_from_pem
    except ValueError:
        print("Incorrect Password")

def test_sign_returns_signature(read_keys_from_files):
    signature = sign(b"a message", read_keys_from_files[0])
    
    assert signature is not None

def test_verify_correct(read_keys_from_files):
    signature = sign(b"a message", read_keys_from_files[0])
    
    verify_result = verify(signature, b"a message", read_keys_from_files[1])
    
    assert verify_result == "The message has been successfully verified"

def test_verify_incorrect_signature(read_keys_from_files):
    verify_result = verify(b'not the signature', b"a message", read_keys_from_files[1])
    
    assert verify_result == "The signature, the message or the Public Key is invalid"

def test_verify_incorrect_message(read_keys_from_files):
    signature = sign(b"wrong message", read_keys_from_files[0])
    
    verify_result = verify(signature, b"a message", read_keys_from_files[1])
    
    assert verify_result == "The signature, the message or the Public Key is invalid"
