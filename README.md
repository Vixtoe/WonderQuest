# WonderQuest

WonderQuest is an AI-powered learning backend for children aged 8 to 10, prototyped in Figma as part of CN330 (Computer Application Development) at Thammasat University. The backend is built with Python, FastAPI, LangGraph, and Google Gemini (`gemini-3.8-flash`) via `langchain-google-genai`, using Supabase for storage. Currently, the core LangGraph evaluation and hint flow is implemented in `engine.py`, exposed via `POST /api/play-step` in `main.py`, and unit-tested with a fake model in `test_engine.py`, while several prototype minigames remain unimplemented.

**Status:** The AI evaluator and hint generator require a Gemini API quota; `POST /api/play-step` returns `503` when the engine fails, including when the Gemini quota is exhausted.

## From Figma Design to Code

| Figma prototype feature | Status | Implementation |
| --- | --- | --- |
| Answer evaluation and guided hint step | Implemented | LangGraph evaluator node with structured output, hint node using `gemini-3.8-flash`, and `POST /api/play-step` in `main.py` |
| Persistence / data layer | Implemented | `db.py` with Supabase storage |
| Math game | Designed, not yet implemented | Planned in Figma design; not yet implemented in backend |
| Animal sound game | Designed, not yet implemented | Planned in Figma design; not yet implemented in backend |
| Spelling game | Designed, not yet implemented | Planned in Figma design; not yet implemented in backend |

## How to Run

Activate your virtual environment (example on macOS/Linux; use `venv\Scripts\activate` on Windows):

```bash
source venv/bin/activate
