import requests


class MailGunApi:
    API_URL = 'https://api.mailgun.net/v3/{}/messages'

    def __init__(self, domain, api_key):
        self.domain = domain
        self.api_key = api_key
        self.base_url = self.API_URL.format(self.domain)


    def send_email(self, to, subject, text, html=None):
        if not isinstance(to, (list, tuple)):
            to = [to]
        data = {
            'from': 'SmileCook <no-reply@{}>'.format(self.domain),
            'to': to,
            'subject': subject,
            'text': text,
            'html': html
        }
        response = requests.post(url=self.base_url, auth=('api', self.api_key), data=data)
        return response


# mailgun = MailGunApi(domain='sandbox0a7de0526e124502ac155429dd35f50f.mailgun.org',
#                      api_key='f001a4905fb0ee408a7e4f8d6dd6f700-4b1aa784-66cf0072')
#
# mailgun.send_email(to=['milovanov160386@gmail.com'], subject='Hello', text='Тестируем MAilGun')

