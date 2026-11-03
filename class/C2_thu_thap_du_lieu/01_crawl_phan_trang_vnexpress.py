import requests
import re
from urllib.parse import urljoin

url="https://vnexpress.net/bong-da"
html = requests.get(url).text

def get_LinksbyRegEx(url_visit):
    global Links_ToDo
    print("** Now visiting:",url_visit)
    
    Links_seen.append(url_visit)    
    html = requests.get(url_visit).text
    NextLinks=re.findall(r'href="([^"]*bong-da-p\d+)"', html)

    for Link in NextLinks:
        full_link = urljoin(url_visit, Link)
        if full_link not in Links_ToDo and full_link not in Links_seen:
            Links_ToDo.append(full_link)
        
    if Links_ToDo:
        get_LinksbyRegEx(Links_ToDo.pop(0))
    else:
        return

#Cách 1: Lấy link tự động từ Biểu thức chính quy - Sử dụng thuật toán đệ quy
Links_ToDo=[url]
Links_seen=[]
get_LinksbyRegEx(Links_ToDo.pop(0))
print(len(Links_seen), "links found!")


#Cách 2: Dựa trên quy tắc cấu trúc url để tạo link
Links_ToDo=[url]
for i in range(2,49):
    Link="https://vnexpress.net/bong-da-p" + str(i)
    Links_ToDo += [Link]

print(Links_ToDo)