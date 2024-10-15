import streamlit as st
st.set_page_config(layout="wide")
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px 
import plotly.graph_objects as go
import random

col1, col2 = st.columns([3,1])

with col1:
    st.title("🎈 UKC Dashboard")
    st.write(
        "Welcome to the UKC Dashboard."
    )

with col2:
    uploaded_file = st.file_uploader('upload ukc logbook file',label_visibility="collapsed")


if uploaded_file is None:
    st.write('upload a file')
else:
    @st.cache_data
    def load_data():
        df = pd.read_excel(uploaded_file)
        df[['style','style category']] = df['Style'].str.split(' ',expand=True)
        df=df.drop(columns=['Style'])
        df.rename(columns={'Partner(s)': 'Partner'}, inplace=True)
        #add index
        df['log_id'] = df.index + 1
        #convert date
        df['Date']=pd.to_datetime(df['Date'], format='%d/%b/%y')
        df["first star"]= df["Grade"].str.find('*')
        df[['overall grade','technical grade', 'star rating']] = df['Grade'].str.split(' ',expand=True)
        df['year'] = pd.DatetimeIndex(df['Date']).year
        df['year'] = pd.to_numeric(df['year'])
    
        return df
    
    
    df = load_data()
    
    # we want to count logs by partner
    
    # Split the 'Partner' column by the delimiter ','
    df_split = df.assign(Partner=df['Partner'].str.split(','))
    
    # Explode the 'Partner' column to create a new row for each partner
    df_split = df_split.explode('Partner')
    
    # Strip any leading/trailing whitespace from the 'Partner' column
    df_split['Partner'] = df_split['Partner'].str.strip()
    
    # Reorder the columns for clarity
    df_split = df_split[['log_id', 'Grade Type', 'Partner']]
    
    #creating counts of logs by partner
    
    partner=df_split.groupby(['Partner']).size().reset_index(name='counts')
    partner=partner.sort_values('counts', ascending=False)
    
    #counts of logs by route type
    route_type=df_split.groupby(['Grade Type']).size().reset_index(name='counts')
    
    ##creating counts of logs by partner by grade type
    
    partner_type=df_split.groupby(['Grade Type','Partner']).size().reset_index(name='counts')
    
    #counts of logs by style
    style=df.groupby(['style']).size().reset_index(name='counts')
    style=style.sort_values('counts', ascending=False)
    
    #sort
    route_type=route_type.sort_values('counts', ascending=True)
    partner_type=partner_type.sort_values('counts', ascending=True)
    partner=partner.sort_values('counts', ascending=True)
    
    # Find the partner with the most counts
    max_counts_row = partner.loc[partner['counts'].idxmax()]
    most_counts_partner = max_counts_row['Partner']
    most_counts_value = max_counts_row['counts']
    
    # Generate summary text
    summary_text = f"You climbed the most with {most_counts_partner} - {most_counts_value} logs!"
    
    # Generate humorous text based on the number of partners
    num_partners = len(partner)
    
    if num_partners < 5:
        funny_text = f"You only climbed with {num_partners} people this year. Looks like a small gathering! Do you need some more friends?!"
    elif num_partners < 10:
        funny_text = f"You climbed with {num_partners} people this year. Enough for a fun game night i suppose!"
    else:
        funny_text = f"You climbed with {num_partners} people this year. Wow, we've got a whole crowd! It's like a party in here!"
    
    # Combine the summary and humorous text
    partner_text = summary_text + " " + funny_text
    
    # Find the style with the most counts
    most_common_style_row = style.loc[style['counts'].idxmax()]
    most_common_style = most_common_style_row['style']
    most_common_counts = most_common_style_row['counts']
    
    # Extract counts for specific styles
    tr_counts = style.loc[style['style'] == 'TR', 'counts'].values[0]
    solo_counts = style.loc[style['style'] == 'Solo', 'counts'].values[0]
    
    # Generate summary text
    summary_text = (
        f"You normally climbed {most_common_style} with {most_common_counts} logs. "
        f"You've done {solo_counts} Solo climbs and {tr_counts} TR climbs."
    )
    # Generate summary text
    summary_text = f"You normally climbed {most_common_style} with {most_common_counts} logs."
    
    # Options for humorous text based on the most common style
    funny_text_options = {
        'Lead': [
            "Leading the way, I see! Who needs a safety net?",
            "Wow, you really like to live on the edge—literally!",
            "Looks like you're the captain of the climbing ship!"
        ],
        '2nd': [
            "So you enjoy following the leader? Nice to have a trusty guide!",
            "Being a second means you get the best view of the show!",
            "Ah, the trusty 2nd—always there for support!"
        ],
        'Sent': [
            "Sent it? I bet it felt great to conquer that route!",
            "Congratulations on sending! That’s what I call a high-five!",
            "Looks like you’re all about those epic sends!"
        ],
        'AltLd': [
            "AltLd? Ah, the art of leading and following at the same time!",
            "You're a true multi-tasker in the climbing world!",
            "Sounds like you’re all about the best of both worlds!"
        ],
        'TR': [
            "Top roping, huh? That's like driving with training wheels!",
            "TR? It's all fun and games until someone falls!",
            "Looks like you're keeping it safe up there!"
        ],
        'Solo': [
            "Solo climbing? Living dangerously, I see!",
            "No ropes? You must really trust your skills!",
            "You must have nerves of steel to climb solo!"
        ],
        '-': [
            "What does '-' mean? Is it a secret climbing style?",
            "Looks like you’re keeping it mysterious with that dash!",
            "Ah, the unknown! The wild card of climbing styles!"
        ],
    }
    
    # Randomly select humorous text for the most common style
    funny_text = random.choice(funny_text_options[most_common_style])
    
    # Randomly select humorous texts for TR and Solo
    tr_humor = random.choice(funny_text_options['TR'])
    solo_humor = random.choice(funny_text_options['Solo'])
    
    # Combine the required texts into the final output
    climb_style_text = (
        summary_text + " " + funny_text
    )
    
    year_route_type=df.groupby(['year','Grade Type']).size().reset_index(name='counts')
    
    
    
    #content
    st.bar_chart(data=year_route_type,  x='year', y='counts', color='Grade Type', use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(partner_text)
        partner_fig=px.bar(partner,x='counts',y='Partner', orientation='h')
        st.write(partner_fig)
    
    with col2:
        st.write("Types of climbing")   
        labels = route_type['Grade Type']
        values = route_type['counts']
        route_fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                     insidetextorientation='radial'
                                    )])
        st.write(route_fig)
    
    with col3:
        st.write("Climbing Styles")   
        labels = style['style']
        values = style['counts']
        style_fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                     insidetextorientation='radial'
                                    )])
        st.write(style_fig)
    ''
    
    ''
    
    
    
    
    
    st.table(df)
    st.table(year_route_type)


