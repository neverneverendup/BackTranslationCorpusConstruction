#-*- coding:utf-8 -*-

import time
import hashlib
import requests
import random
from .translator import Translator

class Youdao(Translator):

    def __init__(self,from_lan_id,to_lan_id,trans_engine,max_bytes_length):

        self.lan_dict={
            '中文':'zh-CHS',
            '英文': 'en',
            '俄文': 'ru',
            '法文': 'fr',
            '日文': 'ja',
            '韩文': 'ko'
            }
        super(Youdao, self).__init__(from_lan_id, to_lan_id, self.lan_dict, trans_engine,  max_bytes_length)

        self.s = requests.Session()
        self.s.keep_alive = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Referer': 'http://fanyi.youdao.com/',
            'contentType': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'OUTFOX_SEARCH_USER_ID=-352392290@116.136.20.84; P_INFO=a121bc; OUTFOX_SEARCH_USER_ID_NCOO=710017829.1902944; JSESSIONID=aaaDa3sqezCDY-snjj91w; SESSION_FROM_COOKIE=unknown; ___rl__test__cookies=' + str(
                int(time.time() * 1000)),
            # 'Connection': 'close'
        }
        self.url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'

    def translate(self,from_lan,to_lan,text):
        self.headers['Content-Length'] = str(233 + len(text))
        ts = str(int(time.time() * 1000))
        salf = ts + str(random.randint(0, 9))
        n = 'fanyideskweb' + text + salf + "n%A-rKaT5fb[Gy?;N5@Tj"
        self.m = hashlib.md5()
        self.m.update(n.encode('utf-8'))
        sign = self.m.hexdigest()
        data = {
            'i': text,
            'from': from_lan,
            'to': to_lan,
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salf,
            'sign': sign,
            'ts': ts,
            'bv': '53539dde41bde18f4a71bb075fcf2e66',
            'doctype': 'json',
            'version': "2.1",
            'keyfrom': "fanyi.web",
            'action': "FY_BY_REALTlME"
        }

        result = self.getHtml(self.s, self.url, self.headers, data,  is_post=True)
       # result = requests.post(url=self.url, data=data, headers=self.headers).json()
        if result != None:
            ans = []
            for c in result['translateResult']:
                ans.append(c[0]['tgt'])
            return ans
        else:
            self.logger.info('有道翻译失败')
            return None

if __name__ == '__main__':
    # 语种id对应关系 1: '中文', 2: '英文', 3: '日文', 6: '俄文'
    # aim_lan = [1,2,3,6]
    # aim_lan = [2]
    # for i in aim_lan:
    #     if i == 1:
    #         yd = Youdao(from_lan_id=i, to_lan_id=2,trans_engine='有道',max_bytes_length=3000)
    #         yd.run()
    #     else:
    #         yd = Youdao(from_lan_id=i,to_lan_id= 1,trans_engine='有道',max_bytes_length=3000)
    #         yd.run()
    #     del yd
    yd = Youdao(from_lan_id=1, to_lan_id=2, trans_engine='有道', max_bytes_length=3000)
    yd.translate('zh-CHS','ru','你好')