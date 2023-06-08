import hashlib

class Hasher(object):
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def hash(str):
        # md5, sha1, sha224, sha256, sha384, sha512
        result = hashlib.sha1(str.encode()).hexdigest()
        return result

