import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import Blueprint, request, jsonify
from services import prompt_service, openai_service
import models.history as history_model
import db

batch_bp = Blueprint("batch_bp", __name__)


def _process_single_input(user_input, prompt_id="Education_Prompt"):
    """Synchronous worker to process one input: build prompt, call OpenAI, save history.

    Why synchronous? The OpenAI Python SDK is blocking; this helper is intended
    to be executed inside a ThreadPoolExecutor so many calls can run concurrently
    without blocking Flask's main thread.
    """
    final_prompt = prompt_service.get_prompt(prompt_id, user_input)
    ai_response = openai_service.call_openai(final_prompt)
    doc = history_model.build_history_doc(user_input, final_prompt, ai_response, prompt_id)
    db.history_col.insert_one(doc)
    return ai_response


@batch_bp.route("/ask-batch", methods=["POST"])
def ask_batch():
    """Handle batch requests concurrently while preserving input order.

    Why use asyncio + ThreadPoolExecutor:
    - Flask routes are synchronous by default.
    - The OpenAI SDK is synchronous (blocking I/O).
    - Using ThreadPoolExecutor with `run_in_executor` allows launching
      multiple blocking calls concurrently without blocking the Flask worker.
    - We preserve order by attaching indices to results and reordering after.
    """
    try:
        payload = request.get_json(force=True)
        inputs = payload.get("inputs") if payload else None

        # Validate inputs: non-empty list of strings.
        if not isinstance(inputs, list) or not inputs:
            return jsonify({"error": "`inputs` must be a non-empty list of strings"}), 400
        for i, item in enumerate(inputs):
            if not isinstance(item, str) or not item.strip():
                return jsonify({"error": f"All inputs must be non-empty strings. Bad item at index {i}"}), 400

        prompt_id = "Education_Prompt"

        # We use ThreadPoolExecutor because the calls are blocking; choose a pool
        # size proportional to the number of inputs but bounded to avoid overload.
        max_workers = min(10, len(inputs))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _run_all():
            results = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Schedule all jobs with their original index to preserve order.
                futures = [
                    loop.run_in_executor(executor, _process_single_input, inp, prompt_id)
                    for inp in inputs
                ]

                # Gather preserves the order of the futures list, so the final
                # results match the original input order.
                completed = await asyncio.gather(*futures, return_exceptions=True)
                return completed

        completed = loop.run_until_complete(_run_all())
        loop.close()

        # Convert exceptions into error messages for individual items.
        responses = []
        for item in completed:
            if isinstance(item, Exception):
                responses.append(f"Error processing input: {item}")
            else:
                responses.append(item)

        return jsonify({"responses": responses}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500
