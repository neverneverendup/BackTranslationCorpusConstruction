#-*- coding:utf-8 -*-
import requests
import time
from config import param

def get_proxy():
    return requests.session.get("http://127.0.0.1:60001/get/").json()

def delete_proxy(proxy):
    requests.session.get("http://127.0.0.1:60001/delete/?proxy={}".format(proxy))

def get_html(logger, session, url, headers, data, is_post=True):
    try:
        if is_post:
            html = session.post(url, headers=headers, data=data, timeout=5)
        else:
            html = session.get(url, headers=headers, timeout=3)
        return html.json()
    except Exception as e:
        logger.info('出错 :' + str(e))
        return None

def get_html_use_proxy(logger, session, url, headers, data, is_post=True):
    while True:
        # 获取代理
        while True:
            try:
                proxy = get_proxy().get("proxy")
                if proxy != None:
                    logger.info('进程得到IP：' + proxy)
                    break
                else:
                    exit(0)
            except Exception as e:
                logger.info('未获得代理，进程退出')
                exit(0)
        try:
            if is_post:
                html = session.post(url, headers=headers, data=data, proxies={"http": "http://{}".format(proxy)}, timeout=8)
                print('ok')
            else:
                html = session.get(url, headers=headers, proxies={"http": "http://{}".format(proxy)}, timeout=3)
            return html.json()
        except Exception as e:
            logger.info(' 翻译出错 :' + str(e))
            return None

def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# 加载待翻译语料
def load_corpus():
    corpus = []
    data_file = param['data_file']
    with open(data_file,encoding='utf-8')as f:
        for idx, text in enumerate(f):
            corpus.append((idx, text.strip()))
    #print(corpus)
    return corpus

def long_sens_genrator(self, sens,max_length):
    ss = ''
    bytes_len = 0
    index = 0
    cid_str = ''
    slid_str = ''

    while index < len(sens):
        local_len = len(sens[index][1].encode())
        if ss == '' and local_len > max_length - 10:
            index += 1
            continue

        if bytes_len + local_len < max_length:
            ss += sens[index][1] + '\n'
            cid_str += str(sens[index][0]) + ','
            bytes_len += local_len
        else:
            yield cid_str,ss
            index -= 1

            bytes_len = 0
            ss = ''
            cid_str = ''

        index += 1
    yield  cid_str, ss