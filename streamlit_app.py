import pandas as pd
import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

uploaded_file = None
while uploaded_file is None:
    uploaded_file = st.file_uploader('upload ukc logbook file')
df1=pd.read_excel(uploaded_file)
st.table(df1)



#uploaded_file = None

#if uploaded_file is not None:
#    df1=pd.read_excel(uploaded_file)
#    st.table(df1)
#else:
#    st.warning('you need to upload ukc logbook excel file.')
#    uploaded_file = st.file_uploader('upload ukc logbook file')

