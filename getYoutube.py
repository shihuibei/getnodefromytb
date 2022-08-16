#! /usr/bin/env python3
from requests.api import head
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import threading
import time
import os
import requests
from io import BytesIO
from pyzbar import pyzbar
from PIL import Image
import base64
import urllib
import json
import re
url = 'https://www.youtube.com/watch?v=4ivs7rZWcM8'
interval = 20
ssVemssList = set()
n = 5
stopNum = 0
needRun = True;
imgPath = './clash/'
youtubeDir = os.getcwd();
if(needRun):
    try:
        proxy = "185.51.76.129:3080" # IP:PORT or HOST:PORT
        options = Options()
        options.add_argument("--mute-audio")
        options.add_argument('headless')
#         options.add_argument("--proxy-server=socks5://" + proxy)
        # path = "./chromedriver"
        path = "/usr/local/bin/chromedriver"
        driver = webdriver.Chrome(path, options=options)
        driver.get(url)

        timeout = 10 # seconds
        element = WebDriverWait(driver, timeout).until(lambda x: x.find_element_by_id("logo"))
        for i in range(3):
            try:
                driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[5]/div[2]/ytd-button-renderer[2]').click()
            except Exception:
                print("跳过cookie pop 窗口不存在")
            time.sleep(60)
            driver.refresh()
        element = WebDriverWait(driver, timeout).until(lambda x: x.find_element_by_id("logo"))
        print("Page is ready!")

    except TimeoutException:
        print("Loading took too much time!")


def isTxt(name, text):
    txtFile = open(name + '.txt', 'a+')
    result = True
    while True:
        line = txtFile.readline()
        if not line:
            break
        if text in line:
            result = False
            break

    txtFile.close()
    return result


def get_QR_doe():
    print("是否开始执行")
    play = driver.find_element_by_class_name("ytp-play-button").get_attribute("aria-label")
    try:
#         if(('pause' not in play) and ('Pause' not in play)):
        driver.find_element_by_class_name("ytp-play-button").click()
        time.sleep(1)
    except Exception:
        print("没有元素")
    png = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    driver.get_screenshot_as_file(r"%s%s.png" % (imgPath, png))

    get_ewm(imgPath + png + ".png")
    print("png path= " + png)
    t = threading.Timer(interval, get_QR_doe)
    global stopNum
    stopNum = stopNum + 1
    t.start()
    
def get_ewm(img_adds):
    try:
        img = Image.open(img_adds)
        txt_list = pyzbar.decode(img)
    except Exception as e: 
        print("解析图片错误 " + e)
    if(stopNum>6):
        exit(0)

    for txt in txt_list:
        barcodeData = txt.data.decode("utf-8")
        barcodeData = str(barcodeData)
        if(((barcodeData.startswith("ss")) or (barcodeData.startswith("vmess")))
        and not (barcodeData.startswith("ssr"))):
            ssVemssList.add(barcodeData)
            print("解析的地址: " + barcodeData)
            if(len(ssVemssList) >= n):
                getClash(ssVemssList)
                s = '\n'.join(ssVemssList)
                contents = base64.b64encode(s.encode()).decode()
                push2gitlab()
                push2gitlabV2ray(contents)
                ssVemssList.clear()
                driver.close(); #closes the browser
                exit(0)

def parseLink(link, idx):
    print(link)
    if(link.startswith("ss")):
        link = link.replace("ss://", "")
        if('@' in link):
            list = link.split('@')
            psword = list[0]  # base64
            psword += "=" * ((4 - len(psword) % 4) % 4)
            encodebytes = str(base64.decodebytes(psword.encode('utf-8'))).replace("b'", "").replace("'", "")
            ports = list[1]   # urlencoded
            raw = str(urllib.parse.unquote(ports))
            print(psword, ports)
            cipher = encodebytes.split(":")[0]
            password = encodebytes.split(":")[1]
            server = raw.split(':')[0]            
            port = raw.split(':')[1].split("#")[0].split('?')[0]
            port = port.replace("/", "")
            data = {
                'name': str(idx) + "@" + str(idx),
                'server': server,
                'port': port,
                'cipher':cipher,
                'type': 'ss',
                'password': password
            } 
            try:
                if("plugin" in raw):
                    # plugin=simple-obfs;obfs=tls;obfs-host=n46hm52773.wns.windows.com
                    # plugin-opts: {mode: websocket, host: twn600wd4.soflyso.info, path: "", tls: true, mux: true, skip-cert-verify: true}
                    print('raw', raw)
                    patternplugin = 'plugin=(.*?);'
                    plugin = re.search(patternplugin, raw).group(1)
                    plugin_opts = {}
                    if("mode" in raw):
                        pattern2 = 'mode=(.*?);'
                        mode = re.search(pattern2, raw).group(1)
                        plugin_opts['mode'] = mode;
                    pattern3 = 'host=(.*?)(#|;)'
                    host = re.search(pattern3, raw).group(1)
                    plugin_opts['host'] = host;
                    if('tls' in raw):
                        plugin_opts['tls'] = True
                        plugin_opts['skip-cert-verify'] = True
                    if('mux' in raw):
                        plugin_opts['mux'] = True
                    
                    plugin_optstr = str(plugin_opts).replace("True", "true").replace("'", "")
                    print('plugin_opts', plugin_optstr)
                    data = {
                    'name': str(idx) + "@" + str(idx),
                    'server': server,
                    'port': port,
                    'cipher':cipher,
                    'type': 'ss',
                    'password': password,
                    'plugin': plugin,
                    'plugin-opts': plugin_optstr
                    }
            except Exception:
                print("执行出错")
            return str(data).replace("'", "")
        else:
            link = link.split("#")[0]
            link += "=" * ((4 - len(link) % 4) % 4)
            encodebytes = str(base64.decodebytes(link.encode('utf-8'))).replace("b'", "").replace("'", "")
            print(encodebytes)
            list = encodebytes.split("@")
            ports = list[1]   # urlencoded
            encodebytes = list[0]
            raw = str(urllib.parse.unquote(ports))
            cipher = encodebytes.split(":")[0]
            password = encodebytes.split(":")[1]
            server = raw.split(':')[0]            
            port = raw.split(':')[1].split("#")[0].split('?')[0]
            port = port.replace("/", "")
            data = {
                'name': str(idx) + "@" + str(idx),
                'server': server,
                'port': port,
                'cipher':cipher,
                'type': 'ss',
                'password': password
            }
            return str(data).replace("'", "")
              
            
    elif(link.startswith("vmess")):
        
        link = link.replace("vmess://", "")
        dd = json.loads(base64.b64decode(link))
        nodedict = {}
        nodedict['name'] = str(idx) + "@" + str(idx)
        nodedict['server'] = dd['add']
        nodedict['port'] = dd['port']
        nodedict['type'] = 'vmess'   
        nodedict['uuid'] = dd['id']
        nodedict['alterId'] = 64
        nodedict['cipher'] = 'auto'
        nodedict['tls'] = True
        nodedict['skip-cert-verify'] = False
        nodedict['network'] = dd['net']
        nodedict['ws-path'] = dd['path']
        nodedict['ws-headers'] = "{Host: " +  dd['host'] + "}"
        return str(nodedict).replace('True', 'true').replace('False', 'false').replace("u'", "'").replace("'", "")
    return ""
# sslink = 'ss://YWVzLTI1Ni1nY206ZHBHakE0R2t6VjI4UVBEWXpFcDk0Y1RlQDEzOC4xOTkuNDIuMTM2OjQ5NTE0#%F0%9F%87%BA%F0%9F%87%B8_US_%E7%BE%8E%E5%9B%BD'
# print(parseLink(sslink, 1))

def setPG(nodes):
    # 设置策略组 auto,Fallback-auto,Proxy
    proxy_names = "proxy-groups:"
    jiedian = """
  - name: 🔰 节点选择
    type: select
    proxies:
      - ♻️ 自动选择
      - 🎯 全球直连
    """
    zidong = """
  - name: ♻️ 自动选择
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    proxies:
    """
    guowai = """
  - name: 🌍 国外媒体
    type: select
    proxies:
      - 🔰 节点选择
      - ♻️ 自动选择
      - 🎯 全球直连
    """
    guonei = """
  - name: 🌏 国内媒体
    type: select
    proxies:
      - 🎯 全球直连
      - 🔰 节点选择
    """
    weiruan = """
  - name: Ⓜ️ 微软服务
    type: select
    proxies:
      - 🎯 全球直连
      - 🔰 节点选择
    """
    dianbao = """
  - name: 📲 电报信息
    type: select
    proxies:
      - 🔰 节点选择
      - 🎯 全球直连
    """

    apple = """
  - name: 🍎 苹果服务
    type: select
    proxies:
      - 🔰 节点选择
      - 🎯 全球直连
      - ♻️ 自动选择
    """
    direct = """
  - name: 🎯 全球直连
    type: select
    proxies:
      - DIRECT
    """
    quanqiulanjie = """
  - name: 🛑 全球拦截
    type: select
    proxies:
      - REJECT
      - DIRECT
    """
    louwang = """
  - name: 🐟 漏网之鱼
    type: select
    proxies:
      - 🎯 全球直连
      - 🔰 节点选择
      - ♻️ 自动选择  
    """
    groups = [jiedian, zidong, guowai,guonei, weiruan, dianbao, apple, direct, quanqiulanjie, louwang]
    for p in groups:
        proxy_names = proxy_names + p
        for idx, node in enumerate(nodes):
            if(idx == 0):
                proxy_names = proxy_names + "  - " +str(idx) + "@" + str(idx) +  "\n"
            else:
                proxy_names = proxy_names + "      - " + str(idx) + "@" + str(idx)  +  "\n"
                if(idx == len(nodes)-1):
                    proxy_names = proxy_names[:-1]
    
    return proxy_names

def setNodes(nodes):
    proxies = "proxies:\n"
    for idx, node in enumerate(nodes):
        txt = parseLink(node, idx)
        proxies = proxies + "  - "+ txt + "\n"
    return proxies[:-1]   

def getClash(nodes):
    with open(youtubeDir + "/clash/general.yaml", "r") as f:
        gener = f.read()
    with open(youtubeDir + "/clash/clash.yaml", "w") as f:
        f.writelines(gener)
    # nodes = list(nodes)
    info = setNodes(nodes) +"\n" + setPG(nodes)
    print(info)
    with open(youtubeDir + "/clash/clash.yaml", 'a') as f:   
        f.write(info)

    with open( youtubeDir + "/clash/rule.yaml", "r") as f:
        rules = f.read()
    with open(youtubeDir + "/clash/clash.yaml", 'a') as f:
        f.write(rules)



def push2gitlab():
    with open( youtubeDir + "/clash/clash.yaml", "r") as f:
        content = f.read()
    url = 'https://gitlab.com/api/v4/projects/{}/repository/files/clash.yaml'.format(29907677)
    # delete first
    data = {
        "branch": "main",
        "author_email": "author@example.com",
        "author_name": "Firstname Lastname",
        "commit_message": "delete file"
    }

    header = {
        'content-type': 'application/json',
        'private-token': 'eLcVYGdgd55VjQQ8UFb7',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'
    }
    res1 = requests.delete(url=url,headers=header, json=data).content
    print("删除结果", res1)

    data['content'] = content
    data['commit_message'] = 'update clash'

    res = requests.post(url=url, headers=header, json=data).content
    print("推送结果", res)


def push2gitlabV2ray(content):
    url = 'https://gitlab.com/api/v4/projects/{}/repository/files/v2ray.txt'.format(29907677)
    # delete first
    data = {
        "branch": "main",
        "author_email": "author@example.com",
        "author_name": "Firstname Lastname",
        "commit_message": "delete v2ray file"
    }

    header = {
        'content-type': 'application/json',
        'private-token': 'eLcVYGdgd55VjQQ8UFb7',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'
    }
    res1 = requests.delete(url=url,headers=header, json=data).content
    print("删除v2ray结果", res1)

    data['content'] = content
    data['commit_message'] = 'update v2ray'

    res = requests.post(url=url, headers=header, json=data).content
    print("推送v2ray结果", res)

if __name__ == '__main__':
    get_QR_doe()



