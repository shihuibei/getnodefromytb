import re
import time

import requests

import setting


class FreeNom(object):
    # 登录
    LOGIN_URL = 'https://my.freenom.com/dologin.php'
    # 查看域名状态
    DOMAIN_STATUS_URL = 'https://my.freenom.com/domains.php?a=renewals'
    # 域名续期
    RENEW_DOMAIN_URL = 'https://my.freenom.com/domains.php?submitrenewals=true'

    TOKEN_REGEX = 'name="token"\svalue="(?P<token>[a-z||A-Z||0-9]+)"'
    DOMAIN_INFO_REGEX = '<tr><td>(?P<domain>[^<]+)<\/td><td>[^<]+<\/td><td>[^<]+<span class="[^"]+">(?P<days>\d+)[' \
                        '^&]+&domain=(?P<id>\d+)"'
    LOGIN_STATUS_REGEX = '<li.*?Logout.*?<\/li>'

    def __init__(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.session = requests.session()
        self.token_pattern = re.compile(self.TOKEN_REGEX)
        self.domain_info_pattern = re.compile(self.DOMAIN_INFO_REGEX)
        self.login_pattern = re.compile(self.LOGIN_STATUS_REGEX)

    def run(self) -> list:
        self.login()
        html = self.get_domains()
        token_match = self.token_pattern.findall(html)
        domain_info_match = self.domain_info_pattern.findall(html)
        login_match = self.login_pattern.findall(html)


        if not login_match:
            print("FreeNom login parse failed")

        if not token_match:
            print("FreeNom token parse failed")

        if not domain_info_match:
            print("FreeNom domain info parse failed")

        token = token_match[0]
        print(f"waiting for renew domain info is {domain_info_match}")

        result = []

        for info in domain_info_match:
            time.sleep(1)
            domain, days, domain_id = info
            msg = "失败"

            if int(days) > 14:
                print(f"FreeNom domain {domain} can not renew, days until expiry is {days}")

            else:
                response = self.renew_domain(token, domain_id)

                if response.find("Order Confirmation") != -1:
                    msg = "成功"
                    print(f"FreeNom renew domain {domain} is success")

            result.append((domain, days, domain_id, msg))
        return result

    def login(self) -> bool:
        data = {
            'username': setting.FM_USERNAME,
            'password': setting.FM_PASSWORD
        }
        headers = {
            **self.headers,
            'Referer': 'https://my.freenom.com/clientarea.php'
        }
        response = self.session.post(self.LOGIN_URL, data=data, headers=headers)
        if response.status_code == 200:
            return True
        else:
            print("FreeNom login failed")

    def get_domains(self) -> str:
        headers = {
            'Referer': 'https://my.freenom.com/clientarea.php'
        }
        response = self.session.get(self.DOMAIN_STATUS_URL, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print("FreeNom check domain status failed")

    def renew_domain(self, token, renewalid) -> str:
        headers = {
            **self.headers,
            "Referer": "https://my.freenom.com/domains.php?a=renewdomain&domain=" + "renewalid"
        }
        data = {
            "token": token,
            "renewalid": renewalid,
            f"renewalperiod[{renewalid}]": "12M",
            'paymentmethod': 'credit'
        }

        response = self.session.post(self.RENEW_DOMAIN_URL, data=data, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print("FreeNom renew domain failed")

    def __del__(self):
        self.session.close()
if __name__ == '__main__':
    c = FreeNom()
    c.run()