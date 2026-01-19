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
        
    # Filter last 52 weeks (approx 365 days)
    end_date = df['date'].max()
    start_date_52w = end_date - timedelta(weeks=52)
    df_filtered = df[df['date'] >= start_date_52w].copy()
    
    # Determine granularity based on filtered data range (or total range, but filtered makes sense)
    # If we have very little data (e.g. < 30 days), show Daily.
    # Otherwise show Weekly.
    
    data_range_days = (df_filtered['date'].max() - df_filtered['date'].min()).days
    
    if data_range_days < 30:
        granularity = 'Daily'
        # Group by Date
        df_filtered['time_segment'] = df_filtered['date'] # Already datetime
        x_axis_format = '%b %d'
        x_axis_title = 'Date'
    else:
        granularity = 'Weekly'
        # Group by Week
        df_filtered['time_segment'] = df_filtered['date'].dt.to_period('W').apply(lambda r: r.start_time)
        x_axis_format = '%b %Y'
        x_axis_title = 'Week'

    # Process Bodyweight (Mean)
    bw_df = df_filtered[df_filtered['category'] == 'Bodyweight']
    bw_agg = bw_df.groupby('time_segment')['value'].mean().reset_index()
    bw_agg['category'] = 'Bodyweight'
    
    # Process Lifts (Max)
    lift_df = df_filtered[df_filtered['category'].isin(['Deadlift', 'Bench Press', 'Squat'])]
    lift_agg = lift_df.groupby(['time_segment', 'category'])['value'].max().reset_index()
    
    # Combine
    final_df = pd.concat([bw_agg, lift_agg])
    return final_df, granularity, x_axis_format, x_axis_title

def plot_metric(df, category, color, x_format, x_title):
    chart_data = df[df['category'] == category]
    
    if chart_data.empty:
        st.warning(f"No data for {category}")
        return

    # Create Altair chart
    chart = alt.Chart(chart_data).mark_line(point=True).encode(
        x=alt.X('time_segment:T', title=x_title, axis=alt.Axis(format=x_format)),
        y=alt.Y('value:Q', title='Weight (kg)', scale=alt.Scale(zero=False)),
        tooltip=['time_segment', 'value'],
        color=alt.value(color)
    ).properties(
        title=f"{category}",
        height=300
    ).interactive()
    
    st.altair_chart(chart, width='stretch')


# Main Loop for Real-Time Updates
while True:
    with placeholder.container():
        df_raw = load_data()
        
        if df_raw.empty:
            st.info("Waiting for data in data/gym_data.csv...")
        else:
            df_processed, granularity, x_fmt, x_lbl = process_data(df_raw)
            
            st.subheader(f"View Mode: {granularity}")
            
            # Layout
            col1, col2 = st.columns(2)
            
            with col1:
                plot_metric(df_processed, "Bodyweight", "#3498db", x_fmt, x_lbl) # Blue
                plot_metric(df_processed, "Bench Press", "#e74c3c", x_fmt, x_lbl) # Red
                
            with col2:
                plot_metric(df_processed, "Squat", "#2ecc71", x_fmt, x_lbl) # Green
                plot_metric(df_processed, "Deadlift", "#9b59b6", x_fmt, x_lbl) # Purple
                
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
    time.sleep(5)