import json

def load_agents(db_path="agents_db.json"):
    """Loads the agent knowledge base from a JSON file."""
    with open(db_path, 'r') as f:
        return json.load(f)

def recommend_agents(task_description, agents):
    """
    Recommends AI coding agents based on a task description.

    Args:
        task_description (str): The user's description of the coding task.
        agents (list): A list of agent dictionaries from the knowledge base.

    Returns:
        list: A sorted list of recommended agents with scores and justifications.
    """
    # Simple keyword matching for now.
    # We can enhance this with NLP later.
    
    scores = []
    task_keywords = set(task_description.lower().split())

    for agent in agents:
        score = 0
        justification = []
        
        # Check against strengths
        for strength in agent.get("strengths", []):
            if any(word in strength.lower() for word in task_keywords):
                score += 2
                justification.append(f"Strength in '{strength}'")

        # Check against ideal use cases
        for use_case in agent.get("ideal_use_cases", []):
            if any(word in use_case.lower() for word in task_keywords):
                score += 2
                justification.append(f"Ideal for '{use_case}'")

        # Check against supported languages
        for lang in agent.get("supported_languages", []):
            if lang.lower() in task_keywords:
                score += 1
                justification.append(f"Supports '{lang}'")

        if score > 0:
            scores.append({
                "name": agent["name"],
                "score": score,
                "justification": list(set(justification)) # Remove duplicates
            })

    # Sort agents by score in descending order
    recommended_agents = sorted(scores, key=lambda x: x["score"], reverse=True)
    
    return recommended_agents[:3] # Return top 3

if __name__ == '__main__':
    # Example usage:
    agents_db = load_agents()
    task = "I need to build a web app in Python. I want to do some refactoring and I need good code completion."
    recommendations = recommend_agents(task, agents_db)
    
    print("Top recommendations:")
    for rec in recommendations:
        print(f"- {rec['name']} (Score: {rec['score']})")
        print(f"  Justification: {', '.join(rec['justification'])}")
