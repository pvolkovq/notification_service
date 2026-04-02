import base64
import json
from typing import Union

from Crypto.Cipher import AES

from app.core.config import mac_len, nonce, public_link_secret_key


def encrypt_data(data: Union[dict[any], str]) -> str:
    if not isinstance(data, str):
        data = json.dumps(data)
    cipher = AES.new(public_link_secret_key, AES.MODE_GCM, nonce=nonce, mac_len=mac_len)
    encrypted_value, tag = cipher.encrypt_and_digest(data.encode("utf-8"))
    ciphertext = cipher.nonce + encrypted_value + tag
    encoded_encrypted_value = base64.urlsafe_b64encode(ciphertext).decode("utf-8")
    return encoded_encrypted_value


def decrypt_data(value: str):
    decoded_value = base64.urlsafe_b64decode(value.encode("utf-8"))
    encrypted_value = decoded_value[:-16][12:]
    cipher2 = AES.new(public_link_secret_key, AES.MODE_GCM, nonce=nonce)
    decrypted_value = cipher2.decrypt(encrypted_value)
    return decrypted_value.decode("utf-8")
