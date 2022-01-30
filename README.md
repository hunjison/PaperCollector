# new_collector.py
논문 수집을 위한 코드.

This is PaperCollecter made by hunjison.

This Tool is based on Google Scholar.

I want to help all systematic literature reviews.

# Prerequisite

```python
import argparse
import requests
import re
from bs4 import BeautifulSoup
import csv
```

and..
- You should make `result/` folder at the location of `new_collector.py`
- You should fill the `HEADERS` in the code which is dictionary of the request header.


# Usage
`new_collector.py [-h] -type TYPE -number NUMBER`

```
  -h, --help      show this help message and exit
  -type TYPE      keyword or url
  -number NUMBER  A number of paper that you want to collect. 0 means "Collect ALL"
```

## Examples
`python3 new_collector.py -type keyword -number 1`

- It require multiline input which is keywords seperated by linebreaks.
- It will search each keyword on Google Scholar, download it, and scrape all metadata.

`python3 new_collector.py -type url -number 0`

- It require URL input of Google Scholar.
- This feature can do backward citation search.
- [input_example](https://scholar.google.com/scholar?cites=5596999640971043266&as_sdt=2005&sciodt=0,5&hl=ko) --> collect all papers which cite the target paper.

# Usage(한국어 버전)
한국인이 만든 영어를 보는 것이 제일 짜증나는 사람입니다.

### `keyword search`
- `-type`으로 `keyword`를 써주시면 됩니다.
- keyword는 키워드 검색이고, 줄바꿈으로 구분된 논문 이름이 input으로 들어갑니다.
- 실질적으로는 csv에 논문 이름을 쭉 정렬하신 뒤에, 복사-붙여넣기하여 input으로 넣으시면 줄바꿈으로 구분되어 예쁘게 들어갑니다.
- Google Scholar에서 검색어당 `number` 개 만큼의 논문을 다운로드합니다. (일반적으로 number는 1임.)
- 다운로드 뿐만 아니라, metadata(연도, 이름, 인용수, 출판사) 등이 `result/result.csv` 파일로 떨궈집니다.

### `url search`
- `-type`으로 `url`를 써주시면 됩니다.
- url input으로는 타겟 논문을 인용한 논문들이 모여져 있는 URL([input_example](https://scholar.google.com/scholar?cites=5596999640971043266&as_sdt=2005&sciodt=0,5&hl=ko))을 넣어주면 됩니다.
- 일반적으로 number는 0(ALL)을 주면 됩니다.
- 다운로드 뿐만 아니라, metadata(연도, 이름, 인용수, 출판사) 등이 `result/result.csv` 파일로 떨궈집니다.





