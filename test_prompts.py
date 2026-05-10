"""
Test script to demonstrate multi-prompt selection logic.
Shows which prompt gets selected for different user inputs.
"""

from services import prompt_service

# Test cases
test_queries = [
    "What is the passing score in CA Final?",
    "How many subjects are in group 1?",
    "What's the best strategy to clear CA Final?",
    "What about subject exemptions?",
    "Tell me about CA Final",  # Should default to Education_Prompt
]

print("=" * 60)
print("PROMPT SELECTION TEST")
print("=" * 60)

for query in test_queries:
    selected_prompt = prompt_service.select_best_prompt(query)
    print(f"\nUser Input: {query}")
    print(f"Selected Prompt: {selected_prompt}")

print("\n" + "=" * 60)
print("Example: Get best prompt for a query")
print("=" * 60)

user_question = "What marks do I need to pass CA Final?"
print(f"\nUser: {user_question}")

try:
    final_prompt = prompt_service.get_best_prompt(user_question)
    print(f"\nSelected Prompt ID: {prompt_service.select_best_prompt(user_question)}")
    print(f"\nFinal Prompt (to be sent to AI):\n{final_prompt}")
except Exception as e:
    print(f"Note: {e}")
    print("(MongoDB might not be available, but prompt selection logic works)")
