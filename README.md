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

  