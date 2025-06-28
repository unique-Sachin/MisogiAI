import streamlit as st
from recommendation_engine import load_agents, recommend_agents

# Load agent data
agents_db = load_agents()

# --- Streamlit UI ---
st.title("AI Coding Agent Recommender")

# Add a sidebar to show all supported agents
with st.sidebar:
    st.header("Supported AI Coding Agents")
    for agent in agents_db:
        with st.expander(agent["name"]):
            st.write(f"**Description:** {agent['description']}")
            st.write("**Strengths:**")
            for strength in agent["strengths"]:
                st.write(f"- {strength}")
            st.write("**Supported Languages:**")
            st.write(", ".join(agent["supported_languages"]))

st.write("""
Describe your coding task below, and we'll recommend the best AI coding agent for the job.
Consider mentioning the programming language, the type of task (e.g., debugging, refactoring, building a UI), and any specific requirements.
""")

# User input
task_description = st.text_area("Enter your coding task description:", height=150)

if st.button("Get Recommendations"):
    if task_description:
        with st.spinner("Analyzing your task..."):
            recommendations = recommend_agents(task_description, agents_db)
        
        st.subheader("Top 3 Recommendations")
        
        if recommendations:
            for i, rec in enumerate(recommendations):
                st.markdown(f"### {i+1}. {rec['name']}")
                st.markdown(f"**Score:** {rec['score']}")
                st.markdown("**Justification:**")
                # Using a list for justifications
                for justification in rec['justification']:
                    st.markdown(f"- {justification}")
                st.divider()
        else:
            st.warning("No suitable agents found for your task. Please try a different description.")
    else:
        st.error("Please enter a task description.")
