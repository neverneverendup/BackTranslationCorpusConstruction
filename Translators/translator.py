#-*- coding:utf-8 -*-
import requests
import time
import logging
from config import param
from .utils import get_now_time, get_html, get_html_use_proxy, long_sens_genrator, load_corpus
import sys
sys.path.append('..')
import random

from Algorithm import sim_com
trans_log=open('Log/trans_log.txt','a',encoding='utf-8')
#requests.adapters.DEFAULT_RETRIES = 5

class Translator():
    def __init__(self,from_lan_id, to_lan_id, lan_dict, trans_engine, max_bytes_length):

        self.from_lan_id = from_lan_id
        self.to_lan_id = to_lan_id
        self.trans_engine = trans_engine

        self.max_bytes_length = max_bytes_length
        self.raw_data = None
        self.target_data = None
        self.logger = None
        self.handler = None
        self.session = requests.session()
        self.logger_init(self.trans_engine)

        self.lan_dict = lan_dict
        self.lanid_dict = {
            1: '中文',
            2: '英文',
            3: '日文',
            4: '法文',
            5: '韩文',
            6: '俄文',
        }
        self.reverse_lanid_dict = {i: j for j, i in self.lanid_dict.items()}

    # 日志记录初始化
    def logger_init(self, trans_engine):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        self.handler = logging.FileHandler('Log/'+trans_engine+"_log.txt",encoding='utf-8')
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if not self.logger.handlers:
            self.handler.setFormatter(formatter)
            self.logger.addHandler(self.handler)

    def get_back_translate_corpus(self):
        return self.lan_dict[self.lanid_dict[self.to_lan_id]], self.lan_dict[self.lanid_dict[self.from_lan_id]], self.target_data

    # 单句翻译接口， 子类必须实现
    def translate(self, from_lan, to_lan, text):
        pass

    # 批量翻译
    def batch_translate(self, trans_engine, from_lan_id, to_lan_id, back_translate=False):
        trans_result=[]
        all = 0
        if not back_translate:
            real_corpus = load_corpus()
            if real_corpus==None:
                return trans_result
            from_lan = self.lan_dict[self.lanid_dict[self.from_lan_id]]
            to_lan = self.lan_dict[self.lanid_dict[self.to_lan_id]]
            self.raw_data = real_corpus
            self.logger.info('-' * 20 + ' ' * 15 + 'start' + ' ' * 15 + '-' * 20 + '\n')
            self.logger.info(self.trans_engine+'共接收' + str(len(real_corpus)) + '条数据， '+ str(self.from_lan_id) + '至' + str(self.to_lan_id))
            print(get_now_time()+' '+self.trans_engine+'接收 ' + str(len(real_corpus)) + '条数据, '+' '+str(self.lanid_dict[self.from_lan_id]) + '至' + str(self.lanid_dict[self.to_lan_id]))
        else:
            from_lan, to_lan, real_corpus=self.get_back_translate_corpus()

        get_now_milli_time = lambda: int(round(time.time() * 1000))
        now = get_now_milli_time()
        self.logger.info(self.trans_engine+'开始翻译')
        sen_gen=long_sens_genrator(self,real_corpus,self.max_bytes_length)

        for sen in sen_gen:
            #print(sen)
            cids=sen[0].split(',')
            text = sen[1]
            #self.logger.info('条目id: '+ str(cids)+', : ' + get_now_time()+'开始翻译')
            step=0
            while step<5:
                ans = self.translate(from_lan, to_lan, text)
                #print('ans', ans)
                if ans != None :
                    all += len(ans)
                    for i in range(len(ans)):
                        trans_result.append((cids[i], ans[i]))
                    break
                step+=1
                self.logger.info('单句翻译失败，再次尝试 '+str(step))
        rand_sleep_time = 0.01 * random.randint(1, 100)
        time.sleep(rand_sleep_time)
        over = get_now_milli_time()
        self.logger.info(trans_engine+'翻译'+ str(all)+ '条句子'+'花费 '+ str((over - now)/1000)+'s ')
        #print('tst', trans_result)
        return trans_result

    # 启动翻译
    def run(self):
        recall_data = []
        now_time = get_now_time()

        target_data = self.batch_translate(self.trans_engine, self.from_lan_id, self.to_lan_id,  back_translate=False)
        if len(target_data) == 0:
            self.logger.info(self.trans_engine+'本次翻译没有得到翻译结果，进程结束')
            return
        self.target_data = target_data
        self.logger.info('单向翻译完毕')
        fake_data = self.batch_translate(self.trans_engine, self.from_lan_id, self.to_lan_id, back_translate=True)
        self.logger.info('回译完毕')

        for i in range(len(target_data)):
            raw = ''
            fake = ''
            for j in fake_data:
                if j[0] == target_data[i][0]:
                    fake = j[1]
                    break
            for k in self.raw_data:
                if str(k[0]) == target_data[i][0]:
                    raw = k[1]
                    break
            if fake != '' and raw != '':
                t = {}
                t['raw_text'] = raw
                t['target_text'] = target_data[i][1]
                t['fake_text'] = fake
                t['cid'] = int(target_data[i][0])
                t['score'] = float(sim_com.similarity_compute(raw, t['fake_text']))
                recall_data.append(t)
            from_lan = self.lanid_dict[self.from_lan_id]
            to_lan = self.lanid_dict[self.to_lan_id]
        #print(recall_data)
        with open('Data/'+self.trans_engine+'_'+from_lan+'_'+to_lan+'_result.txt','w',encoding='utf-8')as f:
            for t in recall_data:
                print(str(t['cid'])+'\t'+t['raw_text'],'\t',t['target_text'],'\t',t['fake_text'],'\t',str(t['score']),file=f)
        if len(recall_data)==0 :
            self.logger.info('本次'+self.trans_engine+'未翻译到数据，已退出')
            return

        #dbop.recall_corpus_insert(recall_data, transed_slid)
        self.logger.info(self.trans_engine+'共翻译'+str(len(recall_data))+'条数据')
        self.logger.info('-'*20+' '*15+'end'+' '*15+'-'*20+'\n')
        print(get_now_time()+' '+self.trans_engine+' 完成 '+str(len(recall_data))+' 条目翻译, '+str(self.lanid_dict[self.from_lan_id]) + '至' + str(self.lanid_dict[self.to_lan_id]))
        self.logger.removeHandler(self.handler)
        #,file=trans_log
    def getHtml(self, session, url, headers, data, is_post):
        if param['use_proxy']:
            return get_html_use_proxy(self.logger, session, url, headers, data, is_post)
        else:
            return get_html(self.logger, session, url, headers, data, is_post)
