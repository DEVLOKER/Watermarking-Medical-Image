import os, sys
import base64, json

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# from Hasher import Hasher



class Crypter(object):

    #########################################################
    #               Constants
    #########################################################
    separator = '.'
    ALGORITHM_NONE, ALGORITHM_B64, ALGORITHM_AES, ALGORITHM_RSA = 0, 1, 2, 3

    #########################################################
    #               Constructor
    #########################################################

    def __init__(self, algorithm=2, key='#My_SickRat_Key#'):
        self.algorithm = algorithm
        match algorithm:
            case Crypter.ALGORITHM_NONE:
                pass
            case Crypter.ALGORITHM_B64:
                pass
            case Crypter.ALGORITHM_AES:
                self.key = key.encode('utf8') if key!=None else get_random_bytes(16)
            case Crypter.ALGORITHM_RSA:
                self.publicKey, self.privateKey = Crypter.generateKeys()
            case _:
                pass

    def encrypt(self, message):
        match self.algorithm:
            case Crypter.ALGORITHM_NONE:
                return message
            case Crypter.ALGORITHM_B64:
                return self.B64_encrypt(message)
            case Crypter.ALGORITHM_AES:
                return self.AES_encrypt(message)
            case Crypter.ALGORITHM_RSA:
                return self.RSA_encrypt(message)
            case _:
                return message

    def decrypt(self, encrypted_message):
        match self.algorithm:
            case Crypter.ALGORITHM_NONE:
                return encrypted_message
            case Crypter.ALGORITHM_B64:
                return self.B64_decrypt(encrypted_message)
            case Crypter.ALGORITHM_AES:
                return self.AES_decrypt(encrypted_message)
            case Crypter.ALGORITHM_RSA:
                return self.RSA_decrypt(encrypted_message)
            case _:
                return encrypted_message

    #########################################################
    #               No Encryption, just 64 coding
    #########################################################
    def B64_encrypt(self, message):
        try:
            return  base64.b64encode(message.encode()).decode()
        except Exception as e:
            return None
        
    def B64_decrypt(self, encrypted_message):
        try:
            return base64.b64decode(encrypted_message.encode()).decode()
        except Exception as e:
            return None

    #########################################################
    #               AES Encryption
    #########################################################
    def AES_encrypt(self, message):
        cipher = AES.new(self.key, AES.MODE_EAX)
        encrypted_message = cipher.encrypt(message.encode('utf8'))
        encrypted_message = base64.b64encode(encrypted_message).decode('utf8')
        nonce = base64.b64encode(cipher.nonce).decode('utf8')
        return f'{encrypted_message}{Crypter.separator}{nonce}'

    def AES_decrypt(self, encrypted_message):
        if Crypter.separator not in encrypted_message:
            return None
        try:
            encrypted_message, nonce = encrypted_message.split(Crypter.separator)
            encrypted_message = base64.b64decode(encrypted_message)
            nonce = base64.b64decode(nonce)
            cipher = AES.new(self.key, AES.MODE_EAX, nonce)
            decrypted_string = cipher.decrypt(encrypted_message)
            return decrypted_string.decode('utf-8')
        except Exception as e:
            return None
        
    #########################################################
    #               RSA Encryption
    #########################################################
    def RSA_encrypt(self, message):
        cipher = PKCS1_OAEP.new(self.publicKey)
        encrypted = cipher.encrypt(message.encode())
        encrypted = base64.b64encode(encrypted).decode()#'ascii'
        return encrypted

    def RSA_decrypt(self, encrypted_message):
        cipher = PKCS1_OAEP.new(self.privateKey)
        try:
            encrypted_message = base64.b64decode(encrypted_message)
            decrypted = cipher.decrypt(encrypted_message).decode()
            return decrypted
        except Exception as e:
            return None

    @staticmethod
    def generateKeys():
        publicKeyPath = os.path.join("src", "keys", "publicKey.pem")
        privateKeyPath = os.path.join("src", "keys", "privateKey.pem")
        if os.path.exists(publicKeyPath) and os.path.exists(privateKeyPath):
            publicKey, privateKey = Crypter.loadKeys(publicKeyPath, privateKeyPath)
            return publicKey, privateKey

        keys = RSA.generate(1024) # 2048
        publicKey = keys.publickey()
        with open(publicKeyPath, "w") as outfile:
            outfile.write(publicKey.exportKey('PEM').decode('ascii'))
        privateKey = keys.exportKey()
        with open(privateKeyPath, "w") as outfile:
            outfile.write(keys.exportKey('PEM').decode('ascii'))
        return publicKey, privateKey

    @staticmethod
    def loadKeys(publicKeyPath, privateKeyPath):
        with open(publicKeyPath, 'rb') as outfile:
            publicKey = RSA.importKey(outfile.read())
        with open(privateKeyPath, 'rb') as outfile:
            privateKey = RSA.importKey(outfile.read())
        return publicKey, privateKey



"""
# data = { "name": "devloker", "date": "07-21-1990" }
# data = [ "devloker", "30", "seatle" ]
data = [ f'{Hasher.hash("AE4569")}', "dev", "loker", "30", "m", "clinic01"]
message = 'secret data'#.rjust(32)
data_type = type(data).__name__
if(data_type=="dict"):
    message = json.dumps(data, indent=0)
if(data_type=="list"):
    message = ','.join(data)
# key = '1234567890123456'
key = '#My_SickRat_Key#'

print("Original message:", message)

encrypted_message = Crypter(key).encrypt(message)
print("Encrypted String:", encrypted_message)

decrypted_string = Crypter(key).decrypt(encrypted_message)
print("Decrypted String:", decrypted_string)


"""





"""
# data = { "name": "devloker", "date": "07-21-1990" }
# data = [ "devloker", "30", "seatle" ]
data = [ "dev", "loker", "30", "m", "clinic01", "AE4569"]
# message = 'secret data'#.rjust(32)
data_type = type(data).__name__
if(data_type=="dict"):
    message = json.dumps(data, indent=0)
if(data_type=="list"):
    message = ','.join(data)

# message = 'This is your secret'


crypter = Crypter()

encrypted = crypter.encrypt(message)
print("\nEncrypted:", encrypted)
decrypted = crypter.decrypt(encrypted)
print('\nDecrypted:', decrypted)

"""