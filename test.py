import datetime
import base64
from cryptography.fernet import Fernet

# class EmailAuthenticateToken(models.Model):

#     def __init__(self, user):
#         self.user = user
#         self.key = Fernet.generate_key()
#         self.date_created = datetime.datetime.now()
#         self.byte_values = bytes(str(user.__string__) +
#                                  str(self.date_created), 'utf-8')
#         self.encoded = Fernet(self.key).encrypt(byte_values)
#         self.encoded_string = base64.b64encode(self.encoded)

#     def get_token(self):
#         return encoded_string


key = Fernet.generate_key()
print(key)
some_bytes = bytes("User" + str(datetime.datetime.now()), 'utf-8')
print(some_bytes)
encoded_bytes = Fernet(key).encrypt(some_bytes)
print(encoded_bytes)
base64_bytes = base64.b64encode(encoded_bytes)
print(base64_bytes)
