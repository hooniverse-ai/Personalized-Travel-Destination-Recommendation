# 사실상 여행 동기 및 여행 목적은 하나만 있어도 동작할 수 있어야하지 않을까 ? 매칭 정확도는 조금 떨어질 수 있어도, 이용자 편의상 한개만 있어도 동작할 수 있는 프로그램이 만들어지면 좋을 것 같음.
# 
import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state for storing schedule
if 'schedule' not in st.session_state:
    st.session_state.schedule = pd.DataFrame(columns=['날짜', '일정', '위치'])

# Display schedule
st.title("여행 일정 플래너")
st.header("현재 일정")

# Add destinations from 여행지추천.py
if 'selected_destinations' in st.session_state and st.session_state.selected_destinations:
    new_destinations = st.session_state.selected_destinations
    st.write("추가된 추천 여행지 목록:")
    for destination in new_destinations:
        st.write(f"- {destination}")
    
    # Button to add destinations to schedule
    if st.button("추천 여행지를 일정에 추가"):
        for destination in new_destinations:
            new_entry = pd.DataFrame({
                '날짜': [datetime.now().date()],  # Default to today's date, can be changed by user
                '일정': [destination],
                '위치': ["추천 여행지"]  # Default location, can be customized
            })
            st.session_state.schedule = pd.concat([st.session_state.schedule, new_entry], ignore_index=True)
        
        # Clear selected destinations after adding to schedule
        st.session_state.selected_destinations = []
# Display the updated schedule
if not st.session_state.schedule.empty:
    st.dataframe(st.session_state.schedule.sort_values(by=['날짜']).reset_index(drop=True), width=800)
else:
    st.write("현재 추가된 일정이 없습니다.")
