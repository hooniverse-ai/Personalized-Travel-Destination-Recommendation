# 여행지추천.py
import streamlit as st
import pandas as pd
from catboost import CatBoostRegressor, Pool, CatBoostError
import os

# 모델 파일 경로
model_path = "catboost_model_v2.bin"

# 모델 파일 존재 여부 확인 및 로드
if not os.path.exists(model_path):
    st.error("모델 파일이 존재하지 않습니다. 메인 페이지를 통해 모델 파일을 다운로드하세요.")
    st.stop()

model = CatBoostRegressor()
try:
    model.load_model(model_path)
    # st.success("모델이 성공적으로 로드되었습니다!")
except CatBoostError as e:
    # st.error(f"모델을 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# Streamlit app UI setup
st.title("당신에게 추천드릴 여행지는 바로!")

# Check if 'traveler' data exists in session state
if "traveler" in st.session_state:
    traveler = st.session_state.traveler

    # Load train data for recommendations
    df_train = pd.read_csv('train_add_last.csv')
    area_names = df_train['VISIT_AREA_NM'].unique()  # 방문지 이름 중복 제거

    # Filter area names based on user-selected region and city
    user_region = traveler.get('INTEGRATED_REGION')
    user_city = traveler.get('INTEGRATED_CITY')       # Assuming city information is also included

    if user_region and user_city:
        filtered_area_names = df_train[(df_train['INTEGRATED_REGION'] == user_region) & (df_train['INTEGRATED_CITY'] == user_city)]['VISIT_AREA_NM'].unique()
    else:
        filtered_area_names = area_names

    # Create DataFrame with traveler data and filtered area names for batch prediction
    input_data_list = []
    for area in filtered_area_names:
        input_data = dict(traveler)
        input_data['VISIT_AREA_NM'] = area
        input_data_list.append(input_data)

    # Convert list of dictionaries to DataFrame for prediction
    input_df = pd.DataFrame(input_data_list)

    categorical_features_names = [
        'INTEGRATED_REGION', 'INTEGRATED_CITY',
        'GENDER', 'MVMN_NM',
        'NTvsCT', 'EXPLODvsCHPLOD', 'RESTvsACT', 'UNKvsK',
        'TRAVEL_MISSION_CHECK1', 'TRAVEL_MISSION_CHECK2',
        'TRAVEL_MOTIVE_1', 'TRAVEL_MOTIVE_2', 'budget', 'VISIT_AREA_NM'
    ]

    # Convert categorical features to string type
    for feature in categorical_features_names:
        if feature in input_df.columns:
            input_df[feature] = input_df[feature].astype(str)

    # Create a Pool object for batch prediction
    prediction_pool = Pool(data=input_df, cat_features=categorical_features_names)

    # Perform batch prediction and get top 10 recommendations
    try:
        input_df['PREDICTION'] = model.predict(prediction_pool)
        if st.button('새로고침'):
            top_recommendations = input_df[['VISIT_AREA_NM', 'PREDICTION']].iloc[input_df['PREDICTION'].argsort()[::-1]].iloc[10:20]
        else:
            top_recommendations = input_df[['VISIT_AREA_NM', 'PREDICTION']].iloc[input_df['PREDICTION'].argsort()[::-1]].head(10)
        st.write(f"추천 여행지 목록 (총 {len(top_recommendations)}개):")

        # Display each recommendation with a checkbox
        selected_destinations = []
        for index, row in top_recommendations.iterrows():
            if st.checkbox(row['VISIT_AREA_NM']):
                selected_destinations.append(row['VISIT_AREA_NM'])

        # Save selected destinations to session state for 플래너.py
        if st.button("선택한 여행지 일정에 추가"):
            st.session_state.selected_destinations = selected_destinations
            st.success("선택한 여행지가 일정에 추가되었습니다!")
            st.switch_page(page="pages/Planner.py")

    except CatBoostError as e:
        st.warning(f"예측을 수행하는 동안 오류가 발생했습니다: {e}")
        st.stop()

else:
    st.warning("추천 결과를 확인하려면 먼저 사용자 입력 페이지에서 데이터를 입력하세요.")
