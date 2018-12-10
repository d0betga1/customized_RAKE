import json

import requests
from RAKE import Rake
from bs4 import BeautifulSoup

# uri = 'https://www.bing.com/search?q=oop&qs=HS&sp=1'
uri = 'https://www.google.com/search?q=oop'
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'
    , 'cookie': 'CONSENT=YES+VN.en+20180617-14-0; 1P_JAR=2018-12-10-04; NID=150=AlIBdTfrBFVIEaHP_N7q8kXAVXUT4GAPd6Ypun_D906J0RrB_uCnJw26pKRtYV_zPM7pNBfMfEfA9YIi3LqKxmg9ScZxSKIgJC5II1CvVR3JgQUSeefvzJGcE0XWPeCfbqs_5GusQ7sXL09H_qTPq9GSz3WRCKeiUkmeuLuzwFrxqmMTbXphyuINrFespR8Sl7l3XvA'
}

r = requests.get(uri, headers=headers)

soup = BeautifulSoup(r.text, 'html.parser')

with open('index.html', 'w+') as file:
    file.write(soup.prettify())
file.close()

# for strong_tag in soup.find_all('strong'):
#     print(
#         strong_tag.text
#         , strong_tag.next_sibling
#     )