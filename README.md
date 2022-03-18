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
- 내가 필요한건 회서의 주요계정들임
- 아래와 같은 코드로 주요계정 불러오기가 가능했음
- 없는 회사를 검색할 시 오류가 나는것을 해결하고 싶었음
- requests의 Response객체가 리턴되고 Response객체는 status_code를 반환하며 이것이 http요청에 대한 응답코드라는 것을 알게됨, 응답코드가 200이라면 정상이니 아래와 같이 코드 작성
- 제이슨 데이터 보면서 코딩하기 힘들었는데 파이썬에 json이라는 내장함수가 있고 그걸 활용하면 된다는 걸 배움 단, json.dumps로 변환하면 타입이 str로 바뀌니 개발과정에서 눈으로 데이터 확인할 때 사용
- 가져온 데이터의 리스트 순회하면서 당기순이익 받기 성공
- 같은 방식으로 발행 주식 수도 받는것에 성공
- EPS계산을 위해 진행하던 도중 자릿수 마다 `,`가 들어있는 문자열이라는것을 확인
- 해결을 위해 re호출하고 `re.sub(r'[^0-9]', '', x['istc_totqy'])`으로 해결
- EPS 만들기 성공

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

