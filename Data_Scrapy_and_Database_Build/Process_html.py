import os
from Python_Lib.My_Lib_Office import *
from hanziconv import HanziConv

def process(html_file):
    # print(html_file)
    html = open(html_file,encoding='utf-8',errors="ignore").read()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    ret = []

    # Find all 'div' elements with 'aria-label' attribute in ["English Terms", "Mandarin Terms", "Academic sector"]
    divs = soup.find_all('div', {'aria-label': ["English Terms", "Mandarin Terms", "Academic sector"]})

    for div in divs:
        # Extract and print text within 'a' tag
        if div['aria-label'] in ["English Terms", "Mandarin Terms"]:
            if div.find('a') is not None:
                ret.append(div.find('a').text.strip())
                if div.find('a').has_attr("href"):
                    ret.append(div.find('a')['href'])
                else:
                    ret.append("")
            else:
                ret.append("")
                ret.append("")

        elif div['aria-label']=="Academic sector":
            ret.append(div.text.strip())

    # for i in range(0,len(ret),5):
    #     print('\t'.join(ret[i:i+5]))

    ret = [HanziConv.toSimplified(x.replace("\n","")) for x in ret]
    print(html_file,len(ret))
    if len(ret)!=5000:
        os.rename(html_file,html_file.replace(".html",'_error.html'))

    ret = [ret[i:i+5] for i in range(0,len(ret),5)]
    write_xlsx(html_file+'.xlsx',ret)


for file in os.listdir('Database'):
    if file.endswith(".html"):
        file = os.path.join("Database",file)
        txt_file = file+'.xlsx'
        if not os.path.isfile(txt_file):
            process(file)