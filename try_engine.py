import asyncio
from engine import agent_graph

async def main():
    result = await agent_graph.ainvoke({
        "task_goal": "Continue the sequence: 2, 4, 6, ?",
        "user_attempt": "5",
        "hint_level": 0,
        "is_solved": False,
        "responses": [],
        "tool_log": [],
    })
    for r in result["responses"]:
        print("-", r)
    print("Tool log:", result["tool_log"])

asyncio.run(main())