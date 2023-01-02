# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 13:31:54 2022

@author: USER
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import streamlit as st 

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
df_bgm = pd.DataFrame()

st.title('Benjamin Graham model')


# Get Average_Yield_AAA

response = requests.get("https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield" ,headers=headers)
soup = BeautifulSoup(response.text,"html.parser")
Average_Yield_AAA = float(soup.find_all("td",{"class":"col-6"})[5].text.replace("%", ""))



# Get AAA_Effective_Yield

response = requests.get("https://ycharts.com/indicators/us_coporate_aaa_effective_yield" ,headers=headers)
soup = BeautifulSoup(response.text,"html.parser")
AAA_Effective_Yield = float(soup.find_all("td",{"class":"col-6"})[5].text.replace("%", ""))

code_AAA_Effective_Yield = f"The AAA Effective Yield: {AAA_Effective_Yield}"
st.code(code_AAA_Effective_Yield, language='python')
code_Average_Yield_AAA = f"The Average Yield AAA: {Average_Yield_AAA}"
st.code(code_Average_Yield_AAA, language='python')


uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if st.button("Process"):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    

        stocks_code = df["Symbol"]
        number_of_stock = len(df["Symbol"])
        
        grown_list, eps_list, price_list = [],[] ,[]
        with st.spinner('Wait for it..., it may take serval minutes'):
            numbers = st.empty()
            counter = 0
            for i in stocks_code:
          
              #Get Growth Rate from Yahoo
              response = requests.get("https://finance.yahoo.com/quote/{}/analysis?p={}".format(i,i),headers=headers)
              soup = BeautifulSoup(response.text,"html.parser")
              if (len(soup.find_all(class_="Ta(end) Py(10px)"))<16):
                  Grown = 0
              else:
                  Grown = soup.find_all(class_="Ta(end) Py(10px)")[16].text
                  Grown = float(Grown.replace("%", "")) if (Grown != 'N/A') else 0
            
            
              #Get EPS from Yahoo
              response = requests.get("https://finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch".format(i,i),headers=headers)
              soup = BeautifulSoup(response.text,"html.parser")
              eps = (soup.find_all(class_="Ta(end) Fw(600) Lh(14px)")[11].text)
              eps=float(eps) if eps !='N/A' else 0
            
              #Get Price from Yahoo
              response = requests.get("https://finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch".format(i,i),headers=headers)
              soup = BeautifulSoup(response.text,"html.parser")
              price = soup.find(class_="Fw(b) Fz(36px) Mb(-4px) D(ib)").text
              price=float(price) if price !='N/A' else 0           
              
              counter = counter +1 
              with numbers.container():
                  st.write(f"processing stock {i} , {counter}/{number_of_stock}")
            
       
              price_list.append(price)
              grown_list.append(Grown)
              eps_list.append(eps)
            
            df_bgm = pd.DataFrame(stocks_code)
            df_bgm["Price"] = price_list
            df_bgm["Grown"] = grown_list
            df_bgm["EPS"] = eps_list
            df_bgm["BGM_value"] = round((df_bgm["EPS"]  * (8.5 + df_bgm["Grown"])* Average_Yield_AAA)/AAA_Effective_Yield,2)
            df_bgm["BGM/price"] = round(df_bgm["BGM_value"]/df_bgm["Price"],2)
            df_bgm["BGM_90%"] = round(0.9*df_bgm["BGM_value"],2)
            df_bgm["BGM_80%"] = round(0.8*df_bgm["BGM_value"],2)
            df_bgm = df_bgm[["Symbol","Price", "BGM/price", "BGM_value", "BGM_90%", "BGM_80%", "Grown", "EPS" ]]
            
            st.dataframe(data=df_bgm)
    
            df_bgm_csv = df_bgm.to_csv().encode('utf-8')
    
            st.download_button(
            label="Download data as CSV",
            data=df_bgm_csv,
            file_name='bgm.csv',
            mime='text/csv',)
     