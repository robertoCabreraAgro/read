import openai
from openai.error import (
    APIAuthenticationError,
    APIConnectionError,
    RateLimitError,
    APIError,
)
from config import OPENAI_API_KEY  # Import from config

class NarrativeEngine:
    def __init__(self):
        # OpenAI API key is now primarily managed globally by DmAgent or set directly from config.
        # This engine will rely on openai.api_key being set prior to its use.
        if OPENAI_API_KEY and not openai.api_key:
            # If DmAgent didn't set it (e.g. NarrativeEngine instantiated standalone),
            # set it here.
            openai.api_key = OPENAI_API_KEY
            print("NarrativeEngine: OpenAI API key LOADED from config.")
        
        if openai.api_key:
            self.ai_enabled = True
            # Optional: print only if NarrativeEngine itself initialized it
            # print("NarrativeEngine: AI is enabled.")
        else:
            self.ai_enabled = False
            print("NarrativeEngine Warning: OpenAI API key not configured. AI features will be disabled.")


    def generate_description(self, topic: str, context: str = "general fantasy setting", tone: str = "neutral") -> str:
        if not self.ai_enabled: # Relies on self.ai_enabled set in __init__
            return f"Narrative Engine AI not configured. Cannot generate description for {topic}."
        
        # Check if openai.api_key is actually set (could be unset after __init__ by external factors, though unlikely here)
        if not openai.api_key:
            return f"Narrative Engine AI Error: OpenAI API key is missing at time of call. Cannot generate description for {topic}."

        system_message_content = "You are a master storyteller for a role-playing game, skilled in creating vivid and engaging descriptions. Focus on being concise yet evocative."
        
        # Prompt construction can be more sophisticated based on needs
        user_prompt = f"Describe the following topic for a player in a role-playing game: '{topic}'.\n"
        user_prompt += f"Context: {context}.\n"
        user_prompt += f"Tone: {tone}."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # Or your preferred model
                messages=[
                    {"role": "system", "content": system_message_content},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7, # Adjust for creativity vs. factuality
                max_tokens=150  # Adjust based on desired length
            )
            narrative = response.choices[0].message['content'].strip()
            return narrative
        except APIAuthenticationError as e:
            print(f"OpenAI API Authentication Error in NarrativeEngine: {e}")
            return f"Narrative AI Error: Authentication failed. Could not generate description for '{topic}'."
        except APIConnectionError as e:
            print(f"OpenAI API Connection Error in NarrativeEngine: {e}")
            return f"Narrative AI Error: Connection problem. Could not generate description for '{topic}'."
        except RateLimitError as e:
            print(f"OpenAI API Rate Limit Error in NarrativeEngine: {e}")
            return f"Narrative AI Error: Rate limit exceeded. Could not generate description for '{topic}'."
        except APIError as e:
            print(f"OpenAI API Error in NarrativeEngine: {e}")
            return f"Narrative AI Error: Could not generate description for '{topic}' due to API issue."
        except Exception as e:
            print(f"An unexpected error occurred in NarrativeEngine: {e}")
            return f"Sorry, an unexpected error occurred while generating the description for '{topic}'."

# Example Usage (for testing purposes, can be removed or adapted)
# if __name__ == '__main__':
#     # IMPORTANT: To run this example, you MUST set the OPENAI_API_KEY environment variable.
#     # e.g., export OPENAI_API_KEY='your_actual_api_key'
#     
#     narrative_eng = NarrativeEngine()
#
#     if not narrative_eng.ai_enabled:
#         print("AI is not enabled in NarrativeEngine. Exiting example.")
#     else:
#         print("\n--- NarrativeEngine AI Test ---")
#         topic1 = "an ancient, moss-covered shrine hidden deep in a forest"
#         description1 = narrative_eng.generate_description(topic1, context="A high fantasy world with forgotten gods", tone="mysterious and slightly ominous")
#         print(f"\nTopic: {topic1}\nDescription 1:\n{description1}")
#
#         topic2 = "a bustling marketplace in a desert oasis city"
#         description2 = narrative_eng.generate_description(topic2, context="A vibrant city that's a hub for traders and travelers from diverse cultures", tone="lively and sensory-rich")
#         print(f"\nTopic: {topic2}\nDescription 2:\n{description2}")
#
#         topic3 = "the interior of a derelict starship"
#         description3 = narrative_eng.generate_description(topic3, context="A science fiction setting, centuries after a galactic war", tone="eerie and decaying")
#         print(f"\nTopic: {topic3}\nDescription 3:\n{description3}")
#
#         # Test fallback if API key was missing (by manually unsetting for a new instance - tricky to test here directly)
#         # To truly test this, you'd run without OPENAI_API_KEY set in the environment.
#         print("\n--- Testing Fallback (simulated by assuming no key for a moment) ---")
#         # This part is illustrative; actual test requires running env without the key.
#         if not os.getenv("OPENAI_API_KEY"):
#             print("Simulating no API KEY for NarrativeEngine for this specific test...")
#             # temp_narrative_eng_no_key = NarrativeEngine() # This would print the error from __init__
#             # fallback_desc = temp_narrative_eng_no_key.generate_description("a simple village")
#             # print(fallback_desc) # Should show the "AI not configured" message.
#         else:
#             print("OPENAI_API_KEY is set, so direct fallback test is not run here.")
#
#         print("\nNarrativeEngine AI Test Complete.")
