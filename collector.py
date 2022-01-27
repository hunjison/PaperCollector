"""
input csv 예시
-----------------------------------------------------------------------------
태그    |   연도         |   이름               |   인용수      |   수집 여부
-----------------------------------------------------------------------------
C1     |               |  FlowDroid ...      |             |    x (or o)    
-----------------------------------------------------------------------------
"""

"""
목표 : csv의 이름(1번 열)을 가지고,
1) scholar.google.com 과 sci-hub.se 사이트로부터 논문을 다운로드
2) csv 파일에서 연도, 인용 수 필드 채우기
3) 중복을 확인하여, 이미 다운로드 받은 논문은 다시 다운하지 않는다. (구글에서 자꾸 봇으로 의심해요..)

사용자 입력
1) request header : 구글 탐지 우회
2) csv 파일 경로
3) .py 파일과 동일 경로에 /result 폴더 생성해주어야 함.
"""

from hashlib import new
from shutil import ExecError
import requests
from bs4 import BeautifulSoup
import re
import csv

# disable warning
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

GoogleURL = "https://scholar.google.com/scholar?hl=ko&as_sdt=0%2C5&q=SEARCH_QUERY&btnG="
sci_hub = "https://sci-hub.se/"

"""
USER INPUT
"""
# request header. 구글 보안 탐지 우회(반드시 추가 필요)
HEADERS = {}
# 정해진 양식으로 만들어진 csv 파일의 경로
path_csv = ""

"""
path_csv : csv 파일의 경로
return : (result: 논문 이름들 리스트, data: csv 전체 데이터 리스트)
def get_list_from_csv(str: path_csv)
"""

def get_list_from_csv(path_csv):
    result = []
    data = csv.reader(open(path_csv, 'r'))
    data = list(data)
    for line in data:
        result.append(line[2])
    print("Read CSV Done!")
    return (result, data)

"""
SEARCH_QUERY : google scholar에 검색하려고 하는 문자열
return : 논문 PDF의 URL
def search(str : SEARCH_QUERY):
    1. SEARCH_QUERY를 google scholar에 검색
    2. 검색 결과를 html.parser 적용한 BeautifulSoup 객체를 반환
"""
def search(SEARCH_QUERY):
    # Google Scholar
    res = requests.get(url = GoogleURL.replace("SEARCH_QUERY", SEARCH_QUERY), headers=HEADERS, verify=False)
    soup = BeautifulSoup(res.content, "html.parser")
    return soup

"""
soup : search() 함수에서 리턴된 값.
return : PDF URL
def retrievePDF(BeautifulSoup : soup):
    1. 첫 번째 검색결과에서 PDF가 존재하면 PDF URL을 리턴
    2. PDF 존재하지 않으면, 해당 검색 결과 제목 부분으로 들어간 후에,
        들어간 페이지에서 doi url을 정규표현식으로 검색함.
        이후에 sci-hub와 연결하여 생성한 PDF URL을 리턴
"""
def retrievePDF(soup):
    # 검색했을 때 첫 번째 뜨는 논문
    first = soup.select_one(".gs_r")
    pdf_paper = first.find("span", string="[PDF]")
    if pdf_paper:
        href = pdf_paper.parent.attrs['href']
        print("From Google Scholar: ", href)
        return href

    # [PDF] not exist.
    else:
        # 첫 번째 논문의 '논문 제목' 부분
        href2 = soup.select_one(".gs_ri .gs_rt a").attrs['href']
        if href2:
            # search doi URL
            res2 = requests.get(url = href2, verify=False)
            doi_URL = re.findall('https://doi[.]org/[^"]+', res2.text)[0]
            if doi_URL:
                # sci-hub 검색
                res3 = requests.get(url = sci_hub + doi_URL, verify=False)
                soup3 = BeautifulSoup(res3.content, "html.parser")
                pdf_src = soup3.select_one("#article embed").attrs['src']
                # //sci-hub.se/downloads/2019-09-13/71/..
                if pdf_src.find("https://") == 0:
                    pass
                else:
                    pdf_src = "https:" + pdf_src
                print("From sci-hub: ",pdf_src)
                return pdf_src
            else:
                raise Exception("Something Wrong..1")
        else:
            raise Exception("Something Wrong..2")

"""
soup : search() 함수에서 리턴된 값.
return : (int: year, int: citation) 튜플
def year_citation(BeautifulSoup: soup):
    첫 번째 검색 결과를 파싱하여, 연도와 인용 수 파싱
"""
def year_citation(soup):
    first = soup.select_one(".gs_r")
    # year, 예시) 2014 - Digital Investigation
    year = re.search("([\d]{4}) -", first.text)
    if year:                # ['2014 -', '2014']
        year = int(year[1])
    # citation
    citation = re.search("([\d]{1,4})회 인용", first.text)
    if citation:            # ['2048회 인용', '2048']
        citation = int(citation[1])

    # None -> 0
    year = 0 if type(year) != type(0) else year
    citation = 0 if type(citation) != type(0) else citation

    return (year, citation)    

"""
URL : pdf의 URL
save_name : 로컬 저장소에 저장되는 파일의 이름
def save(str: URL, str: save_name)
"""
def save(URL, save_name):
    try:
        file = requests.get(URL, stream = True, verify=False)
    except Exception as e:
        print("URL error..", URL, e)
        return False
    
    with open(save_name + ".pdf","wb") as pdf:
        for chunk in file.iter_content(chunk_size=1024):
            if chunk:
                pdf.write(chunk)
        print("Save PDF Done!", save_name[:60])
    
    return True

"""
MAIN START!
"""
(paper_list, data) = get_list_from_csv(path_csv)#[1:]
for idx, paper_name in enumerate(paper_list):
    # 목차 1줄 빼기 + 중복 작업 수행 X
    if idx == 0 or data[idx][4] == 'o':
        continue 
    try:
        soup = search(paper_name)
        paper_url = retrievePDF(soup)
        tag = data[idx][0]
        (year, citation) = year_citation(soup)
    except Exception as e:
        print(f"Error occured in search({paper_name[:20]})", e)

    # PDF 파일 저장
    save_result = None
    if 'paper_url' in vars(): # isset() in python, 예외 없이 성공했을 때에 다음을 진행
        print(f"[{tag}][{idx}][{year}년, 인용:{citation}]", end="")
        paper_name = paper_name.replace('/','')
        save_result = save(paper_url, "result/" + f"{tag}_{year}_{paper_name}")
        
    if save_result:
        # csv에 연도, 인용 추가
        data[idx][1] = year
        data[idx][3] = citation
        data[idx][4] = 'o'
        f = open(path_csv, 'w', newline='')
        wr = csv.writer(f)
        wr.writerows(data)