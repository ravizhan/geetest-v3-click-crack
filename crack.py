import hashlib
import json
import math
import random
import time

import httpx
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15


class Crack:
    def __init__(self, gt=None, challenge=None):
        self.pic_path = None
        self.s = None
        self.c = None
        self.session = httpx.Client(http2=True)
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        # self.session.verify = False
        self.gt = gt
        self.challenge = challenge
        self.aeskey = ''.join(f'{int((1 + random.random()) * 65536):04x}'[1:] for _ in range(4))
        public_key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDB45NNFhRGWzMFPn9I7k7IexS5
XviJR3E9Je7L/350x5d9AtwdlFH3ndXRwQwprLaptNb7fQoCebZxnhdyVl8Jr2J3
FZGSIa75GJnK4IwNaG10iyCjYDviMYymvCtZcGWSqSGdC/Bcn2UCOiHSMwgHJSrg
Bm1Zzu+l8nSOqAurgQIDAQAB
-----END PUBLIC KEY-----'''
        self.public_key = serialization.load_pem_public_key(public_key.encode())
        self.enc_key = self.public_key.encrypt(self.aeskey.encode(), PKCS1v15()).hex()
        with open("mousepath.json", "r") as f:
            self.mouse_path = json.loads(f.read())

    def get_type(self) -> dict:
        url = f"https://api.geetest.com/gettype.php?gt={self.gt}"
        res = self.session.get(url)
        return json.loads(res.text[1:-1])["data"]

    @staticmethod
    def encode(input_bytes: list):
        def get_char_from_index(index):
            char_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()"
            return char_table[index] if 0 <= index < len(char_table) else "."

        def transform_value(value, bit_mask):
            result = 0
            for r in range(23, -1, -1):
                if (bit_mask >> r) & 1:
                    result = (result << 1) + ((value >> r) & 1)
            return result

        encoded_string = ""
        padding = ""
        input_length = len(input_bytes)
        for i in range(0, input_length, 3):
            chunk_length = min(3, input_length - i)
            chunk = input_bytes[i:i + chunk_length]
            if chunk_length == 3:
                value = (chunk[0] << 16) + (chunk[1] << 8) + chunk[2]
                encoded_string += get_char_from_index(transform_value(value, 7274496)) + get_char_from_index(
                    transform_value(value, 9483264)) + get_char_from_index(
                    transform_value(value, 19220)) + get_char_from_index(transform_value(value, 235))
            elif chunk_length == 2:
                value = (chunk[0] << 16) + (chunk[1] << 8)
                encoded_string += get_char_from_index(transform_value(value, 7274496)) + get_char_from_index(
                    transform_value(value, 9483264)) + get_char_from_index(transform_value(value, 19220))
                padding = "."
            elif chunk_length == 1:
                value = chunk[0] << 16
                encoded_string += get_char_from_index(transform_value(value, 7274496)) + get_char_from_index(
                    transform_value(value, 9483264))
                padding = ".."
        return encoded_string + padding

    @staticmethod
    def MD5(text: str):
        return hashlib.md5(text.encode()).hexdigest()

    @staticmethod
    def encode_mouse_path(path: list, c: list, s: str):
        def preprocess(path: list):
            def BFIQ(e):
                t = 32767
                if not isinstance(e, int):
                    return e
                else:
                    if t < e:
                        e = t
                    elif e < -t:
                        e = -t
                return round(e)

            def BGAB(e):
                t = ''
                n = 0
                len(e or [])
                while n < len(e) and not t:
                    if e[n]:
                        t = e[n][4]
                    n += 1
                if not t:
                    return e
                r = ''
                i = ['mouse', 'touch', 'pointer', 'MSPointer']
                for s in range(len(i)):
                    if t.startswith(i[s]):
                        r = i[s]
                _ = list(e)
                for a in range(len(_) - 1, -1, -1):
                    c = _[a]
                    l = c[0]
                    if l in ['move', 'down', 'up']:
                        value = c[4] or ''
                        if not value.startswith(r):
                            _.pop(a)
                return _

            t = 0
            n = 0
            r = []
            s = 0
            if len(path) <= 0:
                return []
            o = None
            _ = None
            a = BGAB(path)
            c = len(a)
            for l in range(0 if c < 300 else c - 300, c):
                u = a[l]
                h = u[0]
                if h in ['down', 'move', 'up', 'scroll']:
                    if not o:
                        o = u
                    _ = u
                    r.append([h, [u[1] - t, u[2] - n], BFIQ(u[3] - s if s else s)])
                    t = u[1]
                    n = u[2]
                    s = u[3]
                elif h in ['blur', 'focus', 'unload']:
                    r.append([h, BFIQ(u[1] - s if s else s)])
                    s = u[1]
            return r

        def process(prepared_path: list):
            h = {
                'move': 0,
                'down': 1,
                'up': 2,
                'scroll': 3,
                'focus': 4,
                'blur': 5,
                'unload': 6,
                'unknown': 7
            }

            def p(e, t):
                n = bin(e)[2:]
                r = ''
                i = len(n) + 1
                while i <= t:
                    i += 1
                    r += '0'
                return r + n

            def d(e):
                t = []
                n = len(e)
                r = 0
                while r < n:
                    i = e[r]
                    s = 0
                    while True:
                        if s >= 16:
                            break
                        o = r + s + 1
                        if o >= n:
                            break
                        if e[o] != i:
                            break
                        s += 1
                    r += 1 + s
                    _ = h[i]
                    if s != 0:
                        t.append(_ | 8)
                        t.append(s - 1)
                    else:
                        t.append(_)
                a = p(n | 32768, 16)
                c = ''
                for l in range(len(t)):
                    c += p(t[l], 4)
                return a + c

            def g(e, tt):
                def temp1(e1):
                    n = len(e)
                    r = 0
                    i = []
                    while r < n:
                        s = 1
                        o = e[r]
                        _ = abs(o)
                        while True:
                            if n <= r + s:
                                break
                            if e[r + s] != o:
                                break
                            if (_ >= 127) or (s >= 127):
                                break
                            s += 1
                        if s > 1:
                            i.append((49152 if o < 0 else 32768) | s << 7 | _)
                        else:
                            i.append(o)
                        r += s
                    return i

                e = temp1(e)

                r = []
                i = []

                def n(e, t):
                    return 0 if e == 0 else math.log(e) / math.log(t)

                for temp in e:
                    t = math.ceil(n(abs(temp) + 1, 16))
                    if t == 0:
                        t = 1
                    r.append(p(t - 1, 2))
                    i.append(p(abs(temp), t * 4))

                s = ''.join(r)
                o = ''.join(i)

                def temp2(t):
                    return t != 0 and t >> 15 != 1

                def temp3(e1):
                    n = []

                    def temp(e2):
                        if temp2(e2):
                            n.append(e2)

                    for r in range(len(e1)):
                        temp(e1[r])
                    return n

                def temp4(t):
                    if t < 0:
                        return '1'
                    else:
                        return '0'

                if tt:
                    n = []
                    e1 = temp3(e)
                    for r in range(len(e1)):
                        n.append(temp4(e1[r]))
                    n = ''.join(n)
                else:
                    n = ''
                return p(len(e) | 32768, 16) + s + o + n

            def u(e):
                t = ''
                n = len(e) // 6
                for r in range(n):
                    t += '()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~'[
                        int(e[6 * r: 6 * (r + 1)], 2)]
                return t

            t = []
            n = []
            r = []
            i = []
            for a in range(len(prepared_path)):
                _ = prepared_path[a]
                a = len(_)
                t.append(_[0])
                n.append(_[1] if a == 2 else _[2])
                if a == 3:
                    r.append(_[1][0])
                    i.append(_[1][1])
            c = d(t) + g(n, False) + g(r, True) + g(i, True)
            l = len(c)
            if l % 6 != 0:
                c += p(0, 6 - l % 6)
            return u(c)

        def postprocess(e, t, n):
            i = 0
            s = e
            o = t[0]
            _ = t[2]
            a = t[4]
            while True:
                r = n[i:i + 2]
                if not r:
                    break
                i += 2
                c = int(r, 16)
                l = chr(c)
                u = (o * c * c + _ * c + a) % len(e)
                s = s[:u] + l + s[u:]
            return s

        return postprocess(process(preprocess(path)), c, s)

    def aes_encrypt(self, content: str):
        cipher = Cipher(algorithms.AES(self.aeskey.encode()), modes.CBC(b"0000000000000000"))
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(content.encode())
        padded_data += padder.finalize()
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return ct

    def get_c_s(self):
        o = {
            "gt": self.gt,
            "challenge": self.challenge,
            "offline": False,
            "new_captcha": True,
            "product": "embed",
            "width": "300px",
            "https": True,
            "protocol": "https://",
        }
        o.update(self.get_type())
        o.update({
            "cc": 16,
            "ww": True,
            "i": "-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1"
        })
        o = json.dumps(o, separators=(',', ':'))
        # print(o)
        ct = self.aes_encrypt(o)
        s = []
        for byte in ct:
            s.append(byte)
        i = self.encode(s)
        r = self.enc_key
        w = i + r
        params = {
            "gt": self.gt,
            "challenge": self.challenge,
            "lang": "zh-cn",
            "pt": 0,
            "client_type": "web",
            "callback": "geetest_" + str(int(round(time.time() * 1000))),
            "w": w
        }
        resp = self.session.get("https://api.geetest.com/get.php", params=params).text
        # print(resp)
        data = json.loads(resp[22:-1])["data"]
        self.c = data["c"]
        self.s = data["s"]
        return data["c"], data["s"]

    def gettype(self):
        url = f"https://api.geetest.com/gettype.php?gt={self.gt}&callback=geetest_{str(int(round(time.time() * 1000)))}"
        return self.session.get(url).text

    def ajax(self):
        def transform(e, t, n):
            if not t or not n:
                return e
            o = 0
            i = list(e)
            s = t[0]
            a = t[2]
            b = t[4]
            while o < len(n):
                r = n[o:o + 2]
                o += 2
                c = int(r, 16)
                l = chr(c)
                u = (s * c * c + a * c + b) % len(i)
                i.insert(u, l)
            return ''.join(i)

        mouse_path = [
            ["move", 385, 313, 1724572150164, "pointermove"],
            ["move", 385, 315, 1724572150166, "pointermove"],
            ["move", 386, 315, 1724572150174, "pointermove"],
            ["move", 387, 315, 1724572150182, "pointermove"],
            ["move", 387, 316, 1724572150188, "pointermove"],
            ["move", 388, 316, 1724572150204, "pointermove"],
            ["move", 388, 317, 1724572150218, "pointermove"],
            ["down", 388, 317, 1724572150586, "pointerdown"],
            ["focus", 1724572150587],
            ["up", 388, 317, 1724572150632, "pointerup"]
        ]
        tt = transform(self.encode_mouse_path(mouse_path, self.c, self.s), self.c, self.s)
        rp = self.MD5(self.gt + self.challenge + self.s)
        temp1 = '''"lang":"zh-cn","type":"fullpage","tt":"%s","light":"DIV_0","s":"c7c3e21112fe4f741921cb3e4ff9f7cb","h":"321f9af1e098233dbd03f250fd2b5e21","hh":"39bd9cad9e425c3a8f51610fd506e3b3","hi":"09eb21b3ae9542a9bc1e8b63b3d9a467","vip_order":-1,"ct":-1,"ep":{"v":"9.1.9-dbjg5z","te":false,"me":true,"ven":"Google Inc. (Intel)","ren":"ANGLE (Intel, Intel(R) Iris(R) Xe Graphics (0x0000A7A0) Direct3D11 vs_5_0 ps_5_0, D3D11)","fp":["scroll",0,1602,1724571628498,null],"lp":["up",386,217,1724571629854,"pointerup"],"em":{"ph":0,"cp":0,"ek":"11","wd":1,"nt":0,"si":0,"sc":0},"tm":{"a":1724571567311,"b":1724571567549,"c":1724571567562,"d":0,"e":0,"f":1724571567312,"g":1724571567312,"h":1724571567312,"i":1724571567317,"j":1724571567423,"k":1724571567330,"l":1724571567423,"m":1724571567545,"n":1724571567547,"o":1724571567569,"p":1724571568259,"q":1724571568259,"r":1724571568261,"s":1724571570378,"t":1724571570378,"u":1724571570380},"dnf":"dnf","by":0},"passtime":1600,"rp":"%s",''' % (
            tt, rp)
        r = "{" + temp1 + '"captcha_token":"1198034057","du6o":"eyjf7nne"}'
        # print(r)
        ct = self.aes_encrypt(r)
        s = [byte for byte in ct]
        w = self.encode(s)
        params = {
            "gt": self.gt,
            "challenge": self.challenge,
            "lang": "zh-cn",
            "pt": 0,
            "client_type": "web",
            "callback": "geetest_" + str(int(round(time.time() * 1000))),
            "w": w
        }
        resp = self.session.get("https://api.geetest.com/ajax.php", params=params).text
        return json.loads(resp[22:-1])["data"]

    def get_pic(self,retry=0):
        params = {
            "type": "click",
            "gt": self.gt,
            "challenge": self.challenge,
            "lang": "zh-cn",
            "callback": "geetest_" + str(int(round(time.time() * 1000))),
        }
        if retry == 0:
            url = "https://api.geevisit.com/get.php"
            params.update(
                {
                    "is_next": "true",
                    "https": "true",
                    "protocol": "https://",
                    "offline": "false",
                    "product": "float",
                    "api_server": "api.geevisit.com",
                    "isPC": True,
                    "autoReset": True,
                    "width": "100%",
                }
            )
        else:
            url = "https://api.geetest.com/refresh.php"
        resp = self.session.get(url, params=params).text
        data = json.loads(resp[22:-1])["data"]
        self.pic_path = data["pic"]
        pic_url = "https://" + data["image_servers"][0][:-1] + data["pic"]
        return self.session.get(pic_url).content

    def verify(self, points: list):
        u = self.enc_key
        o = {
            "lang": "zh-cn",
            "passtime": 1600,
            "a": ",".join(points),
            "pic": self.pic_path,
            "tt": self.encode_mouse_path(self.mouse_path, self.c, self.s),
            "ep": {
                "ca": [{"x": 524, "y": 209, "t": 0, "dt": 1819}, {"x": 558, "y": 299, "t": 0, "dt": 428},
                       {"x": 563, "y": 95, "t": 0, "dt": 952}, {"x": 670, "y": 407, "t": 3, "dt": 892}],
                "v": '3.1.0',
                "$_FB": False,
                "me": True,
                "tm": {"a": 1724585496403, "b": 1724585496605, "c": 1724585496613, "d": 0, "e": 0, "f": 1724585496404,
                       "g": 1724585496404, "h": 1724585496404, "i": 1724585496404, "j": 1724585496404, "k": 0,
                       "l": 1724585496413, "m": 1724585496601, "n": 1724585496603, "o": 1724585496618,
                       "p": 1724585496749, "q": 1724585496749, "r": 1724585496751, "s": 1724585498068,
                       "t": 1724585498068, "u": 1724585498069}
            },
            "h9s9": "1816378497",
        }
        o["rp"] = self.MD5(self.gt + self.challenge + str(o["passtime"]))
        o = json.dumps(o, separators=(',', ':'))
        # print(o)
        ct = self.aes_encrypt(o)
        s = []
        for byte in ct:
            s.append(byte)
        p = self.encode(s)
        w = p + u
        params = {
            "gt": self.gt,
            "challenge": self.challenge,
            "lang": "zh-cn",
            "pt": 0,
            "client_type": "web",
            "w": w
        }
        resp = self.session.get("https://api.geevisit.com/ajax.php", params=params).text
        return resp[1:-1]
