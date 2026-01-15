import streamlit as st
import pandas as pd
import altair as alt
import time
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Gym Progress Dashboard",
    page_icon="💪",
    layout="wide"
)

# Title
st.title("💪 Gym Progress Dashboard")

# Metric Placeholders (for real-time update visual effect)
# We use a container to refresh just the data part or the whole app
placeholder = st.empty()

@st.cache_data(ttl=5)  # Cache data for 5 seconds to allow "real-time" feeling without reading disk every microsecond
def load_data():
    try:
        df = pd.read_csv("data/gym_data.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

def process_data(df):
    if df.empty:
        return pd.DataFrame()
        
    # Filter last 52 weeks
    end_date = df['date'].max()
    start_date = end_date - timedelta(weeks=52)
    df_filtered = df[df['date'] >= start_date].copy()
    
    # Add 'Week' column for grouping
    df_filtered['week'] = df_filtered['date'].dt.to_period('W').apply(lambda r: r.start_time)

    # Process Bodyweight (Mean per week)
    bw_df = df_filtered[df_filtered['category'] == 'Bodyweight']
    bw_weekly = bw_df.groupby('week')['value'].mean().reset_index()
    bw_weekly['category'] = 'Bodyweight'
    
    # Process Lifts (Max per week)
    lift_df = df_filtered[df_filtered['category'].isin(['Deadlift', 'Bench Press', 'Squat'])]
    lift_weekly = lift_df.groupby(['week', 'category'])['value'].max().reset_index()
    
    # Combine
    final_df = pd.concat([bw_weekly, lift_weekly])
    return final_df

def plot_metric(df, category, color):
    chart_data = df[df['category'] == category]
    
    if chart_data.empty:
        st.warning(f"No data for {category}")
        return

    # Create Altair chart
    chart = alt.Chart(chart_data).mark_line(point=True).encode(
        x=alt.X('week:T', title='Week', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('value:Q', title='Weight (kg)', scale=alt.Scale(zero=False)), # Zero=False to show progress better
        tooltip=['week', 'value'],
        color=alt.value(color)
    ).properties(
        title=f"{category} Progress (Last 52 Weeks)",
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)


# Main Loop for Real-Time Updates
# Streamlit auto-reruns on interaction, but for "always on" dashboard we can use a loop or st.empty with periodic refresh.
# However, standard Streamlit practice for auto-refresh is usually `st.empty()` or `st_autorefresh` component. 
# Here we will rely on basic Streamlit rerun capability if we want it to be "live".
# BUT: Streamlit effectively watches files. If "data/gym_data.csv" changes, Streamlit should detect it and ask to rerun or rerun if configured.
# To force it to look like a "live monitoring dashboard" we can add a loop.

# Let's try to just render once first, but add a "Last Updated" timestamp.
# If the user wants it to self-update without file changes (e.g. just polling), we can add a sleep loop.
# Given "dashboard has to refresh in real-time", I will add a poll loop.

while True:
    with placeholder.container():
        df_raw = load_data()
        
        if df_raw.empty:
            st.error("No data found in data/gym_data.csv")
        else:
            df_weekly = process_data(df_raw)
            
            # Layout
            col1, col2 = st.columns(2)
            
            with col1:
                plot_metric(df_weekly, "Bodyweight", "#3498db") # Blue
                plot_metric(df_weekly, "Bench Press", "#e74c3c") # Red
                
            with col2:
                plot_metric(df_weekly, "Squat", "#2ecc71") # Green
                plot_metric(df_weekly, "Deadlift", "#9b59b6") # Purple
                
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
    # Wait for a bit before refreshing
    # time.sleep(2) # 2 seconds refresh rate might be too aggressive for CSV reading, let's do 5 or 10
    # Actually, Streamlit's `st.rerun()` is the "modern" way to do this loop, but a simple while True with sleep works in simple scripts too if we use empty().
    time.sleep(5)