from datetime import datetime


def build_history_doc(user_input, final_prompt, ai_response, prompt_id) -> dict:
    """Build a history document to persist in MongoDB.

    Why: Keeping user inputs, the transformed prompt, and the AI response
    allows auditing and later analysis (improving prompts, debugging).
    """
    return {
        "prompt_id": prompt_id,
        "user_input": user_input,
        "final_prompt": final_prompt,
        "ai_response": ai_response,
        "created_at": datetime.utcnow(),
    }
