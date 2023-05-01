import streamlit as st
import pandas as pd
import uuid
from fpdf import FPDF
import base64
import plotly.express as px

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
    
    timeline_data = (data['Дневной спрос'] / epe).astype('int')
    st.dataframe(data=timeline_data, use_container_width=True)
    
    st.title(f"Времени остается на переналадки в день: {co_in_a_day} минут")
    st.title(f"Времени переналадки в цикле EPE: {co_time_in_epe} минут")
    st.title(f"EPE = {epe} дней")
    
    



