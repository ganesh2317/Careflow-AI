Chatbot Gemini Customization for System-Specific Responses

1. [x] Define system-specific rules and guidelines for Gemini responses.
   - Include rules for hospital management context: answer based on hospital data, maintain privacy, no medical advice, focus on services like appointments, queues, beds.

2. [x] Update the prompt in chatbot/views.py chat_message function.
   - Add system rules to the final_prompt to ensure responses align with system guidelines.

3. [x] Optionally, integrate saving chat messages to ChatMessage model for logging.

4. Test the updated chatbot functionality.
   - Verify responses are system-specific and appropriate.

5. Confirm with user if additional customizations are needed.
