import streamlit as st
import json
from optimizers.gemini_optimizer import optimize_prompt_with_gemini

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Prompt Optimizer",
    page_icon="✨",
    layout="wide"
)

# --- Data Loading ---
@st.cache_data
def load_tool_data():
    """Loads tool analysis data from the JSON file."""
    with open('tool_analysis.json', 'r') as f:
        return json.load(f)

try:
    tool_data = load_tool_data()
    tool_options = {key: data['name'] for key, data in tool_data.items()}
except FileNotFoundError:
    st.error("`tool_analysis.json` not found. Please make sure the file exists.")
    st.stop()

# --- API Key ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.sidebar.error("Google API key not found! Please add it to your `.streamlit/secrets.toml` file.")
    GOOGLE_API_KEY = ""


# --- UI Components ---
st.title("🤖 AI Prompt Optimizer for Coding Tools")
st.write(
    "This tool uses Google's Gemini to refine a base prompt for a selected coding tool, "
    "enhancing its effectiveness based on the tool's unique capabilities."
)

st.sidebar.header("Configuration")
selected_tool_key = st.sidebar.selectbox(
    "Select an AI Coding Tool:",
    options=list(tool_options.keys()),
    format_func=lambda key: tool_options[key]
)

original_prompt = st.text_area("Enter your base prompt here:", height=200, placeholder="e.g., 'Write a Python function to sort a list of numbers.'")

if st.button("🚀 Optimize Prompt"):
    if original_prompt:
        if not GOOGLE_API_KEY:
            st.error("Cannot optimize without a Google API key.")
        else:
            with st.spinner("Optimizing your prompt with Gemini..."):
                # --- Core Logic ---
                selected_tool_name = tool_data[selected_tool_key]['name']
                tool_strategies = tool_data[selected_tool_key]['strategies']
                optimized_prompt, explanation = optimize_prompt_with_gemini(
                    original_prompt,
                    selected_tool_name,
                    tool_strategies,
                    GOOGLE_API_KEY
                )

                # --- Display Results ---
                st.subheader("Results")
                col1, col2 = st.columns(2)
                with col1:
                    st.text_area("Original Prompt", original_prompt, height=300, disabled=True)
                with col2:
                    st.text_area("✨ Optimized Prompt", optimized_prompt, height=300)

                st.subheader("Explanation of Changes")
                st.info(explanation)

    else:
        st.warning("Please enter a prompt to optimize.")


# --- Footer ---