# LLM Inference Calculator

An interactive Streamlit web app that allows users to estimate the latency, memory usage, cost per request, and hardware compatibility of various LLM models (7B, 13B, GPT-4) based on a set of input parameters. This tool is designed for educational, research, and engineering estimation purposes.

---

## 🚀 Features

*   **Model Comparison**: Choose between 7B, 13B, or GPT-4 models.
*   **Customizable Inputs**: Adjust model size, tokens, batch size, hardware type, and deployment mode.
*   **Key Output Metrics**: Get instant estimates for per-request latency, batch latency, memory usage, and cost per request.
*   **Hardware Compatibility Check**: Instantly see if your chosen model and configuration will fit on the selected hardware.
*   **Use Case Presets**: Quickly load configurations for common scenarios like `Chatbot`, `Summarizer`, and `Batch QA System`.
*   **Formula Transparency**: The underlying formulas used for calculations are displayed in the app.

---

## 🛠️ How to Run

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone 
    cd Q1
    ```

2.  **Install the required dependencies:**
    Make sure you have Python 3.7+ installed. Then, run the following command to install the necessary packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    Once the dependencies are installed, you can start the application with this command:
    ```bash
    streamlit run inference_calculator.py
    ```
    The application will open in your default web browser.

---

## 📂 Project Structure

*   `inference_calculator.py`: The main Python script containing the Streamlit application logic and UI.
*   `model_data.json`: A static JSON file that stores all the reference data for models, hardware, costs, and performance multipliers.
*   `requirements.txt`: A list of the Python packages required to run the application.
*   `LLM_Inference_Calculator_PRD.txt`: The original Product Requirements Document (PRD) that defined the project scope and goals.
*   `research_notes.md`: A markdown file containing background information on LLM inference fundamentals and a detailed comparison of the supported models.
*   `scenario_analysis.md`: A markdown file that analyzes three different use cases (Chatbot, Summarizer, Batch QA) and provides recommendations for the optimal setup for each.
*   `readme.md`: This file, providing an overview and instructions for the project.

---

## UI Overview

The application is divided into two main sections:

1.  **Sidebar**: On the left, you'll find all the input controls. You can select the model, hardware, and deployment mode from dropdown menus, and set the token count and batch size using number inputs. The use case preset buttons are also located here.
2.  **Main Panel**: The main area of the application displays the calculated output metrics in clear, easy-to-read cards. It shows the per-request latency, total batch latency, estimated memory usage, cost per request, and whether the configuration is compatible with the selected hardware. 