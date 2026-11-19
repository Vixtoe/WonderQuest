from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import agent_graph
from db import save_attempt, get_attempts

app = FastAPI(title="Agentic Enterprise Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlayStepRequest(BaseModel):
    task_goal: str
    user_attempt: str
    hint_level: int = 0
    user_id: str = "default_user"

class PlayStepResponse(BaseModel):
    is_solved: bool
    hint_level: int
    responses: list[str]
    protocol_logs: list[str]

class ProgressSaveRequest(BaseModel):
    user_id: str
    task_goal: str
    user_attempt: str
    hint_level: int
    is_solved: bool

class ProgressResponseModel(BaseModel):
    id: str
    user_id: str
    task_goal: str
    user_attempt: str
    hint_level: int
    is_solved: bool
    created_at: str

@app.post("/api/v1/agent/step", response_model=PlayStepResponse)
@app.post("/api/play-step", response_model=PlayStepResponse)
async def process_agent_step(payload: PlayStepRequest):
    initial_state = {
        "task_goal": payload.task_goal,
        "user_attempt": payload.user_attempt,
        "hint_level": payload.hint_level,
        "is_solved": False,
        "responses": [],
        "tool_log": [],
    }

    try:
        final_state = await agent_graph.ainvoke(initial_state)
    except Exception as e:
        print(f"Error executing agent graph: {e}")
        # 503 tells the client the upstream AI service failed, not that the request succeeded
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Engine execution failed: {str(e)}",
        )

    is_solved = final_state.get("is_solved", False)
    hint_level = final_state.get("hint_level", 0)

    try:
        save_attempt(
            user_id=payload.user_id,
            task_goal=payload.task_goal,
            user_attempt=payload.user_attempt,
            hint_level=hint_level,
            is_solved=is_solved,
        )
    except Exception as db_err:
        # Saving progress shouldn't stop the learner from getting feedback
        print(f"Warning: Failed to save progress attempt to database: {db_err}")

    return PlayStepResponse(
        is_solved=is_solved,
        hint_level=hint_level,
        responses=final_state.get("responses", []),
        protocol_logs=final_state.get("tool_log", []),
    )

@app.post("/api/progress", response_model=ProgressResponseModel, status_code=status.HTTP_201_CREATED)
async def create_progress(payload: ProgressSaveRequest):
    try:
        result = save_attempt(
            user_id=payload.user_id,
            task_goal=payload.task_goal,
            user_attempt=payload.user_attempt,
            hint_level=payload.hint_level,
            is_solved=payload.is_solved,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database save failed: {str(e)}",
        )

@app.get("/api/progress/{user_id}", response_model=list[ProgressResponseModel])
async def read_user_progress(user_id: str):
    try:
        attempts = get_attempts(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(e)}",
        )

    if not attempts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attempts found for user {user_id}",
        )
    return attempts