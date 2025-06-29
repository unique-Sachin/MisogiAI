# AI Prompt Optimizer for Coding Tools

This project is an AI-powered tool designed to optimize prompts for various AI coding assistants. It uses Google's Gemini to refine prompts to align with the specific strengths and interaction models of each tool, improving the quality and relevance of the generated code.

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up your API Key:**
    Create a file at `.streamlit/secrets.toml` and add your Google API key to it:
    ```toml
    GOOGLE_API_KEY = "your-api-key-here"
    ```

3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

4.  Open your browser and navigate to the URL provided by Streamlit.

## Project Structure

-   `app.py`: The main application file containing the Streamlit web interface.
-   `optimizers/`: A directory containing the Gemini API integration.
-   `tool_analysis.json`: A metadata file that describes the capabilities and optimization strategies for each tool.
-   `requirements.txt`: A file listing the Python dependencies for the project.
-   `readme.md`: This documentation file. 