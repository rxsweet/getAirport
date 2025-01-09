import re
import time
import requests
import threading
from tqdm import tqdm
#from retry import retry
from datetime import datetime
import math
import yaml
import urllib.parse

#文件位置
URLLIST_PATH = './data/subscribes.txt'
URL_YAML = './data/sub_info.yaml'

"""
URL_YAML = '4.yaml'
URL_LIST = '2.txt'
ALIVE_LIST = '3.txt'
"""
# 流量byte转字符串str大小
def pybyte(size, dot=2):
    size = float(size)
    # 位 比特 bit
    if 0 <= size < 1:
        human_size = str(round(size / 0.125, dot)) + 'b'
    # 字节 字节 Byte
    elif 1 <= size < 1024:
        human_size = str(round(size, dot)) + 'B'
    # 千字节 千字节 Kilo Byte
    elif math.pow(1024, 1) <= size < math.pow(1024, 2):
        human_size = str(round(size / math.pow(1024, 1), dot)) + 'KB'
    # 兆字节 兆 Mega Byte
    elif math.pow(1024, 2) <= size < math.pow(1024, 3):
        human_size = str(round(size / math.pow(1024, 2), dot)) + 'MB'
    # 吉字节 吉 Giga Byte
    elif math.pow(1024, 3) <= size < math.pow(1024, 4):
        human_size = str(round(size / math.pow(1024, 3), dot)) + 'GB'
    # 太字节 太 Tera Byte
    elif math.pow(1024, 4) <= size < math.pow(1024, 5):
        human_size = str(round(size / math.pow(1024, 4), dot)) + 'TB'
    # 拍字节 拍 Peta Byte
    elif math.pow(1024, 5) <= size < math.pow(1024, 6):
        human_size = str(round(size / math.pow(1024, 5), dot)) + 'PB'
    # 艾字节 艾 Exa Byte
    elif math.pow(1024, 6) <= size < math.pow(1024, 7):
        human_size = str(round(size / math.pow(1024, 6), dot)) + 'EB'
    # 泽它字节 泽 Zetta Byte
    elif math.pow(1024, 7) <= size < math.pow(1024, 8):
        human_size = str(round(size / math.pow(1024, 7), dot)) + 'ZB'
    # 尧它字节 尧 Yotta Byte
    elif math.pow(1024, 8) <= size < math.pow(1024, 9):
        human_size = str(round(size / math.pow(1024, 8), dot)) + 'YB'
    # 千亿亿亿字节 Bront Byte
    elif math.pow(1024, 9) <= size < math.pow(1024, 10):
        human_size = str(round(size / math.pow(1024, 9), dot)) + 'BB'
    # 百万亿亿亿字节 Dogga Byte
    elif math.pow(1024, 10) <= size < math.pow(1024, 11):
        human_size = str(round(size / math.pow(1024, 10), dot)) + 'NB'
    # 十亿亿亿亿字节 Dogga Byte
    elif math.pow(1024, 11) <= size < math.pow(1024, 12):
        human_size = str(round(size / math.pow(1024, 11), dot)) + 'DB'
    # 万亿亿亿亿字节 Corydon Byte
    elif math.pow(1024, 12) <= size:
        human_size = str(round(size / math.pow(1024, 12), dot)) + 'CB'
    # 负数
    else:
        raise ValueError('{}() takes number than or equal to 0, but less than 0 given.'.format(pybyte.__name__))
    return human_size


def list_rm(urlList):#列表去重
    begin = 0
    rm = 0
    length = len(urlList)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = urlList[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            if proxy_compared == urlList[begin_2]:
                urlList.pop(begin_2)
                length -= 1
                begin_2 -= 1
                rm += 1
            begin_2 += 1
        begin += 1
    print(f'重复数量 {rm}\n-----去重结束-----\n')
    print(f'剩余总数 {str(len(urlList))}\n')
    return urlList
    
def sub_check(url,bar):
    headers = {'User-Agent': 'ClashforWindows/0.18.1'}
    with thread_max_num:
        #@retry(tries=3)
        def start_check(url):
            res=requests.get(url,headers=headers,timeout=5)#设置5秒超时防止卡死
            if res.status_code == 200:
                res.encoding='utf-8' 
                try: #有流量信息
                    info = res.headers['subscription-userinfo']
                    #print(str(res.headers))
                    info_num = re.findall('\d+',info)
                    #info_num[3] - 到期时间 
                    #info_num[2]- 总流量
                    #info_num[1]-使用的下载流量
                    #info_num[0] - 使用的上传流量
                    time_now=int(time.time())
                    # 剩余流量大于10MB
                    if int(info_num[2])-int(info_num[1])-int(info_num[0])>10485760:
                        if len(info_num) == 4: # 有时间信息
                            if time_now <= int(info_num[3]): # 没有过期
                                usetime = int(info_num[3])
                                date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(usetime))
                                #date_str = time.strftime('%Y-%m-%d', time.localtime(usetime))
                                liuliang_str = pybyte(int(info_num[2])-int(info_num[1])-int(info_num[0]))
                                #查看有节点再添加
                                if res.text:
                                    try:
                                        proxyconfig = yaml.load(res.text, Loader=yaml.FullLoader)
                                        #print('len = '+ str(len(proxyconfig['proxies'])))
                                        node_num = len(proxyconfig['proxies'])
                                        if node_num > 0:
                                            #
                                            url_yaml = {}
                                            url_yaml['api'] = url
                                            url_yaml['time'] = date_str
                                            url_yaml['free'] = liuliang_str
                                            url_yaml['nodes'] = str(node_num)
                                            url_yaml['url'] = res.headers['profile-web-page-url']
                                            #url_yaml['content-disposition'] = res.headers['content-disposition']
                                            name = re.search(f"UTF-8''(.*)", res.headers['content-disposition'])
                                            #如果获取到内容
                                            if name:
                                                url_yaml['name'] = urllib.parse.unquote(name.group(1))
                                                #print("url_yaml['content-disposition'] = " + url_yaml['content-disposition'] )
                                            new_yaml.append(url_yaml)
                                    except Exception as e: 
                                        print('获取机场信息失败')
                                        print(e)
                                
                                #print(url+' 到期时间：' + date_str +' -- 剩余流量：' + liuliang_str)
                            else: # 已经过期
                                old_list.append(url)
                        else: # 没有时间信息
                            liuliang_str = pybyte(int(info_num[2])-int(info_num[1])-int(info_num[0]))
                            #查看有节点再添加
                            if res.text:
                                try:
                                    proxyconfig = yaml.load(res.text, Loader=yaml.FullLoader)
                                    #print('len = '+ str(len(proxyconfig['proxies'])))
                                    node_num = len(proxyconfig['proxies'])
                                    if node_num > 0:
                                        #
                                        url_yaml = {}
                                        url_yaml['api'] = url
                                        url_yaml['time'] = '永久有效'
                                        url_yaml['free'] = liuliang_str
                                        url_yaml['nodes'] = str(node_num)
                                        url_yaml['url'] = res.headers['profile-web-page-url']
                                        #url_yaml['content-disposition'] = res.headers['content-disposition']
                                        name = re.search(f"UTF-8''(.*)", res.headers['content-disposition'])
                                        #如果获取到内容
                                        if name:
                                           url_yaml['name'] = urllib.parse.unquote(name.group(1))
                                        new_yaml.append(url_yaml)
                                except Exception as e: 
                                    print('获取机场信息失败')
                                    print(e)
                            #print(url+' 到期时间：无 -- 剩余流量：'+ liuliang_str)
                    else: # 流量小于10MB
                        #old_list.append(url)
                        pass
                except:
                    #old_list.append(url)  
                    pass
                # output_text='无流量信息捏'
            else:
                #old_list.append(url)
                pass
        try:
            start_check(url)
        except:
            #old_list.append(url)
            pass
        bar.update(1)

#读取list文件,
#返回str字符串
#读取完成后需  url_list = re.split(r'\n+',urllist_content) #将字符串以'\n'切割为列表   
def read_listfile(urllistfile):
    file_urllist = open(urllistfile, 'r', encoding='utf-8')
    urllist_content = file_urllist.read()
    file_urllist.close()
    return urllist_content


def yaml_rm(new_yaml):#列表去重
    begin = 0
    rm = 0
    length = len(new_yaml)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = new_yaml[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            if proxy_compared['name'] == new_yaml[begin_2]['name']:
                if proxy_compared['time'] == '永久有效':
                    new_yaml.pop(begin_2)
                else:
                    date_obj = datetime.strptime(proxy_compared['time'], "%Y-%m-%d %H:%M:%S")
                    date_obj1 = datetime.strptime(new_yaml[begin_2]['time'], "%Y-%m-%d %H:%M:%S")
                    if date_obj < date_obj1:
                        new_yaml[begin]['api'] = new_yaml[begin_2]['api']
                        new_yaml[begin]['time'] = new_yaml[begin_2]['time']
                    new_yaml.pop(begin_2)
                length -= 1
                begin_2 -= 1
                rm += 1
            begin_2 += 1
        begin += 1
    print(f'重复数量 {rm}\n-----去重结束-----\n')
    print(f'剩余总数 {str(len(new_yaml))}\n')
    return new_yaml

if __name__=='__main__':

    new_list = []
    alive = []
    new_yaml = []

    #添加更新时间
    currentTime = datetime.now().strftime("%Y-%m-%d\t%H:%M:%S")
    new_list.append('更新时间:\t'+currentTime+'\n')
    #读取订阅api
    urllist_content = read_listfile(URLLIST_PATH)
    url_list = re.split(r'\n+',urllist_content)
    #url_list= list_rm(url_list)  #去重  
    thread_max_num =threading.Semaphore(32) #32线程
    bar = tqdm(total=len(url_list), desc='订阅筛选：')
    thread_list = []
    for url in url_list:
        #为每个新URL创建线程
        t = threading.Thread(target=sub_check, args=(url,bar))
        #加入线程池并启动
        thread_list.append(t)
        t.daemon=True
        t.start()
    for t in thread_list:
        t.join()
    bar.close()
    # 去重
    new_yaml = yaml_rm(new_yaml)
    #收集alive,new_list
    for url in new_yaml:
        alive.append(url['api'])
        new_list.append('name：' + url['name'] + ' -- time：' + url['time'] +' -- free：' + url['free'] + ' -- nodes：' + url['nodes'] + ' -- url：' + url['url'])
        new_list.append(url['api']+'\n')
    #save alive,未保存newlist
    with open(URLLIST_PATH,"w+") as f:
        for url in alive:
            f.write(url+'\n')
    #save yaml
    with open(URL_YAML, 'w',encoding="utf-8") as f:
        data = yaml.dump(new_yaml, f,allow_unicode=True)

