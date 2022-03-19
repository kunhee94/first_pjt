import dart_fss as dart
import requests
import json
import re


api_key = '408e1771f5975d135bb7af91efe3daf8516cc749'

# 당기순이익
income = 0
# 발행주식수
total_stock = 0
# 자본총액
equity = 0


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


# 자본총계 찾기
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

print(EPS)
print(ROE)
