# 从github 获取 节点然后转存到gitlab

import requests


def push2gitlab(content):
    url = 'https://gitlab.com/api/v4/projects/{}/repository/files/clash2.yaml'.format(29907677)
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

url = 'https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1'

# proxies = { 
#               "http"  : "http://127.0.0.1:7890", 
#               "https" : "http://127.0.0.1:7890"
# }


headers = {
    'authority': 'api.github.com',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
}

response = requests.get(url=url, headers=headers)
data = response.json()

datalist = data['tree']
import datetime
currDate = datetime.datetime.now().strftime("%Y_%m_%d") + "/"

rawUrl = 'https://raw.githubusercontent.com/changfengoss/pub/main/{}'
for i in datalist:
    path = i['path']
    if  (currDate in path and '.yaml' in path):
        size = i['size']
        if(size < 2000000):
            print(rawUrl.format(path))
            res = requests.get(url=rawUrl.format(path), headers=headers)
            # with open('./clash/new.yaml', 'wb') as f:
            #     f.write(res.content)
            # with open('./clash/new.yaml', 'r') as f:
            #     content = f.read()
            #     push2gitlab(content)
            push2gitlab(res.content.decode("utf-8"))
            exit(0)

