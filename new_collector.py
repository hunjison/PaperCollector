import argparse
import requests
import re
from bs4 import BeautifulSoup
import csv

# disable warning
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

"""
YOU SHOULD FILL THIS!!!!!
"""
HEADERS = {}

description = """PaperCollecter\n\n
This is PaperCollecter made by hunjison.\n
This Tool is based on Google Scholar.\n
I want to help all systematic literature reviews.
"""

def multiline_input():
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return lines

"""
url : 검색하려고 하는 URL(Google Scholar)
return : 논문 PDF의 URL
def scholar_search(str : url):
    1. url google scholar에 검색
    2. 검색 결과를 html.parser 적용한 BeautifulSoup 객체를 반환
"""
def scholar_search(url):
    if not HEADERS:
        raise Exception('HEADERS required.')
    res = requests.get(url = url, headers=HEADERS, verify=False)
    soup = BeautifulSoup(res.content, "html.parser")
    return soup

def parse_soup(soup):
    board = soup.select_one('#gs_res_ccl_mid')
    contents = board.select('.gs_r')
    return contents

def parse_each_content(content):
    article_name = ""
    article_year = ""
    article_citation = ""
    article_author = ""
    article_publication = ""
    article_iscollect = False

    left = content.select_one('.gs_ri')
    right = content.select_one('.gs_ggs')

    article_name = left.select_one('a').text
    metadata = left.select_one(".gs_a").text.split('- ')
    article_author = metadata[0].strip()
    article_year = metadata[1].strip()[-4:]
    article_publication = metadata[2].strip()

    citation = re.search("([\d]{1,4})회 인용", left.text)
    if citation:            # ['2048회 인용', '2048']
        article_citation = int(citation[1])

    return [article_year, article_name, article_citation, article_author, article_publication, article_iscollect]


def retrievePDF(content):
    right = content.select_one('.gs_ggs a')
    if right:
        href = right.attrs['href']
        if href[-4:] == '.pdf':
            print("From Google Scholar:", href)
            return href
    
    # 1. "right" not exist (페이지에 PDF url 존재 X)
    # 2. href do not end with '.pdf' (존재하지만 pdf가 아닌 경우) 
    try:
        href2 = content.select_one(".gs_rt a").attrs['href']
        # search doi URL
        res = requests.get(url = href2, verify=False)
        try:
            doi_URL = re.findall('https://doi[.]org/[^"]+', res.text)[0]
            # sci-hub 검색
            sci_hub = "https://sci-hub.se/"
            res3 = requests.get(url = sci_hub + doi_URL, verify=False)
            soup3 = BeautifulSoup(res3.content, "html.parser")
            pdf_src = soup3.select_one("#article embed").attrs['src']
            # //sci-hub.se/downloads/2019-09-13/71/..
            if pdf_src.find('.pdf') < 0:
                raise Exception('PDF not exist')
            elif pdf_src.find("https://") != 0:
                pdf_src = "https:" + pdf_src
            print("From sci-hub:",pdf_src)
            return pdf_src
        except: 
            raise Exception("doi_URL not found")
    except:
        raise Exception(".gs_rt a href not found")

def save(URL, save_name):
    try:
        file = requests.get(URL, stream = True, verify=False)
    except Exception as e:
        print("URL error..", URL, e)
        return False
    
    with open(save_name, "wb") as pdf:
        try:
            for chunk in file.iter_content(chunk_size=1024):
                if chunk:
                    pdf.write(chunk)
            print("Save PDF Done!", save_name)
            return True
        except:
            return False

def csv_save(data):
    f = open('result/result.csv', 'w', newline='')
    wr = csv.writer(f)
    wr.writerows(data)
    f.close()

def do_with_content(content):
    #article_year, article_name, article_citation, article_author, article_publication, article_iscollect
    content_data = parse_each_content(content)
    try:
        article_pdf_url = retrievePDF(content)
        save_result = save(article_pdf_url, "result/" + f"{content_data[1].replace('/','') + '.pdf'}")
        if save_result:
            content_data[5] = True # article_collected
    except Exception as e:
        print(f"[Error]{content_data[1][:60]}: {e}")
    
    return content_data

def search_keyword(number):
    if number > 20:
        raise Exception('number cannot exceed 20')
    
    result = []
    keywords = multiline_input()
    for keyword in keywords:
        url = f'https://scholar.google.com/scholar?hl=ko&as_sdt=0%2C5&q={keyword}&btnG='
        soup = scholar_search(url)
        contents = parse_soup(soup)

        for idx, content in enumerate(contents):
            if idx >= number:
                break
            result.append(do_with_content(content))

    csv_save(result)
    print(f"{len(result)} paper saved.")

def search_url(number):
    url = input()
    result = []
    
    cnt = 0
    collected = 0
    while cnt < number and cnt == collected:
        search_url = url + f"&start={cnt}"
        soup = scholar_search(search_url)
        contents = parse_soup(soup)
        
        for content in contents:
            result.append(do_with_content(content))

        cnt += 10
        collected = len(result)

    csv_save(result)
    print(f"{len(result)} paper saved.")

def main():
    parser = argparse.ArgumentParser(description=description)

    # 입력받을 인자값 등록
    parser.add_argument('-type', required=True, help='keyword or url')
    parser.add_argument('-number', required=True, help='A number of paper that you want to collect. 0 means "Collect ALL"')
    args = parser.parse_args()

    # 입력받은 인자값 출력
    print("-type:", args.type, "-number:", args.number)

    if not args.number.isdigit():
        raise Exception(f'-number option requires int, not {type(args)}')
    else:
        num = int(args.number)
        if num == 0:
            num = 10000 # ALL

    if args.type.lower() == 'keyword':
        search_keyword(num)
    elif args.type.lower() == 'url':
        search_url(num)
    else:
        raise Exception('Not supported search type')

if __name__ == "__main__":
    main()