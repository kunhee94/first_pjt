import dart_fss as dart

# Open DART API KEY 설정
api_key = '발급받은 키'
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