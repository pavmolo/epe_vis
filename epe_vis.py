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
if "rows" not in st.session_state:
    st.session_state["rows"] = []

rows_collection = []

def add_row():
    element_id = uuid.uuid4()
    st.session_state["rows"].append(str(element_id))


def remove_row(row_id):
    st.session_state["rows"].remove(str(row_id))


def generate_row(row_id):
    row_container = st.empty()
    row_columns = row_container.columns((5, 3, 3, 3, 1))
    row_name = row_columns[0].text_input("SKU на оборудовании", key=f"txt_{row_id}")
    row_qty = row_columns[1].number_input("Дневной спрос", step=1, key=f"nbr_{row_id}")
    row_cycle = row_columns[2].number_input("Время цикла", step=2, key=f"time_{row_id}")
    row_co = row_columns[3].number_input("Время переналадки", step=3, key=f"co_{row_id}")
    row_columns[4].button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])
    return {"name": row_name, "qty": row_qty, "cycle": row_cycle, "co": row_co}

if uploaded_file:
    menu = st.columns(2)
    with menu[0]:
        st.button("Добавить SKU", on_click=add_row)
    
if len(rows_collection) == 0:
    if uploaded_file:
        data = pd.read_excel(uploaded_file)
        st.subheader("Показатели")
        co_in_a_day = work_minutes - (data['Дневной спрос'] * data['Время цикла']).sum()
        co_time_in_epe = data['Время переналадки'].sum()
        epe = co_time_in_epe / co_in_a_day
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
        #st.dataframe(data=time_data, use_container_width=True)
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

if len(rows_collection) > 0:
    st.title("Данные по SKU на оборудовании")

    for row in st.session_state["rows"]:
        row_data = generate_row(row)
        rows_collection.append(row_data)

    
    st.subheader("Показатели")
    data = pd.DataFrame(rows_collection)
    data.rename(columns={"name": "SKU", "qty": "Дневной спрос", "cycle": "Время цикла", "co": "Время переналадки"}, inplace=True)
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
        #st.dataframe(data=time_data, use_container_width=True)
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

        #st.title(f"Времени остается на переналадки в день: {co_in_a_day} минут")
        #st.title(f"Времени переналадки в цикле EPE: {co_time_in_epe} минут")
        #st.title(f"EPE = {epe} дней")
        #st.title(f"EPE = {epe * work_minutes} минут")
        
        
        
    else:
        st.title(f"В цикле не остается времени на переналадку. EPE отрицательна и составляет {epe} дней")
