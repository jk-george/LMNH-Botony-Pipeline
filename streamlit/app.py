import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import pymssql
import os

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

def create_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Create an Altair chart showing soil moisture and temperature for the selected minute.
    """
    base = alt.Chart(data).encode(
        x=alt.X('plant_name:N', title="Plant Name"),
        tooltip=[
            alt.Tooltip('plant_name:N', title="Plant"),
            alt.Tooltip('botanist_name:N', title="Botanist"),
            alt.Tooltip('soil_moisture:Q', title="Soil Moisture (%)"),
            alt.Tooltip('temperature:Q', title="Temperature (°C)"),
            alt.Tooltip('recording_taken:T', title="Recorded At"),
            alt.Tooltip('last_watered:T', title="Last Watered"),
        ]
    )

    moisture_chart = base.mark_bar(color='#ccffcc').encode(
        y=alt.Y('soil_moisture:Q', title="Soil Moisture (bar) (%)"),
    )

    temperature_chart = base.mark_circle(color='#008000', size=100).encode(
        y=alt.Y('temperature:Q', title="Temperature (dot) (°C)"),
    )

    return alt.layer(moisture_chart, temperature_chart).resolve_scale(
        y='independent'
    ).properties(
        title="Soil Moisture and Temperature by Plant",
        width=800,
        height=400
    )

def main():
    st.title("Plant Monitoring by Minute")
    st.sidebar.header("Filter Options")

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

if __name__ == "__main__":
    main()
