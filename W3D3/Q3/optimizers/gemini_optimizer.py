import google.generativeai as genai
import json

def optimize_prompt_with_gemini(prompt: str, tool_name: str, strategies: list, api_key: str):
    """
    Uses the Google Gemini API to optimize a prompt based on tool-specific strategies.
    """
    if not api_key:
        return (
            "Error: Google API key not found.",
            "Please add your Google API key to the `.streamlit/secrets.toml` file."
        )

    try:
        genai.configure(api_key=api_key)

        strategy_list = "\n- ".join(strategies)
        
        system_prompt = f"""
You are an expert prompt engineer. Your task is to refine a user's base prompt to make it more effective for a specific AI coding tool.

Analyze the user's prompt and rewrite it to incorporate the following tool-specific strategies. The optimized prompt should be clear, actionable, and tailored to the tool's strengths.

Tool: {tool_name}
Strategies:
- {strategy_list}

Your response must be a single, valid JSON object with two keys: "optimized_prompt" and "explanation".
The "explanation" should briefly describe the key changes you made. Do not include any other text or markdown formatting.
"""
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_prompt
        )

        response = model.generate_content(prompt)

        # The response should be a JSON string directly.
        json_string = response.text.strip()
        if json_string.startswith("```json"):
            json_string = json_string[7:-3].strip()

        result = json.loads(json_string)
        
        return result.get("optimized_prompt", ""), result.get("explanation", "")

    except Exception as e:
        error_message = f"An error occurred with the Gemini API: {e}"
        explanation = "Could not generate an optimization. Please check your API key and the connection."
        return error_message, explanation 