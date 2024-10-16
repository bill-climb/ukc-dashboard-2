import streamlit as st
st.set_page_config(layout="wide")
import altair as alt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px 
import plotly.graph_objects as go
import random
from wordcloud import WordCloud
from collections import Counter

# grades ordered for the dataframe
grades = {
    "grade rank": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
              21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
              41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
              61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84],
    "overall grade": ["M", "D", "HD", "VD", "HVD", "S", "MS", "HS", "MVS", "VS", "HVS", "E1", "E2", "E3", 
              "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "f2", "f2+", "f3", "f3+", "f4", "f4+", "f5", 
              "f5+", "f6A", "f6A+", "f6B", "f6B+", "f6C", "f6C+", "f7A", "f7A+", "f7B", "f7B+", "f7C", 
              "f7C+", "f8A", "f8A+", "f8B", "f8B+", "f8C", "f8C+", "f9A", "f9A+", "f9B", "4", "4a", "4b", 
              "4c", "5", "5a", "5b", "5c", "6a", "6a+", "6b", "6b+", "6c", "6c+", "7a", "7a+", "7b", 
              "7b+", "7c", "7c+", "8a", "8a+", "8b", "8b+", "8c", "8c+", "9a", "9a+", "9b", "9b+", 
              "9c", "9c+"]
}

# Create a DataFrame from the grades dictionary
df_graderank = pd.DataFrame(grades)


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
        
        df = pd.merge(df, df_graderank, on='overall grade', how='left')
        df['grade rank']=df['grade rank'].replace(np.nan, 0)
        df['grade rank']=df['grade rank'].astype(int)
        return df
    
    
    df = load_data()
    #calculating top grades sent
    style_options = ['Lead', 'Sent']
    style_category_options = ['dog', 'dnf']
    #only show routes lead
    df_filtered = df[df['style'].isin(style_options)] 
    #remove dogged or dnf
    df_filtered = df_filtered[~df_filtered['style category'].isin(style_category_options)] 
    df_top_grades=df_filtered.groupby(['Grade Type'])['grade rank'].max().reset_index(name='max grade rank')
    df_top_grades_summary=pd.merge(df_graderank, df_top_grades, left_on='grade rank', right_on='max grade rank', how='inner')
    #print(df_top_grades_summary)
    df_top_grades=pd.merge(df_filtered, df_top_grades, left_on='grade rank', right_on='max grade rank', how='inner')
    #print(df_top_grades)

    df_max_trad = df_top_grades_summary['overall grade'][df_top_grades_summary['Grade Type'] == 'Trad'].values[0]
    df_max_sport = df_top_grades_summary['overall grade'][df_top_grades_summary['Grade Type'] == 'Sport'].values[0]
    df_max_boulder = df_top_grades_summary['overall grade'][df_top_grades_summary['Grade Type'] == 'Bouldering'].values[0]
    
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
    # calculate the counts by grade type by year
    year_route_type=df.groupby(['year','Grade Type']).size().reset_index(name='counts')
    # Calculate the total counts in 2024
    df_2024 = year_route_type[year_route_type['year'] == 2024]
    total_counts_2024 = df_2024['counts'].sum()
    # Find the grade type with the most counts in 2024
    max_grade_type_2024 = df_2024.loc[df_2024['counts'].idxmax(), 'Grade Type']
    annual_logs_text = (
        f"You logged {total_counts_2024} climbs in 2024. Your favourite type of climbing was {max_grade_type_2024}"
    )
    #accumulation by date
    df_accumulated = df.groupby('Date').size().reset_index(name='counts')
    range_start = '2024-01-01'
    range_end = '2024-12-31'
    # Create a complete date range from 2024-01-01 to 2024-12-31
    full_range = pd.date_range(start=range_start, end=range_end, freq='D')
    df_full_range = pd.DataFrame(full_range, columns=['Date'])
    # Merge the original DataFrame with the full date range to include missing dates
    df_accumulated_merged = pd.merge(df_full_range, df_accumulated, on='Date', how='left')
    
    # Fill missing 'value' entries with 0
    df_accumulated_merged['counts'] = df_accumulated_merged['counts'].fillna(0)
    
    # Calculate cumulative sum of the 'value' column
    df_accumulated_merged['cumulative_sum'] = df_accumulated_merged['counts'].cumsum().astype(int)
    
    
    
    
    #content
    st.write(annual_logs_text)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h1 style='text-align: center;'>2024 Profile</h1>", unsafe_allow_html=True)
        st.line_chart(data=df_accumulated_merged,x='Date',y='cumulative_sum')

    
    with col2:
        st.markdown("<h1 style='text-align: center;'>Yearly Profile</h1>", unsafe_allow_html=True)
        st.bar_chart(data=year_route_type,  x='year', y='counts', color='Grade Type', use_container_width=True)
   
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Trad", value=df_max_trad)
    with col2:
        st.metric(label="Sport", value=df_max_sport)
    with col3:
        st.metric(label="Trad", value=df_max_boulder)

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
    wctext = df['Crag name'].values
    # Count the frequency of each crag name
    word_frequencies = Counter(wctext)
    
    # Generate the word cloud using the frequency dictionary
    wc = WordCloud().generate_from_frequencies(word_frequencies)
    
    # Create a matplotlib figure
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")  # Hide axes
    
    # Display the word cloud in Streamlit
    st.pyplot(fig)
        
    st.table(df)
    st.table(year_route_type)


