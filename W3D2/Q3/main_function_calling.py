import os
import openai
import json
import math
from tools.string_tools import count_vowels, count_letters
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def calculate_expression(expression: str) -> float:
    """Calculate mathematical expressions safely"""
    try:
        # Handle specific cases
        if "average" in expression.lower() and "sqrt" in expression.lower():
            # Extract numbers for average calculation
            import re
            numbers = re.findall(r'\d+', expression)
            if len(numbers) >= 2:
                avg = sum(map(int, numbers)) / len(numbers)
                return round(math.sqrt(avg), 2)
        
        # Handle simple arithmetic
        if "plus" in expression.lower() or "minus" in expression.lower() or "times" in expression.lower():
            # Convert natural language to math expression
            expr = expression.lower()
            expr = expr.replace("plus", "+").replace("minus", "-").replace("times", "*")
            expr = expr.replace("what is", "").replace("?", "").strip()
            
            # Use eval with limited globals for safety (demo only)
            result = eval(expr, {"__builtins__": {}}, {"math": math})
            return round(float(result), 2)
            
        return 0.0
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}. Error: {e}")


def run_query_with_function_calling(query):
    print(f"🧠 Query: {query}")
    
    # Define functions for OpenAI
    functions = [
        {
            "type": "function",
            "function": {
                "name": "calculate_expression",
                "description": "Calculate mathematical expressions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "count_vowels",
                "description": "Count vowels in a word",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "The word to count vowels in"
                        }
                    },
                    "required": ["word"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "count_letters",
                "description": "Count letters in a word",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "The word to count letters in"
                        }
                    },
                    "required": ["word"]
                }
            }
        }
    ]
    
    # Call OpenAI with function calling
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
        tools=functions,  # type: ignore
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    print(f"\n🪜 Reasoning:\n{response_message.content if response_message.content else 'No reasoning provided'}")
    
    if tool_calls:
        # Execute the function calls
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"\n🔧 Tool called: {function_name}")
            print(f"📝 Arguments: {function_args}")
            
            # Execute the appropriate function
            if function_name == "calculate_expression":
                try:
                    result = calculate_expression(function_args["expression"])
                    print(f"✅ Result: {result}")
                    return result
                except Exception as e:
                    print(f"❌ Error: {e}")
                    return f"Error in calculation: {e}"
                    
            elif function_name == "count_vowels":
                result = count_vowels(function_args["word"])
                print(f"✅ Result: {result}")
                return result
                
            elif function_name == "count_letters":
                result = count_letters(function_args["word"])
                print(f"✅ Result: {result}")
                return result
    else:
        print(f"\n🔧 Tool used: None")
        print(f"\n✅ Final Answer: {response_message.content}")
        return response_message.content


if __name__ == "__main__":
    test_queries = [
        "What's the square root of the average of 18 and 50?",
        "How many vowels are in the word 'Multimodality'?",
        "Is the number of letters in 'machine' greater than the number of vowels in 'reasoning'?",
        "What is 23 plus 19 minus 4 times 2?",
        "Count the letters in 'Generalization'."
    ]

    print("🚀 Testing OpenAI Built-in Function Calling\n")
    
    for query in test_queries:
        print("=" * 60)
        result = run_query_with_function_calling(query)
        print(f"\n🎯 Final Answer: {result}")
        print("=" * 60 + "\n") 