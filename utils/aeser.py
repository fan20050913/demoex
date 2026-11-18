import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        # 密钥用sha256固定32字节
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        b64_str = base64.b64encode(iv + cipher.encrypt(raw.encode())).decode('utf-8')
        # URL安全base64
        url_safe = b64_str.replace("+", "-").replace("/", "_").rstrip("=")
        return url_safe

    def decrypt(self, enc):
        # 还原url安全字符
        enc = enc.replace("-", "+").replace("_", "/")
        # 补齐base64等号
        pad_len = (4 - len(enc) % 4) % 4
        enc += "=" * pad_len
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        pad = self.bs - len(s) % self.bs
        return s + pad * chr(pad)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


# 测试示例
if __name__ == '__main__':
    aes = AESCipher("123456")
    txt = "hello OA系统"
    res = aes.encrypt(txt)
    print("加密结果：", res)
    print("解密结果：", aes.decrypt(res))
