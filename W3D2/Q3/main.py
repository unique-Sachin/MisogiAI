import os
import openai
from tools.math_tools import calculate_expression
from tools.string_tools import count_vowels, count_letters
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# tools = [{
#     "type": "function",
#     "name": "get_weather",
#     "description": "Get current temperature for a given location.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "location": {
#                 "type": "string",
#                 "description": "City and country e.g. Bogotá, Colombia"
#             }
#         },
#         "required": [
#             "location"
#         ],
#         "additionalProperties": False
#     }
# }]


def get_reasoning_from_llm(query):
    prompt = f"""
You are a reasoning assistant. Given a natural language query, you must think step by step and decide whether a calculation or string operation is needed.

Query: "{query}"
Step-by-step reasoning:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip() if response.choices[0].message.content else ""


def decide_and_use_tool(reasoning, query):
    used_tool = None
    final_answer = None

    if "calculator" in reasoning.lower():
        # Simple expression parsing (demo purpose)
        expression = query.replace("What's", "").replace("?", "")
        try:
            result = calculate_expression(expression)
            used_tool = "calculator"
            final_answer = result
        except Exception as e:
            final_answer = f"Error in calculation: {e}"

    elif "vowel" in reasoning.lower():
        # Extract word from query
        word = query.split("'")[1].split("'")[0]
        result = count_vowels(word)
        used_tool = "vowel_counter"
        final_answer = result

    elif "letters" in reasoning.lower():
        word = query.split("'")[1].split("'")[0]
        result = count_letters(word)
        used_tool = "letter_counter"
        final_answer = result

    elif "letters" and "vowel" in reasoning.lower():
        words = query.split("'")
        word1 = words[1].split("'")[0]
        print(word1)
        word2 = words[3].split("'")[0]
        result = count_letters(word1) > count_vowels(word2)
        used_tool = "letter_counter + vowel_counter"
        final_answer = f"Yes" if result else "No"

    else:
        final_answer = "Answer not computable by tools."

    return used_tool, final_answer


def run_query(query):
    print(f"🧠 Query: {query}")
    reasoning = get_reasoning_from_llm(query)
    print(f"\n🪜 Reasoning:\n{reasoning}")
    tool, answer = decide_and_use_tool(reasoning, query)
    print(f"\n🔧 Tool used: {tool if tool else 'None'}")
    print(f"\n✅ Final Answer: {answer}")


if __name__ == "__main__":
    test_queries = [
        "What's the square root of the average of 18 and 50?",
        "How many vowels are in the word 'Multimodality'?",
        "Is the number of letters in 'machine' greater than the number of vowels in 'reasoning'?",
        "What is 23 plus 19 minus 4 times 2?",
        "Count the letters in 'Generalization'."
    ]

    for query in test_queries:
        print("=" * 60)
        run_query(query)
        print("=" * 60 + "\n")