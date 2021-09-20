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

ssVemssList = set()
n = 15
needRun = True;
if(needRun):
    try:
        proxy = "127.0.0.1:7890" # IP:PORT or HOST:PORT
        options = Options()
        options.add_argument("--mute-audio")
        options.add_argument('headless')
        # options.add_argument("--proxy-server=http://" + proxy)
        path = "./chromedriver"
        driver = webdriver.Chrome(path, options=options)
        driver.get("https://www.youtube.com/watch?v=Lc21evKC1jg")

        timeout = 10 # seconds
        element = WebDriverWait(driver, timeout).until(lambda x: x.find_element_by_id("logo"))
        for i in range(3):
            try:
                driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[5]/div[2]/ytd-button-renderer[2]').click()
            except Exception:
                print("跳过cookie pop 窗口不存在")
            time.sleep(10)
            driver.refresh()
        element = WebDriverWait(driver, timeout).until(lambda x: x.find_element_by_id("logo"))
        print("Page is ready!")

    except TimeoutException:
        print("Loading took too much time!")


def txt2(name, target):
    b = os.getcwd()

    if not os.path.exists(b):
        os.makedirs(b)

    txtFile = open(name + '.txt', 'a')
    if isTxt(name, target):
        txtFile.write(target)
    txtFile.close()


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

def get_ewm(img_adds):
    if os.path.isfile(img_adds):
        img = Image.open(img_adds)
    else:
        rq_img = requests.get(img_adds).content
        img = Image.open(BytesIO(rq_img))

    txt_list = pyzbar.decode(img)

    for txt in txt_list:
        barcodeData = txt.data.decode("utf-8")
        txt2('result', barcodeData + "\n")
        barcodeData = str(barcodeData)
        if(((barcodeData.startswith("ss")) or (barcodeData.startswith("vmess")))
        and not (barcodeData.startswith("ssr"))):
            ssVemssList.add(barcodeData)
            if(len(ssVemssList) >= n):
                getClash(ssVemssList)
                ssVemssList.clear()
                os.remove('./result.txt')
                driver.close(); #closes the browser
                exit(0)


    os.remove(img_adds)

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
            # print(psword, ports)
            cipher = encodebytes.split(":")[0]
            password = encodebytes.split(":")[1]
            server = raw.split(':')[0]            
            temp = raw.split(':')[1].split("#")[0].split('/?')
            port = raw.split(':')[1].split("#")[0].split('/?')[0]
            data = {
                'name': str(idx) + "@" + str(idx),
                'server': server,
                'port': port,
                'cipher':cipher,
                'type': 'ss',
                'password': password
            } 
            if(len(temp) == 2):
                # plugin=simple-obfs;obfs=tls;obfs-host=n46hm52773.wns.windows.com
                # plugin: obfs, plugin-opts: {mode: tls, host: n46hm52773.wns.windows.com}
                plugis = raw.split(':')[1].split("#")[0].split('/?')[1]
                plugin = plugis.split(';')[0].split('plugin=')[1].replace("simple-", "")
                mode = plugis.split(';')[1].replace("obfs=" ,"")
                hosts = plugis.split(';')[2].replace("obfs-host=", "")
                plugin_opts = '{mode: '+mode+', host: '+hosts+'}'
                data = {
                'name': str(idx) + "@" + str(idx),
                'server': server,
                'port': port,
                'cipher':cipher,
                'type': 'ss',
                'password': password,
                'plugin': plugin,
                'plugin-opts': plugin_opts
                } 
              
            return str(data).replace("'", "")
    elif(link.startswith("vmess")):
        
        link = link.replace("vmess://", "")
        dd = json.loads(base64.b64decode(link))
        nodedict = {}
        nodedict['name'] = str(idx) + "@" + str(idx)
        nodedict['server'] = dd['add']
        nodedict['port'] = dd['port']
        if(dd['net'] == 'ws'):
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
      - 🔰 节点选择
      - 🎯 全球直连
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
    with open("./clash/general.yaml", "r") as f:
        gener = f.read()
    with open("./clash/clash.yaml", "w") as f:
        f.writelines(gener)
    # nodes = list(nodes)
    info = setNodes(nodes) +"\n" + setPG(nodes)
    print(info)
    with open("./clash/clash.yaml", 'w') as f:   
        f.write(info)

    with open("./clash/rule.yaml", "r") as f:
        rules = f.read()
    with open("./clash/clash.yaml", 'a') as f:
        f.write(rules)

def get_QR_doe():
    play = driver.find_element_by_class_name("ytp-play-button").get_attribute("aria-label")
    try:
        if(('pause' not in play) and ('Pause' not in play)):
            driver.find_element_by_class_name("ytp-play-button").click()
            time.sleep(1)
    except Exception:
        print("没有元素")
    png = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    driver.get_screenshot_as_file(r"./png/%s.png" % png)

    get_ewm("./png/" + png + ".png")
    t = threading.Timer(30, get_QR_doe)
    t.start()

def readFromtxt():
    lines = tuple(open("./result.txt", 'r'))
    node = set()
    for i  in lines:
        i = i.replace('\n', '')
        if((i.startswith("ss") or i.startswith("vmess"))and not i.startswith("ssr")):
            node.add(i)
    getClash(node)

if __name__ == '__main__':
    get_QR_doe()


