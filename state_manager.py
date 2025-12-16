# state_manager.py

# Key: username (str)
# Value: List of messages (list[dict])
# Example: {'testuser': [{'role': 'user', 'content': 'Hi'}, {'role': 'ai', 'content': 'Hello'}]}
USER_CONTEXT_STORE = {}