### 1일차

- 어디서 재무제표를 긁어오나 여기저기 둘러보던 중 `OPEN DART`라는 사이트라는 금감원에서 제공하는 사이트 발견 

- `dart-fss` 라는 라이브러리를 활용해야 해서 [공식문서](https://dart-fss.readthedocs.io/en/latest/index.html#)로 사용법 공부

  - `pip install dart-fss` 이걸로 라리브러리 다운받음  
  - 아래와 같은방법으로 원하는 회사의 종목코드 추출하기 가능

  ```python
  import dart_fss as dart
  
  # Open DART API KEY 설정
  api_key='발급받은 키'
  dart.set_api_key(api_key=api_key)
  
  # DART 공시된 회사 리스트 반환
  corp_list = dart.get_corp_list()
  # 회사 명칭을 이용한 검색
  company = corp_list.find_by_corp_name(input(), exactly=True)[0]
  # 회사 정보 딕셔너리로 저장
  a = company.to_dict()
  # 회사의 종목번호 추출
  code = a.get('stock_code')
  print(code)
  ```


### 2일차

- 종목코드를 활용해서 검색하려 했으나 dart에서 제공하는 기업의 고유번호로 검색해야한다는걸 알게되었음
- stock_code가 아닌 corp_code를 불러와서 해결
- 내가 필요한건 회사의 주요계정들임
- 아래와 같은 코드로 사업보고서 불러오기가 가능했음

```python
URL_saub = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'
PARAMS = {
  'crtfc_key': f'{api_key}', # API 인증키
  'corp_code': f'{corp_code}', # 회사 고유번호
  'bsns_year': '2021', # 사업연도(4자리)
  'reprt_code': '11011', # 사업보고서
}
resp = requests.get(url=URL_saub, params=PARAMS)
```

- 없는 회사를 검색할 시 오류가 나는것을 해결하고 싶었음
- requests의 Response객체가 리턴되고 Response객체는 status_code를 반환하며 이것이 http요청에 대한 응답코드라는 것을 알게됨, 응답코드가 200이라면 정상이니 아래와 같이 코드 작성

```python
if resp.status_code == 200:
```

- 제이슨 데이터 보면서 코딩하기 힘들었는데 파이썬에 json이라는 내장함수가 있고 그걸 활용하면 된다는 걸 배움 단, json.dumps로 변환하면 타입이 str로 바뀌니 개발과정에서 눈으로 데이터 확인할 때 사용

```python
# http 정상응답시 처리
if resp.status_code == 200:
    # json 데이터로 받아준다.
    data_json = resp.json()
    # 눈디버깅을 위해서 json.dumps 사용
    data_str = json.dumps(data_json, indent=4, ensure_ascii=False)
```

- 가져온 데이터의 리스트 순회하면서 당기순이익 받기 성공

```python
# 당기순이익 가져오기
    # status가 정상이라면
    if data_json['status'] == "000":
        # 리스트 받아와서
        detail = data_json['list']
        for x in detail:
            # 연결재무제표의 손익계산서상의 당기순이익 검색
            if x['fs_div'] == 'CFS' and x['sj_div'] == 'IS' and x['account_nm'] == '당기순이익':
                income =  x['thstrm_amount']
    # 아니면 오류메시지 출력
    else:
        print(data_json['message'])
```

- 같은 방식으로 발행 주식 수도 받는것에 성공
- EPS계산을 위해 진행하던 도중 자릿수 마다 `,`가 들어있는 문자열이라는것을 확인
- 해결을 위해 re호출하고 `re.sub(r'[^0-9]', '', x['istc_totqy'])`으로 해결
- EPS 만들기 성공 아래 오늘까지 진행 상황

```python
import dart_fss as dart
import requests
import json
import re


api_key = '내 api키'

# 당기순이익
income = 0
# 발행주식수
total_stock = 0


# 고유번호 추출하기
# Open DART API KEY 설정
dart.set_api_key(api_key=api_key)
# DART 공시된 회사 리스트 반환
corp_list = dart.get_corp_list()
# 회사 명칭을 이용한 검색
company = corp_list.find_by_corp_name(input(), exactly=True)[0]
# 회사 정보 딕셔너리로 저장
a = company.to_dict()
# 회사의 고유번호 추출
corp_code = a.get('corp_code')



# 사업보고서 확인하기
URL_saub = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'
PARAMS = {
  'crtfc_key': f'{api_key}', # API 인증키
  'corp_code': f'{corp_code}', # 회사 고유번호
  'bsns_year': '2021', # 사업연도(4자리)
  'reprt_code': '11011', # 사업보고서
}
resp = requests.get(url=URL_saub, params=PARAMS)
# http 정상응답시 처리
if resp.status_code == 200:
    # json 데이터로 받아준다.
    data_json = resp.json()
    # 눈디버깅을 위해서 json.dumps 사용
    data_str = json.dumps(data_json, indent=4, ensure_ascii=False)


# 당기순이익 가져오기
    # status가 정상이라면
    if data_json['status'] == "000":
        # 리스트 받아와서
        detail = data_json['list']
        for x in detail:
            # 연결재무제표의 손익계산서상의 당기순이익 검색
            if x['fs_div'] == 'CFS' and x['sj_div'] == 'IS' and x['account_nm'] == '당기순이익':
                income = int(re.sub(r'[^0-9]', '', x['thstrm_amount']))
    # 아니면 오류메시지 출력
    else:
        print(data_json['message'])


# 발행 주식 수 찾기
URL_stock = 'https://opendart.fss.or.kr/api/stockTotqySttus.json'
PARAMS2 = {
  'crtfc_key': f'{api_key}',    # API 인증키
  'corp_code': f'{corp_code}',  # 회사 고유번호
  'bsns_year': '2021',  # 사업연도(4자리)
  'reprt_code': '11011',    # 사업보고서
}
resp2 = requests.get(url=URL_stock, params=PARAMS2)
# http 정상응답시 처리
if resp2.status_code == 200:
    # json 데이터로 받아준다.
    stock_json = resp2.json()
    # 눈디버깅을 위해서 json.dumps 사용
    stock_str = json.dumps(stock_json, indent=4, ensure_ascii=False)
    # status가 정상이라면
    if stock_json['status'] == "000":
        # 리스트 받아와서
        detail = stock_json['list']
        for x in detail:
            # 보통주의 발행주식 충수 찾기
            if x['se'] == '보통주':
                total_stock = int(re.sub(r'[^0-9]', '', x['istc_totqy']))
    # 아니면 오류메시지 출력
    else:
        print(stock_json['message'])

EPS = income/total_stock

```

### 3일차

- ROE가 필요해서 아래의 코드로 자본총액을 구함

```python
# 자본총액 찾기
URL_equity = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
PARAMS3 = {
    'crtfc_key': f'{api_key}',    # API 인증키
    'corp_code': f'{corp_code}',  # 회사 고유번호
    'bsns_year': '2021',  # 사업연도(4자리)
    'reprt_code': '11011',    # 사업보고서
    'fs_div': 'CFS',
}
resp3 = requests.get(url=URL_equity, params=PARAMS3)
# http 정상응답시 처리
if resp3.status_code == 200:
    # json 데이터로 받아준다.
    equity_json = resp3.json()
    # 눈디버깅을 위해서 json.dumps 사용
    equity_str = json.dumps(equity_json, indent=4, ensure_ascii=False)
    # print(asset_str)
    # status가 정상이라면
    if equity_json['status'] == "000":
        # 리스트 받아와서
        detail = equity_json['list']
        for x in detail:
            # 보통주의 발행주식 충수 찾기
            if x['sj_div'] == 'BS' and x['account_nm'] == '자본총계':
                x_str = json.dumps(x, indent=4, ensure_ascii=False)
                equity = int(re.sub(r'[^0-9]', '', x['thstrm_amount']))
    # 아니면 오류메시지 출력
    else:
        print(equity_json['message'])

ROE = income/equity
```

### 4일차 

- 이 코드로 어찌되었든 사이트를 만들어야하는데 과연 이게 장고의 views.py에서 실행해도 될까라는 의문이 생김. 마침 다음주 장고 시험도 있겠다 공부 삼아 미리 기본적인 틀을 짜두는것도 나쁘지 않겠다 싶어 한번 장고로 프로젝트 진행시켜봤음
- 기본적인 틀 완성 이후 `index` 페이지에서 이용자에게 주식명을 요청받아 간단하게 그 회사의 당기순이익, 자본총계, 발행주식총수와 이를 활용하여 계산한 ROE와 EPS를 보여주는 식으로 작성 
- 아래 index.html

```html
{% extends 'base.html' %}
{% block content %}
<form action="{% url 'stock:result' %}" method="POST">
  {% csrf_token %}
  <label for="name">주식이름</label>
  <input type="text" id="name" name="name">
</form>

{% endblock content %}
```

- 사용자에게 보여줄 결과창인 result.html

```html
{% extends 'base.html' %}
{% block content %}
결과 창입니다.
<br>
{{income}}
<br>
{{equity}}
<br>
{{total_stock}}
<br>
{{EPS}}
<br>
{{ROE}}
{% endblock content %}
```

- 의외로 views.py는 금방 만들었다 미리 파이참에서 디버깅해가며 만들어두었더니 그냥 request로 주식명 받아주는 부분만 수정하면 깔끔하게 실행되는것을 확인할 수 있었다.

```python
from django.shortcuts import render
import dart_fss as dart
import requests
import json
import re
# Create your views here.
api_key = '내 api키'

def index(request):
    return render(request, 'stock/index.html')

def result(request):
    # 당기순이익
    income = 0
    # 발행주식수
    total_stock = 0
    # 발행 주식 수 찾기
    equity = 0
    name = request.POST.get('name')
    # 고유번호 추출하기
    # Open DART API KEY 설정
    dart.set_api_key(api_key=api_key)
    # DART 공시된 회사 리스트 반환
    corp_list = dart.get_corp_list()
    # 회사 명칭을 이용한 검색
    company = corp_list.find_by_corp_name(name, exactly=True)[0]
    # 회사 정보 딕셔너리로 저장
    a = company.to_dict()
    # 회사의 고유번호 추출
    corp_code = a.get('corp_code')
    # 사업보고서 확인하기
    URL_saub = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'
    PARAMS = {
    'crtfc_key': f'{api_key}', # API 인증키
    'corp_code': f'{corp_code}', # 회사 고유번호
    'bsns_year': '2021', # 사업연도(4자리)
    'reprt_code': '11011', # 사업보고서
    }
    resp = requests.get(url=URL_saub, params=PARAMS)
    if resp.status_code == 200:
    # json 데이터로 받아준다.
        data_json = resp.json()
        if data_json['status'] == "000":
            # 리스트 받아와서
            detail = data_json['list']
            for x in detail:
                # 연결재무제표의 손익계산서상의 당기순이익 검색
                if x['fs_div'] == 'CFS' and x['sj_div'] == 'IS' and x['account_nm'] == '당기순이익':
                    income = int(re.sub(r'[^0-9]', '', x['thstrm_amount']))
        # 아니면 오류메시지 출력
        else:
            print(data_json['message'])
    
    # 당기순이익 가져오기
    # status가 정상이라면
    if data_json['status'] == "000":
        # 리스트 받아와서
        detail = data_json['list']
        for x in detail:
            # 연결재무제표의 손익계산서상의 당기순이익 검색
            if x['fs_div'] == 'CFS' and x['sj_div'] == 'IS' and x['account_nm'] == '당기순이익':
                income = int(re.sub(r'[^0-9]', '', x['thstrm_amount']))
    # 아니면 오류메시지 출력
    else:
        print(data_json['message'])


    # 발행 주식 수 찾기
    URL_stock = 'https://opendart.fss.or.kr/api/stockTotqySttus.json'
    PARAMS2 = {
    'crtfc_key': f'{api_key}',    # API 인증키
    'corp_code': f'{corp_code}',  # 회사 고유번호
    'bsns_year': '2021',  # 사업연도(4자리)
    'reprt_code': '11011',    # 사업보고서
    }
    resp2 = requests.get(url=URL_stock, params=PARAMS2)
    # http 정상응답시 처리
    if resp2.status_code == 200:
        # json 데이터로 받아준다.
        stock_json = resp2.json()
        # status가 정상이라면
        if stock_json['status'] == "000":
            # 리스트 받아와서
            detail = stock_json['list']
            for x in detail:
                # 보통주의 발행주식 충수 찾기
                if x['se'] == '보통주':
                    total_stock = int(re.sub(r'[^0-9]', '', x['istc_totqy']))
        # 아니면 오류메시지 출력
        else:
            print(stock_json['message'])

    # 자본총액 찾기
    URL_equity = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
    PARAMS3 = {
        'crtfc_key': f'{api_key}',    # API 인증키
        'corp_code': f'{corp_code}',  # 회사 고유번호
        'bsns_year': '2021',  # 사업연도(4자리)
        'reprt_code': '11011',    # 사업보고서
        'fs_div': 'CFS',
    }
    resp3 = requests.get(url=URL_equity, params=PARAMS3)
    # http 정상응답시 처리
    if resp3.status_code == 200:
        # json 데이터로 받아준다.
        equity_json = resp3.json()
        # print(asset_str)
        # status가 정상이라면
        if equity_json['status'] == "000":
            # 리스트 받아와서
            detail = equity_json['list']
            for x in detail:
                # 보통주의 발행주식 충수 찾기
                if x['sj_div'] == 'BS' and x['account_nm'] == '자본총계':
                    x_str = json.dumps(x, indent=4, ensure_ascii=False)
                    equity = int(re.sub(r'[^0-9]', '', x['thstrm_amount']))
        # 아니면 오류메시지 출력
        else:
            print(equity_json['message'])
    EPS = income/total_stock
    ROE = income/equity
    context = {
        'income': income,
        'total_stock': total_stock,
        'equity': equity,
        'EPS': EPS,
        'ROE': ROE,
    }

    return render(request, 'stock/result.html', context)
```

- 실행은 잘되는 result창을 보여주기 위해 로딩되는 시간이 조금 걸린다.
- `corp_list = dart.get_corp_list()` 이부분에서 시간이 걸리는것 같음
- 혹시 모든 리스트 안받고 입력값에 대한 정보만 따로 가져올수없을까 싶었으나 타입이`dart_fss.corp.corp_list.CorpList`였기에 불가능했음

































































































