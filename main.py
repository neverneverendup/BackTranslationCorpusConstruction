#-*- coding:utf-8 -*-
from Translators import baidu, youdao, google
from config import param
import threading

if __name__=='__main__':

    from_lan = param['from_lan']
    to_lan = param['to_lan']
    corpus_file = param['data_file']

    bd = baidu.Baidu(from_lan, to_lan, trans_engine='百度', max_bytes_length=3000)
    yd = youdao.Youdao(from_lan, to_lan, trans_engine='有道', max_bytes_length=5000)
    gg = google.Google(from_lan, to_lan, trans_engine='谷歌', max_bytes_length=2000)

    t1 = threading.Thread(target=bd.run, args=())
    t2 = threading.Thread(target=yd.run, args=())
    t3 = threading.Thread(target=gg.run, args=())

    print('翻译启动')
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    print('翻译完毕')