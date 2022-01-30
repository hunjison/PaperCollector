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
- You should fill the HEADERS in the code which is dictionary of the request header.


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
