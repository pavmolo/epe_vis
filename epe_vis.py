import streamlit as st
import pandas as pd
import uuid
from fpdf import FPDF
import base64
import plotly.express as px
import plotly.figure_factory as ff
import datetime
from datetime import timedelta

input_row = st.columns(2)
with input_row[0]:
    work_minutes = st.number_input("Рабочих минут оборудования в сутки", 0)
with input_row[1]:
    uploaded_file = st.file_uploader("Выберите XLSX файл", accept_multiple_files=False)
if uploaded_file:
    data = pd.read_excel(uploaded_file)
    st.subheader("Показатели")
    co_in_a_day = work_minutes - (data['Дневной спрос'] * data['Время цикла']).sum()
    co_time_in_epe = data['Время переналадки'].sum()
    epe = co_time_in_epe / co_in_a_day
    if epe > 0:
        t_data = ((data['Дневной спрос'] * epe).astype('int')) * data['Время цикла']
        timeline_data = pd.concat([data['SKU'], t_data, data['Время переналадки']],axis=1)
        timeline_data.columns = ['SKU', 'Время производства', 'Время переналадки']
        stage = []
        time = []
        for sku in data['SKU']:
            stage.append(f'Производство {sku}')
            stage.append(f'Переналадка')
            time.append(timeline_data[timeline_data['SKU'] == sku]['Время производства'].iloc[0])
            time.append(timeline_data[timeline_data['SKU'] == sku]['Время переналадки'].iloc[0])
        finish_time = []
        start_time = []
        a = 0
        for i in time:
            start_time.append(a)
            a = a + i
            finish_time.append(a)
        #today = pd.Timestamp('today').strftime('%Y-%m-%d')
        #now = datetime.datetime.now()
        #time_data = pd.concat([pd.Series(stage), pd.Series(time), (now + pd.Series([pd.Timedelta(minutes=i) for i in start_time])), (now + pd.Series([pd.Timedelta(minutes=i) for i in finish_time]))],axis=1)
        #time_data['Start'] = pd.to_datetime(time_data['Start'])
        #time_data['Finish'] = pd.to_datetime(time_data['Finish'])
        time_data = pd.concat([pd.Series(stage), pd.Series(time), pd.Series(start_time), pd.Series(finish_time)],axis=1)
        time_data.columns = ['Task', 'Description', 'Start', 'Finish']
        timeline_data['Размер партии, шт.'] = timeline_data['Время производства'] / data['Время цикла']
        timeline_data = timeline_data[['SKU', 'Размер партии, шт.', 'Время производства', 'Время переналадки']]
        st.dataframe(data=timeline_data, use_container_width=True)
        #fig = px.timeline(time_data, x_start="Start", x_end="Finish", y="Task", Description = 'Время, мин.')
        fig = ff.create_gantt(time_data, bar_width = 0.4, index_col='Task')
        fig.update_layout(xaxis_type='linear', autosize=False)
        fig.layout.update({'title': 'Схема цикла EPE'})
        #fig.update_layout(hovermode="Description")
        fig.update_layout(xaxis_title="Линия времени в минутах", yaxis_title="Операция")
        fig.show()

        fig.update_yaxes(autorange="reversed")
        col1, col2 = st.columns(2)
        col1.metric("Времени остается на переналадки в день", f"{co_in_a_day} минут")
        col2.metric("Времени переналадки в цикле EPE", f"{co_time_in_epe} минут")
        col3, col4 = st.columns(2)
        col3.metric("EPE в днях", f"{epe} дней")
        col4.metric("EPE в минутах", f"{epe * work_minutes} минут")
        st.subheader("График EPE")
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)        
        st.subheader("Описание цикла EPE")
        st.dataframe(data=timeline_data, use_container_width=True)
    else:
        st.title(f"В цикле не остается времени на переналадку. EPE отрицательна и составляет {epe} дней")
