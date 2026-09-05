import requests
import re
import os

url="https://phongtro123.com/tinh-thanh/da-nang"
html = requests.get(url).text

def get_LinksbyRegEx(url_visit):
    global Links_ToDo
    print("** Now visiting:",url_visit)
    
    Links_seen.append(url_visit)    
    html = requests.get(url_visit).text
    NextLinks = re.findall(r'href="(https://phongtro123\.com/tinh-thanh/da-nang\?page=\d+)"', html)

    for Link in NextLinks:
        if  Link not in Links_ToDo and Link not in Links_seen:
            Links_ToDo.append(Link)
        
    if Links_ToDo:
        get_LinksbyRegEx(Links_ToDo.pop())
    else:
        return

#Cách 1: Lấy link tự động từ Biểu thức chính quy - Sử dụng thuật toán đệ quy
Links_ToDo=[url]
Links_seen=[]
get_LinksbyRegEx(Links_ToDo.pop())
print(len(Links_seen), "links found!")