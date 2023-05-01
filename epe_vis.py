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
  if st.button('Установить количество SKU'):
    titles = {}
    cycle_times = {}
    changeover_times = {}
    for i in range(sku_quantity):
      titles[f'title{i}'] = st.text_input(f'Введите название продукта {i}', f'Продукт # {i}')
      cycle_times[f'cycle_time{i}'] = st.number_input('Установите время цикла единицы производства в минутах', 1)
      changeover_times[f'changeover_time{i}'] = st.number_input('Установите время переналадки с продукта {i} на продукт {i + 1} в минутах', 20)
    
st.title('Приложение по моделированию EPE')
titles
cycle_times
changeover_times
