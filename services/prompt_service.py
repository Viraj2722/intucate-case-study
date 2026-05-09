from typing import Optional
import db


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
