from flask import Blueprint, request, jsonify
from services import prompt_service, openai_service
import models.history as history_model
import db

single_bp = Blueprint("single_bp", __name__)


@single_bp.route("/ask", methods=["POST"])
def ask_single():
    """Handle a single prompt request.

    Flow & reasoning:
    - Validate input early to provide clear 4xx errors for clients.
    - Auto-select the best prompt based on user input keywords.
    - Build the final prompt by substituting user input into the template.
    - Call the OpenAI service synchronously and persist the exchange.
    - Wrap in try/except so unexpected issues produce an informative 500.
    """
    try:
        payload = request.get_json(force=True)
        user_input = payload.get("userInput") if payload else None

        # Validate that `userInput` exists and is a non-empty string.
        if not isinstance(user_input, str) or not user_input.strip():
            return jsonify({"error": "`userInput` is required and must be a non-empty string"}), 400

        # Auto-select best prompt based on user input keywords
        final_prompt = prompt_service.get_best_prompt(user_input)
        
        # Determine which prompt was actually selected (for history logging)
        selected_prompt_id = prompt_service.select_best_prompt(user_input)

        # Call the OpenAI API to get the AI response.
        ai_response = openai_service.call_openai(final_prompt)

        # Persist the interaction for auditing/analytics.
        doc = history_model.build_history_doc(user_input, final_prompt, ai_response, selected_prompt_id)
        db.history_col.insert_one(doc)

        # Return only the AI response to the client.
        return jsonify({"response": ai_response}), 200

    except ValueError as ve:
        # Known validation-like problems (e.g., missing prompt) map to 400.
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        # Unexpected errors are returned as 500 with a helpful message.
        return jsonify({"error": f"Internal server error: {e}"}), 500
