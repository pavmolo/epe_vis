import streamlit as st
import pandas as pd
import uuid
from fpdf import FPDF
import base64
import plotly.express as px
import plotly.figure_factory as ff
import datetime
from datetime import timedelta


work_minutes = st.number_input("Рабочих минут оборудования в сутки", 0)

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

st.title("Данные по SKU на оборудовании")

for row in st.session_state["rows"]:
    row_data = generate_row(row)
    rows_collection.append(row_data)

menu = st.columns(2)

with menu[0]:
    st.button("Add Item", on_click=add_row)
    
if len(rows_collection) > 0:
    st.subheader("Данные")
    data = pd.DataFrame(rows_collection)
    data.rename(columns={"name": "SKU", "qty": "Дневной спрос", "cycle": "Время цикла", "co": "Время переналадки"}, inplace=True)
    st.dataframe(data=data, use_container_width=True)
    st.bar_chart(data=data, x="SKU", y="Дневной спрос")
    co_in_a_day = work_minutes - (data['Дневной спрос'] * data['Время цикла']).sum()
    co_time_in_epe = data['Время переналадки'].sum()
    epe = co_time_in_epe / co_in_a_day
    t_data = ((data['Дневной спрос'] * epe).astype('int')) * data['Время цикла']
    timeline_data = pd.concat([data['SKU'], t_data, data['Время переналадки']],axis=1)
    timeline_data.columns = ['SKU', 'Время производства', 'Время переналадки']
    st.dataframe(data=timeline_data, use_container_width=True)
    
    stage = []
    time = []
    for sku in data['SKU']:
        stage.append(f'Производство {sku}')
        stage.append(f'Переналадка с {sku}')
        time.append(timeline_data[timeline_data['SKU'] == sku]['Время производства'].iloc[0])
        time.append(timeline_data[timeline_data['SKU'] == sku]['Время переналадки'].iloc[0])
    finish_time = []
    start_time = []
    a = 0
    for i in time:
        start_time.append(a)
        a = a + i
        finish_time.append(a)
    today = pd.Timestamp('today').strftime('%Y-%m-%d')
    now = datetime.datetime.now()
    time_data = pd.concat([pd.Series(stage), pd.Series(time), (now + pd.Series([pd.Timedelta(minutes=i) for i in start_time])), (now + pd.Series([pd.Timedelta(minutes=i) for i in finish_time]))],axis=1)
    time_data.columns = ['Task', 'Время, мин.', 'Start', 'Finish']
    time_data['Start'] = pd.to_datetime(time_data['Start'])
    time_data['Finish'] = pd.to_datetime(time_data['Finish'])
    st.dataframe(data=time_data, use_container_width=True)
    
    fig = px.timeline(time_data, x_start="Start", x_end="Finish", y="Task")
    fig.update_yaxes(autorange="reversed")
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    st.title(f"Времени остается на переналадки в день: {co_in_a_day} минут")
    st.title(f"Времени переналадки в цикле EPE: {co_time_in_epe} минут")
    st.title(f"EPE = {epe} дней")
    
    



