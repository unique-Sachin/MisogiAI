"""Streamlit interface for the local RAG pipeline."""
import sys
from pathlib import Path

# Add parent directory to Python path so we can import from app/
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from app.intent_classifier import classify_intent
from app.retriever import retrieve, retrieve_with_references
from app.llm_router import LLMRouter

router = LLMRouter()

st.set_page_config(page_title="Customer Support RAG", page_icon="🤖")

st.title("📚 Local RAG Customer Support Assistant")

if "mode" not in st.session_state:
    st.session_state["mode"] = "ollama"

with st.sidebar:
    st.header("Settings")
    llm_mode = st.selectbox("LLM backend", ["ollama", "openai"], index=0)
    k = st.number_input("Top-k context chunks", min_value=1, max_value=10, value=4, step=1)
    show_references = st.checkbox("Show source references", value=False)

prompt = st.chat_input("Ask your question…")

if prompt:
    # Classify intent
    intent = classify_intent(prompt)
    st.chat_message("assistant").write(f"**Detected intent:** `{intent}`")

    # Retrieve context with or without references
    if show_references:
        context_with_refs = retrieve_with_references(prompt, intent, k=int(k))
        context = [item["content"] for item in context_with_refs]
        
        with st.expander("Retrieved context with references"):
            for i, item in enumerate(context_with_refs, 1):
                st.markdown(f"**Chunk {i}:** (Source: `{item['metadata'].get('source_file', 'unknown')}`, Chunk #{item['metadata'].get('chunk_index', 0)})")
                st.markdown(f"> {item['content']}")
                st.markdown(f"*Similarity: {1 - item['distance']:.3f}*")
                st.markdown("---")
    else:
        # Fallback to legacy method
        context = retrieve(prompt, intent, k=int(k))
        
        with st.expander("Retrieved context"):
            for i, c in enumerate(context, 1):
                st.markdown(f"**Chunk {i}:**\n> {c}")

    # Build final prompt
    full_prompt = "\n".join(context) + "\n\nUser: " + prompt

    # Use the selected LLM backend
    force_openai = (llm_mode == "openai")
    
    with st.chat_message("assistant"):
        holder = st.empty()
        collected = ""
        try:
            for token in router.generate(full_prompt, stream=True, force_openai=force_openai):
                collected += token
                holder.markdown(collected + "▌")
            holder.markdown(collected)
        except Exception as e:
            st.error(f"Error generating response: {e}")
            if "OPENAI_API_KEY" in str(e):
                st.info("💡 Set your OPENAI_API_KEY environment variable to use OpenAI backend.") 