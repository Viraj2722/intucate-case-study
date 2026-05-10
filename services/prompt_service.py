from typing import Optional
import db


def select_best_prompt(user_input: str) -> str:
    """Intelligently select the best prompt based on user input keywords.
    
    Scans user input for keywords and returns the matching prompt ID.
    Falls back to Education_Prompt if no specific match.
    
    Args:
        user_input: the raw user question to analyze
    
    Returns:
        The best matching prompt ID (e.g., 'CA_Scoring_Prompt')
    """
    user_lower = user_input.lower()
    
    # Keyword-to-prompt mapping
    prompt_mappings = [
        ("CA_Scoring_Prompt", ["score", "pass", "marks", "criteria", "aggregate", "percentage", "fail", "minimum"]),
        ("CA_Syllabus_Prompt", ["subject", "group", "syllabus", "topics", "chapter", "paper", "group 1", "group 2"]),
        ("CA_Exam_Strategy_Prompt", ["attempt", "strategy", "prepare", "tips", "study", "revision", "time", "exam"]),
        ("CA_Exemption_Prompt", ["exemption", "exempt", "validity", "re-exam", "re-attempt"]),
    ]
    
    # Check each mapping and return first match
    for prompt_id, keywords in prompt_mappings:
        for keyword in keywords:
            if keyword in user_lower:
                return prompt_id
    
    # Default fallback
    return "Education_Prompt"


def get_prompt(prompt_id: str, user_input: str) -> str:
    """Fetch a prompt template by `_id` from MongoDB and substitute the user input.

    Why: Storing templates in the DB makes them editable without code deploys.

    Args:
        prompt_id: the document _id to fetch from `prompts` collection
        user_input: the raw user-provided string to insert into the template

    Returns:
        The final prompt string ready to send to the AI.

    Raises:
        ValueError: if the prompt document is not found.
    """
    doc: Optional[dict] = db.prompts_col.find_one({"_id": prompt_id})
    if not doc:
        # Raise a clear error so upstream handlers can return appropriate HTTP errors.
        raise ValueError(f"Prompt with id '{prompt_id}' not found in database")

    template = doc.get("template", "")
    # Simple, explicit substitution; we intentionally do not use templating engines
    # to keep behavior straightforward and avoid template injection risks.
    final = template.replace("{{userInput}}", user_input)
    return final


def get_best_prompt(user_input: str) -> str:
    """Convenience function: auto-select best prompt and render it.
    
    Args:
        user_input: the raw user question
    
    Returns:
        The final rendered prompt ready for AI
    """
    best_prompt_id = select_best_prompt(user_input)
    return get_prompt(best_prompt_id, user_input)

