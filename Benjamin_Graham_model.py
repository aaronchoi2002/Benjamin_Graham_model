# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 13:31:54 2022

@author: USER
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import streamlit as st 
import yfinance as yf
import plotly.graph_objects as go

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
df_bgm = pd.DataFrame()
# st.set_page_config(layout="wide")

st.title('Benjamin Graham model')



@st.cache()
def load_yield():
    # Get Average_Yield_AAA
    response = requests.get("https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield" ,headers=headers)
    soup = BeautifulSoup(response.text,"html.parser")
    Average_Yield_AAA = float(soup.find_all("td",{"class":"col-6"})[5].text.replace("%", ""))

    # Get AAA_Effective_Yield
    response = requests.get("https://ycharts.com/indicators/us_coporate_aaa_effective_yield" ,headers=headers)
    soup = BeautifulSoup(response.text,"html.parser")
    AAA_Effective_Yield = float(soup.find_all("td",{"class":"col-6"})[5].text.replace("%", ""))
    
    return(Average_Yield_AAA, AAA_Effective_Yield)

Average_Yield_AAA = load_yield()[0]
AAA_Effective_Yield = load_yield()[1]


# Display on web app
col1, col2= st.columns(2)
with col1:
    code_AAA_Effective_Yield = f"The AAA Effective Yield: {AAA_Effective_Yield}"
    st.code(code_AAA_Effective_Yield, language='python')

with col2:
    code_Average_Yield_AAA = f"The Average Yield AAA: {Average_Yield_AAA}"
    st.code(code_Average_Yield_AAA, language='python')





# age = st.slider('Margin of Safty', min_value =0.5, max_value = 1.0, step =0.05, value = 0.8)

tab1, tab2 = st.tabs(["Single Stock","Bulk Upload"])

with tab1:
    st.header("Single Stock")
    stock_code = st.text_input("Enter ticker here" , value="AAPL")
    
    @st.cache(allow_output_mutation=True)
    def load_stock_data(stock_code):
   
       #Get Growth Rate from Yahoo
       response = requests.get("https://finance.yahoo.com/quote/{}/analysis?p={}".format(stock_code,stock_code),headers=headers)
       soup = BeautifulSoup(response.text,"html.parser")
       if (len(soup.find_all(class_="Ta(end) Py(10px)"))<16):
           Grown = 0
       else:
           Grown_str = soup.find_all(class_="Ta(end) Py(10px)")[16].text
           Grown = float(Grown_str.replace("%", "")) if (Grown_str != 'N/A') else 0
 
 
       #Get EPS from Yahoo
       response = requests.get("https://finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch".format(stock_code,stock_code),headers=headers)
       soup = BeautifulSoup(response.text,"html.parser")
       eps_str = (soup.find_all(class_="Ta(end) Fw(600) Lh(14px)")[11].text)
       eps=float(eps_str) if eps_str !='N/A' else 0
     
       #Get Price from Yahoo
       stock_price = yf.download(stock_code, period="3y")
       print(1)
       price=round(stock_price["Close"][-1],2)        
   
       return(Grown, eps, price, stock_price)
    
    stock_data = load_stock_data(stock_code)
    Grown = stock_data[0]
    eps = stock_data[1]
    price = stock_data[2]
    stock_price= stock_data[3]
   
    col1, col2, col3= st.columns([1,0.8,1.3])
    with col1:
        print_price = f"Stock Price: {price}"
        st.code(print_price, language='python')
     
    with col2:
        print_eps = f"EPS: {eps}"
        st.code(print_eps, language='python')
     
    with col3:
        print_grown = f"Next 5 Years(annum): {Grown}"
        st.code(print_grown, language='python')
       
    BGM_value = round((eps * (8.5 + Grown)* Average_Yield_AAA)/AAA_Effective_Yield,2)    
    st.code(f"BGM value: {BGM_value}", language='python')
    Margin_of_safty = st.slider("Margin of safty", min_value=0.5, max_value=1.0, value=0.8, step=0.05)
    New_BGM = round(BGM_value *Margin_of_safty,2)
    st.code(f"BGM value (Margin_of_safty): {New_BGM}", language='python')
       
       
    stock_price["Date"] = stock_price.index
    stock_price.reset_index(inplace=True, drop=True)
    # stock_price
    # st.dataframe(stock_price)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=stock_price["Date"], open=stock_price["Open"], high=stock_price["High"], low=stock_price["Low"], close=stock_price["Close"]) )
    fig.add_hline(y=BGM_value, line_dash="dot" , annotation_text=f"BGM Value: {BGM_value}")
    fig.add_hline(y=New_BGM , annotation_text=f"Margin_of_safty: {New_BGM}")
    st.plotly_chart(fig)
       
with tab2:
    st.header("CSV File Upload")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])


    @st.cache(allow_output_mutation=True, suppress_st_warning=True)
    def load_bulk_data(dataframe):
        
        df = pd.read_csv(dataframe)
        stocks_code = df["Symbol"]
        numbers = st.empty()
        counter = 0
        number_of_stock = len(stocks_code)
        grown_list, eps_list, price_list = [],[],[]
        
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
              price=round(float(price),2) if price !='N/A' else 0           
            
              price_list.append(price)
              grown_list.append(Grown)
              eps_list.append(eps)
              
              counter = counter +1 
              with numbers.container():
                  st.write(f"processing stock {i} , {counter}/{number_of_stock}")
            
        return(price_list, grown_list, eps_list, stocks_code)
           
       
    # stocks_code = st.sidebar.text_input("Enter ticker here" , value="AAPL")
    load = st.button("Load Data")
    
    if "load_state" not in st.session_state:
        st.session_state.load_state = False
    
    
    if load or st.session_state.load_state:
        st.session_state.load_state = True
    
        if uploaded_file is not None:

            stock_data = load_bulk_data(uploaded_file)
            price_list = stock_data[0]
            grown_list = stock_data[1]
            eps_list = stock_data[2]
            stocks_code = stock_data[3]
            number_of_stock = len(stocks_code) 
                
            
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
            
            #end
     