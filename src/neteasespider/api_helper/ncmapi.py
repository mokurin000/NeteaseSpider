#!/usr/bin/env python
# encoding: UTF-8

import base64
import binascii
import hashlib
import os
import json
import logging

import requests
from cachier import cachier
from Crypto.Cipher import AES


site_uri = "http://music.163.com"
uri = "http://music.163.com/api"
uri_we = "http://music.163.com/weapi"
uri_v1 = "http://music.163.com/weapi/v1"
uri_v3 = "http://music.163.com/weapi/v3"
uri_e = "https://music.163.com/eapi"

logger = logging.getLogger(__name__)


class CodeShouldBe200(Exception):
    def __init__(self, data):
        self._code = data["code"]
        self._data = data

    def __str__(self):
        return f"json code field should be 200, got {self._code}. data: {self._data}"


class API(object):
    def __init__(self):
        super().__init__()
        self.headers = {
            "Host": "music.163.com",
            "Connection": "keep-alive",
            "Referer": "http://music.163.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/33.0.1750.152 Safari/537.36",
        }
        self._cookies = dict(appver="1.2.1", os="osx")
        self._http = None

    @property
    def cookies(self):
        return self._cookies

    def load_cookies(self, cookies):
        self._cookies.update(cookies)
        # 云盘资源发布仅有似乎不支持osx平台
        self._cookies.update(dict(appver="7.2.24", os="android"))

    def set_http(self, http):
        self._http = http

    @property
    def http(self):
        return requests if self._http is None else self._http

    def request(self, method, action, query=None, timeout=2):
        # logger.info('method=%s url=%s data=%s' % (method, action, query))
        if method == "GET":
            res = self.http.get(
                action, headers=self.headers, cookies=self._cookies, timeout=timeout
            )
        elif method == "POST":
            res = self.http.post(
                action,
                data=query,
                headers=self.headers,
                cookies=self._cookies,
                timeout=timeout,
            )
        elif method == "POST_UPDATE":
            res = self.http.post(
                action,
                data=query,
                headers=self.headers,
                cookies=self._cookies,
                timeout=timeout,
            )
            self._cookies.update(res.cookies.get_dict())
        content = res.content
        content_str = content.decode("utf-8")
        content_dict = json.loads(content_str)
        return content_dict

    @cachier()
    def playlist_detail_v3(self, pid, offset=0, limit=200):
        """
        该接口返回的 ['playlist']['trackIds'] 字段会包含所有的歌曲
        """
        action = "/playlist/detail"
        url = uri_v3 + action
        data = dict(id=pid, limit=limit, offset=offset, n=limit)
        payload = self.encrypt_request(data)
        res_data = self.request("POST", url, payload)
        if res_data["code"] == 200:
            return res_data["playlist"]
        raise CodeShouldBe200(res_data)

    @cachier()
    def song_detail(self, music_id):
        action = (
            uri + "/song/detail/?id=" + str(music_id) + "&ids=[" + str(music_id) + "]"
        )
        data = self.request("GET", action)
        if data["code"] == 200:
            if data["songs"]:
                return data["songs"][0]
            return
        raise CodeShouldBe200(data)

    def _create_aes_key(self, size):
        return ("".join([hex(b)[2:] for b in os.urandom(size)]))[0:16]

    def _aes_encrypt(self, text, key):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(bytes(key, "utf-8"), 2, b"0102030405060708")
        enc_text = encryptor.encrypt(bytes(text, "utf-8"))
        enc_text_encode = base64.b64encode(enc_text)
        return enc_text_encode

    def _rsa_encrypt(self, text):
        e = "010001"
        n = (
            "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615"
            "bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf"
            "695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46"
            "bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b"
            "8e289dc6935b3ece0462db0a22b8e7"
        )
        reverse_text = text[::-1]
        encrypted_text = pow(
            int(binascii.hexlify(reverse_text), 16), int(e, 16), int(n, 16)
        )
        return format(encrypted_text, "x").zfill(256)

    def eapi_encrypt(self, path, params):
        """
        eapi接口参数加密
        :param bytes path: 请求的路径
        :param params: 请求参数
        :return str: 加密结果
        """
        params = json.dumps(params, separators=(",", ":")).encode()
        sign_src = b"nobody" + path + b"use" + params + b"md5forencrypt"
        m = hashlib.md5()
        m.update(sign_src)
        sign = m.hexdigest()
        aes_src = path + b"-36cd479b6b5-" + params + b"-36cd479b6b5-" + sign.encode()
        pad = 16 - len(aes_src) % 16
        aes_src = aes_src + bytearray([pad] * pad)
        crypt = AES.new(b"e82ckenh8dichen8", AES.MODE_ECB)
        ret = crypt.encrypt(aes_src)
        return binascii.b2a_hex(ret).upper()

    def encrypt_request(self, data):
        text = json.dumps(data)
        first_aes_key = "0CoJUm6Qyw8W8jud"
        second_aes_key = self._create_aes_key(16)
        enc_text = self._aes_encrypt(
            self._aes_encrypt(text, first_aes_key).decode("ascii"), second_aes_key
        ).decode("ascii")
        enc_aes_key = self._rsa_encrypt(second_aes_key.encode("ascii"))
        payload = {
            "params": enc_text,
            "encSecKey": enc_aes_key,
        }
        return payload


ncmapi = API()
