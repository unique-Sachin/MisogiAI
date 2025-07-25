import streamlit as st
from agent.agent_executor import run_agent
from google_api.gsheet_connector import get_worksheet_names

st.set_page_config(page_title="Google Sheet AI Agent", layout="wide")
st.title("📊 Google Sheet AI Assistant")

spreadsheet_id = st.text_input("🔗 Enter Google Sheet ID")

sheet_name = None
if spreadsheet_id:
    try:
        worksheet_names = get_worksheet_names(spreadsheet_id)
        sheet_name = st.selectbox("🗂️ Select Worksheet", worksheet_names)
    except Exception as e:
        st.error(f"❌ Could not fetch worksheet names: {e}")

query = st.text_area("💬 Ask your question:")
run = st.button("▶️ Run")

if run and spreadsheet_id and sheet_name and query:
    with st.spinner("Running query..."):
        try:
            result_df = run_agent(query, spreadsheet_id, sheet_name)
            st.success("✅ Query completed!")
            st.dataframe(result_df)
        except Exception as e:
            st.error(f"❌ Error: {e}")
