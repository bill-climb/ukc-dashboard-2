import streamlit as st
st.set_page_config(layout="wide")
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px 
import plotly.graph_objects as go
import random


df1 = None 
col1, col2 = st.columns([3,1])

with col1:
    st.title("🎈 UKC Dashboard")
    st.write(
        "Welcome to the UKC Dashboard."
    )

with col2:
    uploaded_file = None
    
    if uploaded_file is not None:
        df1=pd.read_excel(uploaded_file)
        st.table(df1)
    else:
        uploaded_file = st.file_uploader('upload ukc logbook file')

st.table(df1)



