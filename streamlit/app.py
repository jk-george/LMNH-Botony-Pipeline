"""Script to create charts, connect to RDS, and connect to streamlit."""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import pymssql
import os
import boto3
from io import StringIO

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import pymssql
import os
import boto3
from io import StringIO

def get_connection() -> pymssql.Connection:
    """
    Connects to RDS database using credentials.
    """
    try:
        conn = pymssql.connect(
            server=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

def fetch_botanists() -> pd.DataFrame:
    """
    Fetch all botanists for populating the dropdown filter.
    """
    query = """
    SELECT DISTINCT 
        CONCAT(TRIM(botanist_forename), ' ', TRIM(botanist_surname)) AS botanist_name
    FROM alpha.botanist
    """
    conn = get_connection()
    if conn:
        try:
            botanists = pd.read_sql(query, conn)
            conn.close()
            return botanists
        except Exception:
            st.error("Error fetching botanists.")
            return pd.DataFrame()
    else:
        st.error("Unable to connect to the database.")
        return pd.DataFrame()

def fetch_data_by_minute(selected_minute: datetime) -> pd.DataFrame:
    """
    Fetch soil moisture and temperature data for the selected minute.
    """
    query = f"""
    SELECT 
        sd.recording_taken, 
        sd.last_watered,
        sd.soil_moisture, 
        sd.temperature, 
        p.plant_id, 
        ps.plant_name, 
        b.botanist_forename, 
        b.botanist_surname
    FROM alpha.sensor_data sd
    INNER JOIN alpha.plant p ON sd.plant_id = p.plant_id
    INNER JOIN alpha.plant_species ps ON p.scientific_name_id = ps.scientific_name_id
    INNER JOIN alpha.botanist b ON p.botanist_id = b.botanist_id
    WHERE sd.recording_taken BETWEEN '{selected_minute.strftime('%Y-%m-%d %H:%M:00')}' 
                                 AND DATEADD(SECOND, 59, '{selected_minute.strftime('%Y-%m-%d %H:%M:00')}')
    """
    conn = get_connection()
    if conn:
        try:
            data = pd.read_sql(query, conn)
            conn.close()
            return data
        except Exception as e:
            st.error(f"Error fetching data for the selected minute: {e}")
            return pd.DataFrame()
    else:
        st.error("Unable to connect to the database.")
        return pd.DataFrame()

def fetch_csv_from_s3(bucket: str, file_key: str) -> pd.DataFrame:
    """
    Connects to AWS S3, retrieves a CSV file, and loads it into a Pandas DataFrame.
    """
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket, Key=file_key)
        csv_data = response['Body'].read().decode('utf-8')
        return pd.read_csv(StringIO(csv_data))
    except Exception as e:
        st.error(f"Error fetching file from S3: {e}")
        return pd.DataFrame()

def create_dual_axis_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Create a dual-axis Altair line chart for temperature and soil moisture over time.
    """
    base = alt.Chart(data).encode(
        x=alt.X('recording_taken:T', title="Time"),
        tooltip=[
            alt.Tooltip('plant_name:N', title="Plant"),
            alt.Tooltip('recording_taken:T', title="Recorded At"),
            alt.Tooltip('temperature:Q', title="Temperature (°C)"),
            alt.Tooltip('soil_moisture:Q', title="Soil Moisture (%)")
        ]
    )

    moisture_line = base.mark_line(color='#1f77b4', strokeWidth=2).encode(
        y=alt.Y('soil_moisture:Q', title="Soil Moisture (%)", axis=alt.Axis(titleColor='#1f77b4')),
        color='plant_name:N'
    )

    temperature_line = base.mark_line(color='#ff7f0e', strokeWidth=2).encode(
        y=alt.Y('temperature:Q', title="Temperature (°C)", axis=alt.Axis(titleColor='#ff7f0e')),
        color='plant_name:N'
    )

    return alt.layer(moisture_line, temperature_line).resolve_scale(
        y='independent'
    ).properties(
        title="Soil Moisture and Temperature Trends by Plant",
        width=800,
        height=400
    )

def main():
    st.title("Plant Monitoring Dashboard")
    st.sidebar.header("Select Graph")

    graph_option = st.sidebar.radio("Choose a graph:", ("Graph 1: Real-time Monitoring", "Graph 2: S3 CSV Trends"))

    if graph_option == "Graph 1: Real-time Monitoring":
        botanists_df = fetch_botanists()
        if botanists_df.empty:
            st.warning("No botanists available.")
            return

        botanists = botanists_df['botanist_name'].tolist()
        selected_botanist = st.sidebar.selectbox("Select Botanist", options=botanists)

        now = datetime.now()
        past_10_minutes = [(now - timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:00') for i in range(10)]
        selected_minute = st.sidebar.selectbox("Select Minute", options=past_10_minutes)

        selected_minute_dt = datetime.strptime(selected_minute, '%Y-%m-%d %H:%M:00')
        data = fetch_data_by_minute(selected_minute_dt)

        if data.empty:
            st.warning("No data available for the selected botanist or minute.")
            return

        data['botanist_name'] = data['botanist_forename'] + ' ' + data['botanist_surname']
        filtered_data = data[data['botanist_name'] == selected_botanist]

        table_data = filtered_data[['plant_name', 'temperature', 'soil_moisture', 'recording_taken', 'last_watered', 'botanist_name']]

        st.subheader(f"Data for {selected_botanist} at {selected_minute}")
        st.write(table_data)

        st.subheader("Soil Moisture and Temperature")
        chart = create_chart(filtered_data)
        st.altair_chart(chart, use_container_width=True)

    elif graph_option == "Graph 2: S3 CSV Trends":
        bucket_name = "connect4-plant-data"
        file_key = "historical_plants_data.csv"

        data = fetch_csv_from_s3(bucket_name, file_key)
        if data.empty:
            st.warning("No data available from the CSV.")
            return

        data['recording_taken'] = pd.to_datetime(data['recording_taken'])

        st.subheader("Soil Moisture and Temperature Trends")
        chart = create_dual_axis_chart(data)
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Full Data")
        st.write(data)

if __name__ == "__main__":
    main()