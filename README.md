# WonderQuest

> An AI-assisted learning backend for children aged 8 to 10. It evaluates a learner's answer to a pattern puzzle, decides whether to give a hint, and generates hints with an LLM. The interface was designed in Figma as part of a university course.

![Figma](https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0052CC?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)

---

## Project Overview

WonderQuest began as a course project for CN330 Computer Application Development at Thammasat School of Engineering. The Figma prototype explores AI-narrated storytelling with math, animal sound, and spelling challenges. This repository contains the backend that handles answer evaluation and adaptive hints for one puzzle type, sequence completion.

---

## Status

- **Built and tested offline:** routing logic, hint escalation limits, text extraction, and database endpoints. Twelve pytest tests pass without calling any external API.
- **Built, pending live verification:** the Gemini-based answer evaluator and hint generator. They require a Gemini API quota. The API currently returns `503 Service Unavailable` when the quota is exhausted, which is the intended error behavior.
- **Not yet built:** the math, animal sound, and spelling games, the story narrator, and the front-end interface. These appear only in the Figma prototype.
- **Not yet measured:** evaluator accuracy. An evaluation set (`puzzles.json` and `eval_puzzles.py`) exists, but it has not been run against the live model.

---

## From Figma Design to Code

| Figma prototype feature | Status | Implementation |
|---|---|---|
| Math challenges | Designed, not yet implemented | None |
| Animal sound and visual games | Designed, not yet implemented | None |
| Spelling challenges | Designed, not yet implemented | None |
| Story narration and level progression | Designed, not yet implemented | None |
| Answer checking | Built, live check pending quota | Gemini structured-output evaluator returns `is_solved` and feedback |
| Adaptive hints (up to 3 per puzzle) | Built, live check pending quota | LangGraph hint node generates escalating hints with Gemini |
| Progress saving | Built, tested with mocked storage | `POST /api/progress` and `GET /api/progress/{user_id}` backed by Supabase |

---

## Architecture

The puzzle flow is a LangGraph state graph:

1. **Evaluator node:** sends the task, the learner's attempt, and the current hint level to Gemini. It returns a structured result with `is_solved`, feedback, and a suggested hint level.
2. **Routing:** if the answer is solved, the graph ends. If the hint level has reached 3, the graph ends. Otherwise, it moves to the hint node.
3. **Hint escalator node:** asks Gemini for one hint at the next level, without revealing the answer.
4. **End.**

The API endpoint `POST /api/play-step` runs the graph. If the graph fails, for example because of a quota error, the endpoint returns `503` with the error message instead of a success status.

---

## How to Run

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install fastapi uvicorn pydantic langgraph langchain-google-genai langchain-core python-dotenv supabase pytest

# 3. Add your keys to a .env file (never commit this file)
#    GOOGLE_API_KEY=your_key
#    SUPABASE_URL=your_url
#    SUPABASE_KEY=your_key

# 4. Start the API server
uvicorn main:app --reload
# Open http://127.0.0.1:8000/docs to test endpoints

# 5. Run the offline tests (no API calls)
pytest -v

# 6. Optional: live check against Gemini (uses API quota)
python try_engine.py
```

---

## Repository Structure

```text
wonderquest/
├── main.py              # FastAPI endpoints
├── engine.py            # LangGraph workflow: evaluator, routing, hint node
├── db.py                # Attempt storage (Supabase)
├── test_main.py         # API tests with mocked storage
├── test_engine.py       # Routing and hint tests with a fake model
├── try_engine.py        # Live smoke test (uses API quota)
├── eval_puzzles.py      # Evaluation script (not yet run against the live model)
├── puzzles.json         # Evaluation puzzles
├── docs/
│   ├── crazy8s-sketch-sheet.pdf
│   └── WonderQuest.png
└── README.md
```

---

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic
- **AI workflow:** LangGraph, LangChain, Google Gemini
- **Storage:** Supabase (PostgreSQL)
- **Testing:** pytest
- **Design:** Figma (interactive prototype)

---

## Figma Prototype

- [View the interactive prototype](https://www.figma.com/make/8CEWes2QYDGyEuBppXYGn8/AI-Story-Adventure-Prototype?t=c3paAW3aAkuIwCoc-1)

To explore it, open the link, click the Play (Present) icon in the top-right toolbar, and click the buttons, story cards, and hint icons to test the flow.
