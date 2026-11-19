import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
    return create_client(url, key)

def save_attempt(
    user_id: str,
    task_goal: str,
    user_attempt: str,
    hint_level: int,
    is_solved: bool
) -> dict:
    """Inserts a puzzle attempt record into Supabase."""
    client = get_client()
    data = {
        "user_id": user_id,
        "task_goal": task_goal,
        "user_attempt": user_attempt,
        "hint_level": hint_level,
        "is_solved": is_solved,
    }
    response = client.table("progress_attempts").insert(data).execute()
    return response.data[0] if response.data else {}

def get_attempts(user_id: str) -> list[dict]:
    """Retrieves all attempts for a given user, ordered newest first."""
    client = get_client()
    response = (
        client.table("progress_attempts")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []