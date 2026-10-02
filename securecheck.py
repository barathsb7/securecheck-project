import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.title("My SecureCheck Project Logs")

def load_clean_data():
    raw_df = pd.read_csv("traffic_stops.csv", nrows=5000)

    raw_df['driver_gender'] = raw_df['driver_gender'].fillna('Unknown')
    raw_df['driver_race'] = raw_df['driver_race'].fillna('Unknown')
    raw_df['violation'] = raw_df['violation'].fillna('Not Specified')

    raw_df['search_conducted'] = raw_df['search_conducted'].fillna(False).astype(bool)
    raw_df['is_arrested'] = raw_df['is_arrested'].fillna(False).astype(bool)

    median_age = raw_df['driver_age'].median()
    raw_df['driver_age'] = raw_df['driver_age'].apply(lambda x: median_age if x < 16 or x > 95 else x)
    raw_df['driver_age'] = raw_df['driver_age'].astype(int)

    
    raw_df['violation'] = raw_df['violation'].str.strip().str.capitalize()
    raw_df['stop_outcome'] = raw_df['stop_outcome'].fillna('No Action').str.strip().str.capitalize()

    return raw_df

data = load_clean_data()

sql_connection = sqlite3.connect("securecheck.db")
data.to_sql(name="traffic_stops", con=sql_connection, if_exists="replace", index=False)
sql_connection.close()

st.sidebar.header("🔎 Search Filters")
violation_choice = st.sidebar.selectbox(
    "Select Violation Type",
    ["All", "Speeding", "Dui", "Equipment", "Seatbelt", "Signal", "Other"]
)

gender_choice = st.sidebar.radio(
    "Select Driver Gender",
    ["All", "M", "F"]
)


query = "SELECT * FROM traffic_stops WHERE 1=1"

if violation_choice != "All":
    query += f" AND violation = '{violation_choice}'"
if gender_choice != "All":
    query += f" AND driver_gender = '{gender_choice}'"


db = sqlite3.connect("securecheck.db")
filtered_data = pd.read_sql(query, db)
db.close()

col1, col2, col3 = st.columns(3)

col1.metric("🚔 Incidents Tracked", len(filtered_data))
col2.metric("🔍 Total Searches", int(filtered_data['search_conducted'].sum() if not filtered_data.empty else 0))
col3.metric("🤝 Total Arrests", int(filtered_data['is_arrested'].sum() if not filtered_data.empty else 0))

st.markdown("---")

st.subheader("📋 Active Check Post Digital Logs Ledger")
st.dataframe(filtered_data, use_container_width=True)

st.write("Arrests without any search conducted:", len(filtered_data[(filtered_data['is_arrested'] == True) & (filtered_data['search_conducted'] == False)]))

st.markdown("---")
st.subheader("📊 Check Post Operational Analytics")


left_chart_col, right_chart_col = st.columns(2)


with left_chart_col:
    if not filtered_data.empty:
        fig_age = px.histogram(
            filtered_data, 
            x="driver_age", 
            color="is_arrested", 
            barmode="group", 
            title="Age Distribution vs Arrests Status"
        )
        st.plotly_chart(fig_age, use_container_width=True)


with right_chart_col:
    if not filtered_data.empty:
        fig_viol = px.histogram(
            filtered_data, 
            x="violation", 
            color="stop_outcome", 
            barmode="stack", 
            title="Violation Outcomes Breakdown"
        )
        st.plotly_chart(fig_viol, use_container_width=True)



st.markdown("---")
st.subheader("📝 Add New Police Log & Predict Outcome and Violation")

# Create a clean form block on the main page canvas
with st.form(key="main_page_log_entry_form", clear_on_submit=False):
    # This splits the empty layout space into two side-by-side columns
    form_col1, form_col2 = st.columns(2)


    with form_col1:
        input_date = st.text_input("Stop Date (YYYY-MM-DD)", value="2026-09-05")
        input_time = st.text_input("Stop Time (HH:MM)", value="14:30")
        input_gender = st.selectbox("Driver Gender", ["M", "F"])
        input_age = st.number_input("Driver Age", min_value=16, value=27)
        input_race = st.selectbox("Driver Race", ["White", "Black", "Hispanic", "Asian", "Other"])



    with form_col2:
        input_violation = st.selectbox("Violation", ["Speeding", "Dui", "Equipment", "Seatbelt", "Signal", "Other"])
        input_search = st.selectbox("Search Conducted?", ["True", "False"])
        input_search_type = st.text_input("Search Type", value="No Search")
        input_drugs = st.selectbox("Drugs Related Stop?", ["True", "False"])
    
    # The actual submission trigger button for the form
    submit_log_btn = st.form_submit_button("Predict & Log Entry")


if submit_log_btn:
    # Basic default values
    outcome_val = "Citation"
    arrest_val = "False"
    
    # If the stop involves drugs or DUI, predict an Arrest outcome automatically
        # If the stop involves drugs or DUI, predict an Arrest outcome automatically
    if input_violation == "Dui" or input_drugs == "True":
        outcome_val = "Arrest"
        arrest_val = "True"
        
    db_conn = sqlite3.connect("securecheck.db")
    cursor = db_conn.cursor()
    
    insert_sql = """
        INSERT INTO traffic_stops (
            stop_date, stop_time, driver_gender, driver_age, driver_race, 
            violation, search_conducted, search_type, stop_outcome, is_arrested, drugs_related_stop
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Convert string text selections back into clean database booleans
    s_cond = True if input_search == "True" else False
    d_stop = True if input_drugs == "True" else False
    is_arr = True if arrest_val == "True" else False
    
    cursor.execute(insert_sql, (
        input_date, input_time, input_gender, int(input_age), input_race,
        input_violation, s_cond, input_search_type, outcome_val, is_arr, d_stop
    ))
    
    db_conn.commit()
    db_conn.close()
    st.success(f"💾 Log entry saved into SQL! (Predicted Outcome: {outcome_val})")



st.markdown("---")
st.subheader("⚙️ Advanced Insights")

# Dropdown match list from your structural requirement image
insight_selection = st.selectbox(
    "Select a Query to Run",
    [
        "Top 5 Most Frequent Search Types",
        "Driver Violation Trends Based on Age and Race",
        "Top 5 Violations with Highest Arrest Rates"
    ]
)



if st.button("Run Query"):
    db_vault = sqlite3.connect("securecheck.db")
    
    if insight_selection == "Top 5 Most Frequent Search Types":
        executed_sql = """
            SELECT search_type, COUNT(*) as count 
            FROM traffic_stops 
            WHERE search_conducted = 1 AND search_type != 'No Search' AND search_type IS NOT NULL
            GROUP BY search_type 
            ORDER BY count DESC 
            LIMIT 5
        """
    elif insight_selection == "Driver Violation Trends Based on Age and Race":
        executed_sql = """
            SELECT violation, driver_race, AVG(driver_age) as average_age, COUNT(*) as total_stops
            FROM traffic_stops 
            GROUP BY violation, driver_race
            ORDER BY total_stops DESC
            LIMIT 10
        """
    else:
        executed_sql = """
            SELECT violation, COUNT(*) as total_stops, SUM(is_arrested) as total_arrests
            FROM traffic_stops 
            GROUP BY violation
            ORDER BY total_arrests DESC
            LIMIT 5
        """
        
    insight_df = pd.read_sql(executed_sql, con=db_vault)
    db_vault.close()
    
    # Render the dynamic data chart table output
    st.dataframe(insight_df, use_container_width=True)
 

