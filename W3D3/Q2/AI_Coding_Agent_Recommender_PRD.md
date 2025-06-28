# Product Requirements Document (PRD)

## Project Title
**AI Coding Agent Recommender**

---

## Objective
Build a system that recommends the best coding agents (e.g., Copilot, Cursor, Replit, CodeWhisperer) for a given coding task described in natural language.

---

## Goals
- Provide intelligent recommendations based on task complexity, type, and programming language.
- Justify why each agent is recommended.
- Make the system user-friendly via a simple web interface.

---

## Target Users
- Developers (beginners to advanced)
- Project managers evaluating tools
- Tech educators and students

---

## Functional Requirements
1. **Task Input Interface**
   - Accepts natural language task descriptions.
   - Streamlit form for input.

2. **Agent Knowledge Base**
   - Stored in a JSON file (`agents_db.json`).
   - Includes each agent’s strengths, supported languages, integrations, and ideal use cases.

3. **Recommendation Engine**
   - Parses task descriptions.
   - Scores agents based on match quality.
   - Outputs top 3 agents with explanations.

4. **Results Display**
   - Shows agent name, score, and justification.
   - Streamlit interface with a clean, readable layout.

---

## Non-Functional Requirements
- Fast and responsive (sub-second latency for recommendations).
- Modular and maintainable code.
- Easily updatable knowledge base.

---

## Technical Stack
- **Frontend/UI**: Streamlit
- **Backend/Logic**: Python
- **Data Storage**: JSON (for agent knowledge base)
- **Libraries**:
  - `spacy` or `transformers` for NLP
  - `pandas` for data handling
  - `streamlit` for UI

---

## File Structure

project_root/
│
├── app.py                    # Main application
├── recommendation_engine.py  # Core logic for analyzing and scoring
├── agents_db.json            # Agent knowledge base
├── demo/                     # Screenshots or demo media
└── README.md                 # Setup, usage, and explanation

---

## Milestones
1. Design schema for agent knowledge base
2. Build task parser and scoring algorithm
3. Build initial Streamlit prototype
4. Connect all modules and test
5. Prepare documentation and demo

---

## Deliverables
- Fully functional Streamlit app (`app.py`)
- JSON-based agent database
- Scoring and recommendation engine
- README and demo folder