import streamlit as st
#import numpy as np
#import pandas as pd
#import plotly.graph_objects as go
#import plotly.express as px
#import random

st.markdown('''<a href="http://kaizen-consult.ru/"><img src='https://www.kaizen.com/images/kaizen_logo.png' style="width: 50%; margin-left: 25%; margin-right: 25%; text-align: center;"></a><p>''', unsafe_allow_html=True)

with st.sidebar:
  st.title('Введите данные для определение цикла EPE на данном оборудовании')
  sku_quantity = st.number_input("Укажите количество SKU, которые обрабатывает данное оборудование (комплекс)", value=10)
  titles = {}
  cycle_times = {}
  changeover_times = {}
  for i in range(sku_quantity):
    titles["string{0}".format(x)]
    title = st.text_input(f'Введите название продукта {i}', f'Продукт # {i}')
    cycle_time = st.number_input('Установите время цикла единицы производства в минутах', 1)
    changeover_time = st.number_input('Установите время переналадки с продукта {i} на продукт {i + 1} в минутах', 20)
    titles.append(title)
    cycle_times.append(cycle_times)
    changeover_times.append(changeover_time)
    
st.title('Приложение по моделированию EPE')
titles
cycle_times
changeover_times
