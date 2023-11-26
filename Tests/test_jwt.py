import pytest
from datetime import datetime
import jwt
import paho.mqtt.client as mqtt
from publisher import on_connect

@pytest.fixture()
def test_gen_valid_token():
    # on_connect(client, userdata, flags, return_code)
    client = mqtt.Client(client_id="TestClient", userdata=None)
    on_connect(client, None, None, 0)
    return client.token.decode("utf-8")
@pytest.fixture
def test_token_decode(test_gen_valid_token):
    decoded = jwt.decode(jwt=test_gen_valid_token,
                         key='my-secret',
                         algorithms=["HS256"])
    return decoded

def test_decode_subject(test_token_decode):
    assert test_token_decode["sub"] == "client"

def test_decode_client(test_token_decode):
    assert test_token_decode["client"] == "TestClient"

def test_valid_token(test_token_decode):
    rightNow = datetime.now()
    expiry = datetime.fromtimestamp(test_token_decode["exp"])
    assert rightNow < expiry