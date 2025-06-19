# main_page.py
import streamlit as st
import pandas as pd
import requests
import os

# GitHub Release 또는 Google Drive 모델 파일 URL
model_url = "https://github.com/SDJuns/Project_Application/releases/download/model_catboost/catboost_model_v2.bin" 
model_path = "catboost_model_v2.bin"  # 다운로드할 모델 파일 경로

# 모델 다운로드 함수
def download_model(url, save_path):
    if not os.path.exists(save_path):  # 모델 파일이 없는 경우에만 다운로드
        st.info("Downloading model file. Please wait...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success("Model downloaded successfully!")
        except Exception as e:
            st.error(f"Failed to download model. Error: {e}")
            raise e

# 모델 다운로드
try:
    download_model(model_url, model_path)
except Exception as e:
    st.error("Model could not be downloaded. Please check the URL and try again.")
    st.stop()  # 다운로드 실패 시 앱 중단


# Streamlit app UI setup
st.title("여행지 추천 인공지능✈️")

# Load train data for recommendations
df_train = pd.read_csv('train_add_last.csv')
area_names = df_train[['VISIT_AREA_NM']].drop_duplicates()  # 방문지 이름 중복 제거

# Updated Region and City dictionary
do_regions = {
    '강원특별자치도': ['춘천시', '원주시', '강릉시', '동해시', '속초시', '삼척시', '홍천군', '횡성군', '영월군', '평창군', '정선군', '철원군', '화천군', '양구군', '인제군', '고성군', '양양군'],
    '충청남도': ['천안시', '아산시', '공주시', '보령시', '서산시', '논산시', '계룡시', '당진시', '금산군', '부여군', '서천군', '청양군', '홍성군', '예산군', '태안군'],
    '충청북도': ['청주시', '충주시', '제천시', '보은군', '옥천군', '영동군', '진천군', '괴산군', '음성군', '단양군', '증평군'],
    '경상북도': ['포항시', '경주시', '김천시', '안동시', '구미시', '영주시', '영천시', '상주시', '문경시', '경산시', '의성군', '청송군', '영양군', '영덕군', '청도군', '고령군', '성주군', '칠곡군', '예천군', '봉화군', '울진군', '울릉군'],
    '경상남도': ['창원시', '김해시', '진주시', '통영시', '사천시', '밀양시', '거제시', '양산시', '의령군', '함안군', '창녕군', '고성군', '남해군', '하동군', '산청군', '함양군', '거창군', '합천군'],
    '전북특별자치도': ['전주시', '익산시', '군산시', '정읍시', '남원시', '김제시', '완주군', '진안군', '무주군', '장수군', '임실군', '순창군', '고창군', '부안군'],
    '전라남도': ['목포시', '여수시', '순천시', '나주시', '광양시', '담양군', '곡성군', '구례군', '고흥군', '보성군', '화순군', '장흥군', '강진군', '해남군', '영암군', '무안군', '함평군', '영광군', '장성군', '완도군', '진도군', '신안군'],
    '경기도': ['성남시', '수원시', '김포시', '고양시', '용인시', '안양시', '부천시', '광명시', '평택시', '과천시', '오산시', '시흥시', '군포시', '의왕시', '하남시', '이천시', '안산시', '의정부시', '파주시', '양주시', '동두천시', '구리시', '남양주시', '여주시', '광주시', '포천시', '양평군', '가평군', '연천군', '화성시'],
    '제주특별자치도': ['제주시', '서귀포시']
}

si_regions = [
    '서울특별시', '인천광역시', '세종특별자치시', '대구광역시', '대전광역시', '부산광역시', '울산광역시'
]

# 데이터의 행정구역 컬럼에서 고유한 행정구역을 가져오기
unique_regions = df_train['INTEGRATED_REGION'].unique()

# 사용자 입력을 통해 행정구역 선택
traveler = {}
traveler['INTEGRATED_REGION'] = st.selectbox("어디로 가고 싶으신가요?", unique_regions)

# 선택된 행정구역에 따라 시, 군 선택 표시 여부 결정
if traveler['INTEGRATED_REGION'] in do_regions:
    traveler['INTEGRATED_CITY'] = st.selectbox("시, 군을 입력해주세요!", do_regions[traveler['INTEGRATED_REGION']], key='city_select')
else:
    traveler['INTEGRATED_CITY'] = '미선택'  # '시' 행정구역의 경우 '미선택'으로 대체

for column in ['INTEGRATED_REGION', 'INTEGRATED_CITY', 'AGE_GRP', 'GENDER', 'TRAVEL_MONTH', 'TRAVEL_PERIOD', 'NTvsCT', 'EXPLODvsCHPLOD', 'RESTvsACT', 'UNKvsK', 'MVMN_NM',
               'TRAVEL_MISSION_CHECK1', 'TRAVEL_MISSION_CHECK2', 'TRAVEL_MOTIVE_1', 'TRAVEL_MOTIVE_2', 'budget']:
    if column == 'INTEGRATED_REGION':
        traveler[column] = traveler['INTEGRATED_REGION']  # 이미 선택된 값을 그대로 사용
    elif column == 'INTEGRATED_CITY':
        traveler[column] = traveler['INTEGRATED_CITY']  # 이미 선택된 값을 그대로 사용
    elif column == 'AGE_GRP':
        traveler[column] = st.selectbox("연령대:", list(range(20, 70, 10)))  # 연령대 20~60대까지
    elif column == 'GENDER':
        traveler[column] = st.selectbox("성별:", ['남', '여'])
    elif column == 'TRAVEL_MONTH':
        traveler[column] = st.selectbox("여행 월:", list(range(4, 12)))  # 월 4~11
    elif column == 'TRAVEL_PERIOD':
        traveler[column] = st.selectbox("여행 기간:", list(range(1, 8)))  # 기간 1~7일
    elif column == 'NTvsCT':
        traveler[column] = st.selectbox("자연vs도시 선호:", ['자연선호', '상관없음', '도시선호'])
    elif column == 'EXPLODvsCHPLOD':
        traveler[column] = st.selectbox("비싼숙소vs저렴한숙소 선호:", ['비싼숙소 선호', '상관없음', '저렴한숙소 선호'])
    elif column == 'RESTvsACT':
        traveler[column] = st.selectbox("휴식vs활동 선호:", ['휴식 선호', '상관없음', '활동 선호'])
    elif column == 'UNKvsK':
        traveler[column] = st.selectbox("안 알려진 곳vs알려진 곳 선호:", ['안 알려진 곳 선호', '상관없음', '알려진 곳 선호호'])
    elif column == 'MVMN_NM':
        traveler[column] = st.selectbox("이동수단:", ['대중교통 등', '자가용'])
    elif column == 'TRAVEL_MISSION_CHECK1':
        traveler[column] = st.selectbox("여행 주목적:", 
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 21, 22, 23, 24, 25, 26, 27, 28],
    format_func=lambda x: {
        1: "쇼핑",
        2: "테마파크, 놀이시설, 동/식물원 방문",
        3: "역사 유적지 방문",
        4: "시티투어",
        5: "야외 스포츠, 레포츠 활동",
        6: "지역 문화예술/공연/전시시설 관람",
        7: "유흥/오락(나이트라이프)",
        8: "캠핑",
        9: "지역 축제/이벤트 참가",
        10: "온천/스파",
        11: "교육/체험 프로그램 참가",
        12: "드라마 촬영지 방문",
        13: "종교/성지 순례",
        21: "Well-ness 여행",
        22: "SNS 인생샷 여행",
        23: "호캉스 여행",
        24: "신규 여행지 발굴",
        25: "반려동물 동반 여행",
        26: "인플루언서 따라하기 여행",
        27: "친환경 여행(플로깅 여행)",
        28: "등반 여행"
    }[x])
    elif column == 'TRAVEL_MISSION_CHECK2':
        traveler[column] = st.selectbox("여행 부목적:", 
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 21, 22, 23, 24, 25, 26, 27, 28],
    format_func=lambda x: {
        1: "쇼핑",
        2: "테마파크, 놀이시설, 동/식물원 방문",
        3: "역사 유적지 방문",
        4: "시티투어",
        5: "야외 스포츠, 레포츠 활동",
        6: "지역 문화예술/공연/전시시설 관람",
        7: "유흥/오락(나이트라이프)",
        8: "캠핑",
        9: "지역 축제/이벤트 참가",
        10: "온천/스파",
        11: "교육/체험 프로그램 참가",
        12: "드라마 촬영지 방문",
        13: "종교/성지 순례",
        21: "Well-ness 여행",
        22: "SNS 인생샷 여행",
        23: "호캉스 여행",
        24: "신규 여행지 발굴",
        25: "반려동물 동반 여행",
        26: "인플루언서 따라하기 여행",
        27: "친환경 여행(플로깅 여행)",
        28: "등반 여행"
    }[x])
    elif column == 'TRAVEL_MOTIVE_1':
        traveler[column] = st.selectbox("여행동기1:", 
    [1, 2, 3, 4, 5, 6, 7],
    format_func=lambda x: {
        1: "일상적인 환경 및 역할에서의 탈출, 지루함 탈피",
        2: "쉴 수 있는 기회, 육체 피로 해결 및 정신적인 휴식",
        3: "진정한 자아 찾기 또는 자신을 되돌아볼 기회 찾기",
        4: "SNS 사진 등록 등 과시",
        5: "운동, 건강 증진 및 충전",
        6: "새로운 경험 추구",
        7: "역사 탐방, 문화적 경험 등 교육적 동기"
    }[x])
    elif column == 'TRAVEL_MOTIVE_2':
        traveler[column] = st.selectbox("여행동기2:", 
    [1, 2, 3, 4, 5, 6, 7],
    format_func=lambda x: {
        1: "일상적인 환경 및 역할에서의 탈출, 지루함 탈피",
        2: "쉴 수 있는 기회, 육체 피로 해결 및 정신적인 휴식",
        3: "진정한 자아 찾기 또는 자신을 되돌아볼 기회 찾기",
        4: "SNS 사진 등록 등 과시",
        5: "운동, 건강 증진 및 충전",
        6: "새로운 경험 추구",
        7: "역사 탐방, 문화적 경험 등 교육적 동기"
    }[x])
    elif column == 'budget':
        traveler[column] = st.number_input("예산 (원):", value=0)

# 추천받기 버튼
if st.button("추천받기✈️"):
    if traveler['budget'] == 0:
        st.warning("예산을 입력해주세요.")
    else:
        # 데이터 저장 후 추천 페이지로 이동
        st.session_state.traveler = traveler
        # 추천 페이지로 이동
        st.switch_page("pages/Recommendation.py")
