def call_openai(prompt: str) -> str:
    """Call Gemini synchronously and return the assistant text.

    We keep this wrapper name so the rest of the app stays unchanged while the
    underlying provider switches from OpenAI to Gemini.
    """
    """
    Mock AI service - simulates AI responses based on prompt keywords.
    The service layer is abstracted so switching to real OpenAI/Gemini
    requires changing only this file.
    """
    prompt_lower = prompt.lower()

    if "score" in prompt_lower or "pass" in prompt_lower or "marks" in prompt_lower:
        return (
            "To pass CA Final, you need a minimum of 40% in each individual "
            "subject and an aggregate of 50% across all subjects in a group. "
            "Scoring below 40% in any single subject means failing that entire "
            "group, regardless of your total aggregate score."
        )

    elif "subject" in prompt_lower or "group" in prompt_lower:
        return (
            "CA Final consists of 6 subjects across 2 groups. "
            "Group 1: Financial Reporting, Strategic Financial Management, "
            "Advanced Auditing & Professional Ethics. "
            "Group 2: Corporate & Economic Laws, Strategic Cost Management, "
            "Elective Paper, Direct & Indirect Tax Laws."
        )

    elif "attempt" in prompt_lower:
        return (
            "There is no restriction on the number of attempts for CA Final. "
            "Candidates may appear as many times as required until they successfully "
            "clear the examination."
        )

    elif "exemption" in prompt_lower:
        return (
            "A subject exemption is granted in CA Final if you score 60% or more "
            "in that paper. The exemption remains valid for the next 3 attempts "
            "of that group."
        )

    elif "syllabus" in prompt_lower or "topics" in prompt_lower:
        return (
            "The CA Final syllabus is prescribed by ICAI and includes advanced topics "
            "in accounting, law, taxation, and management. It is updated periodically. "
            "Refer to icai.org for the latest syllabus."
        )

    else:
        return (
            "As a CA Final education expert: Focus on ICAI official study material, "
            "practice with mock test papers, and maintain consistent revision. "
            "Time management and conceptual clarity are the keys to clearing "
            "this prestigious examination. Visit icai.org for official resources."
        )
