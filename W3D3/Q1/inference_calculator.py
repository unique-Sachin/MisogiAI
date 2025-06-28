import streamlit as st
import json
import os

# Construct an absolute path to the JSON file relative to the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'model_data.json')

# Load data from JSON file
with open(json_path, 'r') as f:
    data = json.load(f)

MODEL_INFO = data['MODEL_INFO']
HARDWARE_COST = data['HARDWARE_COST']
LATENCY_MULTIPLIER = data['LATENCY_MULTIPLIER']
COST_MULTIPLIER = data['COST_MULTIPLIER']
MEMORY_FACTOR = data['MEMORY_FACTOR']
HARDWARE_MEMORY = data['HARDWARE_MEMORY']

# --- UI Setup ---
st.set_page_config(page_title="LLM Inference Calculator", layout="wide")
st.title("LLM Inference Calculator")
st.write("An interactive tool to estimate latency, memory, and cost for LLM inference.")

# --- Sidebar Inputs ---
st.sidebar.header("Input Parameters")
model_size = st.sidebar.selectbox("Model Size", ["7B", "13B", "GPT-4"])
hardware_type = st.sidebar.selectbox("Hardware Type", ["A100", "T4", "CPU", "TPU"])
deployment_mode = st.sidebar.selectbox("Deployment Mode", ["cloud", "on-premise", "serverless"])
tokens = st.sidebar.number_input("Tokens", min_value=1, value=500)
batch_size = st.sidebar.number_input("Batch Size", min_value=1, value=4)

st.sidebar.header("Use Case Presets")
if st.sidebar.button("Chatbot"):
    tokens = 50
    batch_size = 1
if st.sidebar.button("Summarizer"):
    tokens = 1000
    batch_size = 2
if st.sidebar.button("Batch QA System"):
    tokens = 500
    batch_size = 10


# --- Calculations ---
def calculate_metrics(model, hardware, deployment, t, b):
    # Latency Calculation
    tokens_per_sec = MODEL_INFO[model]['tokens_per_sec'].get(hardware, 0)
    if tokens_per_sec == 0:
        return "N/A", "N/A", "N/A", "No", "N/A"

    total_latency = (t * b) / tokens_per_sec
    per_request_latency = total_latency / b if b > 0 else 0
    
    latency_modifier = LATENCY_MULTIPLIER.get(deployment, 1.0)
    final_latency = per_request_latency * latency_modifier

    # Memory Calculation
    base_memory = MODEL_INFO[model]['base_memory']
    mem_factor = MEMORY_FACTOR[model]
    memory_usage = base_memory + (t * b * mem_factor / 1024) # Convert to GB

    # Cost Calculation
    hourly_cost = HARDWARE_COST.get(hardware, 0)
    cost_modifier = COST_MULTIPLIER.get(deployment, 1.0)
    cost_per_request = ((total_latency * hourly_cost) / 3600) * cost_modifier / b if b > 0 else 0

    # Hardware Compatibility
    hardware_compatible = "Yes" if memory_usage <= HARDWARE_MEMORY.get(hardware, 0) else "No"

    return f"{final_latency:.4f}s", f"{memory_usage:.2f} GB", f"${cost_per_request:.6f}", hardware_compatible, f"{total_latency:.4f}s"

# --- Main Panel Outputs ---
st.header("Estimated Outputs")

if tokens > 0 and batch_size > 0:
    per_req_lat, mem_usage, cost, compatible, batch_lat = calculate_metrics(model_size, hardware_type, deployment_mode, tokens, batch_size)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Per-Request Latency", per_req_lat)
    with col2:
        st.metric("Memory Usage", mem_usage)
    with col3:
        st.metric("Cost per Request", cost)
    with col4:
        st.metric("Hardware Compatible", compatible)
        
    st.metric("Batch Latency", batch_lat)
else:
    st.warning("Please enter valid token and batch sizes.")

# --- Documentation ---
with st.expander("Assumptions and Formula Logic"):
    st.markdown("""
    - **Latency**: `(tokens * batch_size / tokens_per_sec) / batch_size * latency_multiplier`
    - **Memory Usage**: `base_memory + (tokens * batch_size * memory_factor / 1024)`
    - **Cost per Request**: `((total_batch_latency * hourly_cost) / 3600) * cost_modifier / batch_size`
    - **Hardware Compatibility**: Checks if estimated memory usage is within the hardware's capacity.
    """) 