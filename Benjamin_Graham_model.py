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
    
    
    
    #get Data from google drive CSV Barry file 
    #https://docs.google.com/spreadsheets/d/1hB4fa284hStCPLRuL379M-GOY_iu0ISayVUCE3M-Vp0/edit?usp=sharing
    # sheet_id ="1hB4fa284hStCPLRuL379M-GOY_iu0ISayVUCE3M-Vp0"
    # df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
    
        stocks_code = df["Symbol"]
        
    
        
        # Get Average_Yield_AAA
        
        # response = requests.get("https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield" ,headers=headers)
        # soup = BeautifulSoup(response.text,"html.parser")
        # Average_Yield_AAA = float(soup.find_all("td",{"class":"col-6"})[5].text.replace("%", ""))
        
        
        # print(AAA_Effective_Yield)
        # print(Average_Yield_AAA)
        
        
        
        grown_list, eps_list= [],[] 
        with st.spinner('Wait for it...'):
        
            for i in stocks_code:
              print(i)
              
              #Get Growth Rate from Yahoo
              response = requests.get("https://finance.yahoo.com/quote/{}/analysis?p={}".format(i,i),headers=headers)
              soup = BeautifulSoup(response.text,"html.parser")
              if (len(soup.find_all(class_="Ta(end) Py(10px)"))<16):
                  Grown = 0
              else:
                  Grown = soup.find_all(class_="Ta(end) Py(10px)")[16].text
                  Grown = float(Grown.replace("%", "")) if (Grown != 'N/A') else 'N/A'
            
            
              #Get EPS from Yahoo
              response = requests.get("https://finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch".format(i,i),headers=headers)
              soup = BeautifulSoup(response.text,"html.parser")
              eps = (soup.find_all(class_="Ta(end) Fw(600) Lh(14px)")[11].text)
              eps=float(eps) if eps !='N/A' else "N/A"
            
              grown_list.append(Grown)
              eps_list.append(eps)
            
            df_bgm = pd.DataFrame(stocks_code)
            df_bgm["Grown"] = grown_list
            df_bgm["EPS"] = eps_list
            
            st.dataframe(data=df_bgm)