"""
input csv 예시
---------------------------------------------------
연도         |   이름               |   인용수
---------------------------------------------------
            |  FlowDroid ..       |     
---------------------------------------------------
"""

"""
목표 : csv의 이름(1번 열)을 가지고,
1) scholar.google.com 과 sci-hub.se 사이트로부터 논문을 다운로드
2) csv 파일에서 연도, 인용 수 필드 채우기

사용자 입력
1) request header : 구글 탐지 우회
2) csv 파일 경로
3) .py 파일과 동일 경로에 /result 폴더 생성해주어야 함.
"""

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

# request header. 구글 보안 탐지 우회(반드시 추가 필요)
HEADERS = {}

"""
path_csv : csv 파일의 경로
return : 논문 이름들로 구성된 리스트
def get_list_from_csv(str: path_csv)
"""

def get_list_from_csv(path_csv):
    result = []
    data = csv.reader(open(path_csv, 'r'))
    for line in data:
        result.append(line[1])
    print("Read CSV Done!")
    return result

"""
SEARCH_QUERY : google scholar에 검색하려고 하는 문자열
return : 논문 PDF의 URL
def search(str : SEARCH_QUERY):
    1. SEARCH_QUERY를 google scholar에 검색
    2. 검색 후 첫 번째 검색결과에서 PDF가 존재하면 PDF URL을 리턴
    3. PDF 존재하지 않으면, 해당 검색 결과 제목 부분으로 들어간 후에,
        들어간 페이지에서 doi url을 정규표현식으로 검색함.
        이후에 sci-hub와 연결하여 생성한 PDF URL을 리턴
"""
def search(SEARCH_QUERY):
    # Google Scholar
    res = requests.get(url = GoogleURL.replace("SEARCH_QUERY", SEARCH_QUERY), headers=HEADERS, verify=False)
    soup = BeautifulSoup(res.content, "html.parser")

    # 검색했을 때 첫 번째 뜨는 논문
    pdf_paper = soup.find("span", string="[PDF]")
    if pdf_paper:
        href = pdf_paper.parent.attrs['href']
        print("From Google Scholar: ", href)
        return href

    # [PDF] not exist.
    else:
    #print("HERE")
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
                pdf_src = "https:" + pdf_src
                print("From sci-hub: ",pdf_src)
                return pdf_src
            else:
                raise Exception("Something Wrong..1")
        else:
            raise Exception("Something Wrong..2")

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
        return
    
    with open(save_name + ".pdf","wb") as pdf:
        for chunk in file.iter_content(chunk_size=1024):
            if chunk:
                pdf.write(chunk)
        print("Save PDF Done!", save_name[:60])

"""
MAIN START!
"""
path_csv = ""
paper_list = get_list_from_csv(path_csv)[1:]
for idx, paper_name in enumerate(paper_list):
    try:
        paper_url = search(paper_name)
    except Exception as e:
        print(f"Error occured in search({paper_name[:20]})", e)
    # isset() in python, 예외 없이 성공했을 때에 다음을 진행
    if 'paper_url' in vars():
        print(f"[{idx}]", end="")
        paper_name = paper_name.replace('/','')
        save(paper_url, "result/" + paper_name)
        #폴더....