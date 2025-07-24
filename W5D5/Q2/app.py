import streamlit as st
from agent import get_sql_agent

st.set_page_config(page_title="SQL Query Agent", layout="centered")
st.title("🧑‍💻 SQL Query Agent (Zepto & Blinkit)")

st.write("""
Enter a natural language question about the Zepto or Blinkit databases.\n
Example: 
- List all products in the Dairy category from Zepto.
- Show me products above ₹500 in Blinkit.
""")

query = st.text_area("Enter your question:", height=80)

if 'agent' not in st.session_state:
    st.session_state['agent'] = get_sql_agent()

if st.button("Ask") and query.strip():
    with st.spinner("Thinking..."):
        try:
            result = st.session_state['agent'].invoke({"input": query})
            st.success("Result:")
            st.write(result)
        except Exception as e:
            st.error(f"Error: {e}") 