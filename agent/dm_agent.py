import os
import openai # Import OpenAI library
import openai # Import OpenAI library
from config import DATABASE_URL, OPENAI_API_KEY # Import from config
from database.engine import init_db, get_session
from database.models import Character, WorldState, RuleSet, LoreTopic 
from sqlalchemy.exc import SQLAlchemyError
from engine.rules_engine import RulesEngine 
from engine.narrative_engine import NarrativeEngine 

class DmAgent:
    def __init__(self, db_url: str = None): # Default db_url is now None
        # Use DATABASE_URL from config if db_url is not explicitly passed
        current_db_url = db_url if db_url is not None else DATABASE_URL
        
        # Database initialization
        init_db(current_db_url) # Use current_db_url
        self.db_session = get_session()
        print(f"DmAgent initialized with DB session for URL: {current_db_url}")
        if current_db_url == "sqlite:///./default_dm_database.db":
            print("INFO: Using default SQLite database. For production, set DATABASE_URL environment variable.")

        # OpenAI API Key Initialization from config
        # The NarrativeEngine will also use this global openai.api_key if set here.
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY # Set the global API key for the openai library
            self.ai_enabled = True
            print("DmAgent: OpenAI API key LOADED from config.")
        else:
            print("DmAgent Error: OPENAI_API_KEY not found in environment/config. AI features will be disabled.")
            self.ai_enabled = False
            
        # Initialize RulesEngine with the database session
        self.rules_engine = RulesEngine(db_session=self.db_session)
        # Initialize NarrativeEngine
        # NarrativeEngine will use the openai.api_key set globally above or handle its absence.
        self.narrative_engine = NarrativeEngine() 
        print("RulesEngine and NarrativeEngine initialized within DmAgent.")


    def trigger_narrative_engine(self, topic: str, context: str = "A player asked for a description.", tone: str = "informative") -> str:
        """
        Triggers the narrative engine to generate a description.
        """
        if not self.ai_enabled: # Check DmAgent's overall AI readiness
            return "Narrative generation disabled because AI is not configured in DmAgent."
        if not hasattr(self, 'narrative_engine'): # Should always exist if __init__ ran
             return "Narrative Engine component not found."
        # NarrativeEngine's own ai_enabled flag will be checked internally by its method
        return self.narrative_engine.generate_description(topic, context, tone)

    def trigger_rules_engine_check(self, keyword: str) -> dict:
        """
        Triggers the rules engine to check a rule.
        """
        if not hasattr(self, 'rules_engine'):
            # This should not happen if __init__ is correct
            return {"outcome": "error", "message": "Rules Engine not initialized."}
        return self.rules_engine.check_rule(keyword)

    def process_input(self, user_input: str) -> str:
        # Optional: Illustrative call to RulesEngine (can be expanded later)
        # For example, if user input is an action that needs a rule check
        # This is a simplistic check; real integration would be more nuanced.
        if user_input.lower().startswith("check rule for:"):
            action_to_check = user_input.lower().replace("check rule for:", "").strip()
            rule_check_result = self.rules_engine.check_rule(action_keyword=action_to_check)
            print(f"Rule check for '{action_to_check}': {rule_check_result}")
            # This result could then be passed to the AI or used to modify the AI's prompt
            # For now, just return a message indicating the check was done.
            return f"Rule check performed for '{action_to_check}'. Details: {rule_check_result.get('message')}"

        if not self.ai_enabled or not openai.api_key:
            return "Error: AI functionality is not available. Check API key configuration."

        try:
            # Constructing a simple prompt
            # For more complex scenarios, this prompt engineering would be more sophisticated
            # and could involve fetching context from the database (e.g., character info, world state)
            
            # Example: Retrieve character data if relevant (illustrative)
            # character_name = "PlayerCharacter" # This would be dynamically determined
            # character = self.get_character_data(character_name)
            # char_info_prompt = ""
            # if character:
            #    char_info_prompt = f" The current character is {character.name}, with status {character.status}."

            # Example: Retrieve world state (illustrative)
            # current_world_state = self.db_session.query(WorldState).first()
            # world_info_prompt = ""
            # if current_world_state:
            #     world_info_prompt = f" The current world event is: {current_world_state.current_event}."

            # Simple prompt for now
            system_prompt = "You are a creative and engaging Dungeon Master for a text-based adventure game."
            # full_prompt = f"{char_info_prompt}{world_info_prompt} The player says: {user_input}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # Or your preferred model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input} 
                ]
            )
            ai_response = response.choices[0].message['content'].strip()
            return ai_response
        except openai.APIAuthenticationError as e:
            print(f"OpenAI API Authentication Error: {e}")
            return "OpenAI API Key is invalid or not authorized. Please check your API key."
        except openai.APIConnectionError as e:
            print(f"OpenAI API Connection Error: {e}")
            return "Could not connect to OpenAI API. Please check your network connection."
        except openai.RateLimitError as e:
            print(f"OpenAI API Rate Limit Error: {e}")
            return "OpenAI API rate limit exceeded. Please try again later."
        except openai.APIError as e: # Catch other OpenAI specific errors
            print(f"OpenAI API Error: {e}")
            return "Sorry, I encountered an error trying to process your request with the AI."
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred while communicating with the AI."

    def get_character_data(self, character_name: str) -> Character | None:
        """
        Queries the Character table for a character by name.
        Returns the Character object if found, otherwise None.
        """
        try:
            character = self.db_session.query(Character).filter_by(name=character_name).first()
            return character
        except SQLAlchemyError as e:
            print(f"Error querying character '{character_name}': {e}")
            # self.db_session.rollback() # Optional: rollback on error
            return None

    def save_character_data(self, character_data: dict) -> Character | None:
        """
        Creates a new Character object from a dictionary, saves it to the DB.
        Returns the newly created Character object or None on error.
        """
        try:
            new_character = Character(
                name=character_data.get("name"),
                attributes=character_data.get("attributes", {}),
                inventory=character_data.get("inventory", []),
                status=character_data.get("status", "unknown")
            )
            self.db_session.add(new_character)
            self.db_session.commit()
            return new_character
        except SQLAlchemyError as e:
            print(f"Error saving character '{character_data.get('name')}': {e}")
            self.db_session.rollback()
            return None

    def update_world_state(self, event_description: str, active_effects: list) -> WorldState | None:
        """
        Updates the existing WorldState or creates a new one.
        For simplicity, assumes a single WorldState entry (fetches the first one).
        Returns the WorldState object or None on error.
        """
        try:
            # Try to get the first WorldState entry
            world_state = self.db_session.query(WorldState).first()

            if world_state:
                world_state.current_event = event_description
                world_state.active_effects = active_effects
            else:
                # If no world state exists, create a new one
                world_state = WorldState(
                    current_event=event_description,
                    active_effects=active_effects
                )
                self.db_session.add(world_state)
            
            self.db_session.commit()
            return world_state
        except SQLAlchemyError as e:
            print(f"Error updating world state: {e}")
            self.db_session.rollback()
            return None

    def close_session(self):
        """Closes the database session."""
        if self.db_session:
            self.db_session.close()
            print("Database session closed.")

# Example Usage (for testing purposes, can be removed)
# if __name__ == '__main__':
#     # IMPORTANT: To run this example, you MUST set the OPENAI_API_KEY environment variable.
#     # e.g., export OPENAI_API_KEY='your_actual_api_key'
#     # Also, the default database is now PostgreSQL, so for local testing without a PG server,
#     # you might want to change the db_url back to "sqlite:///:memory:" temporarily.
#
#     print("Starting DmAgent example...")
#     # agent = DmAgent(db_url="sqlite:///:memory:") # Use this for quick local test without PG
#     agent = DmAgent() # Uses default PostgreSQL, ensure your DB and OPENAI_API_KEY are set
#
#     if not agent.ai_enabled:
#         print("AI is not enabled. Proceeding with limited functionality for example.")
#
#     # Example of adding a ruleset to the DB if using sqlite for testing
#     if "sqlite" in agent.db_session.bind.url.drivername : # Check if using SQLite for this test
#         from database.models import RuleSet
#         import json
#         print("Attempting to add a sample ruleset for testing RulesEngine...")
#         sample_rules_list = json.dumps([
#             {"keyword": "attack", "description": "Roll D20 + STR mod vs AC.", "effect": "On hit, roll damage."},
#             {"keyword": "sneak", "description": "Roll DEX (Stealth) vs WIS (Perception).", "effect": "If successful, gain advantage or remain undetected."}
#         ])
#         existing_ruleset = agent.db_session.query(RuleSet).filter_by(name="Basic Actions").first()
#         if not existing_ruleset:
#             try:
#                 basic_rules = RuleSet(name="Basic Actions", rules=sample_rules_list)
#                 agent.db_session.add(basic_rules)
#                 agent.db_session.commit()
#                 print("Sample 'Basic Actions' ruleset added to the database.")
#             except Exception as e_db:
#                 print(f"Error adding sample ruleset: {e_db}")
#                 agent.db_session.rollback()
#         else:
#             print("'Basic Actions' ruleset already exists.")
#
#     print("DmAgent initialized. Type 'quit' to exit.")
#     print("You can test rule checking by typing 'check rule for: attack' or 'check rule for: sneak'")
#         # Test saving a character (optional, if you have a DB running)
#         # try:
#         #     char_data = {
#         #         "name": "Elara",
#         #         "attributes": {"wisdom": 16, "magic_affinity": 7},
#         #         "inventory": [{"item_name": "Ancient Tome", "quantity": 1}],
#         #         "status": "Seeking knowledge"
#         #     }
#         #     elara = agent.save_character_data(char_data)
#         #     if elara:
#         #         print(f"Saved character: {elara.name}, ID: {elara.id}")
#         # except Exception as e:
#         #     print(f"Could not save character during example: {e}")
#
#         # Simple interaction loop
#         while True:
#             user_query = input("Player: ")
#             if user_query.lower() == "quit":
#                 break
#             dm_response = agent.process_input(user_query)
#             print(f"DM: {dm_response}")
#
#     # Test saving a character
#     char_data = {
#         "name": "Liáng Wùzhào",
#         "attributes": {"strength": 15, "cultivation_level": 5},
#         "inventory": [{"item_name": "Spirit Sword", "quantity": 1}],
#         "status": "Meditating"
#     }
#     liáng = agent.save_character_data(char_data)
#     if liáng:
#         print(f"Saved character: {liáng.name}, ID: {liáng.id}")
#
#     # Test retrieving a character
#     retrieved_char = agent.get_character_data("Liáng Wùzhào")
#     if retrieved_char:
#         print(f"Retrieved character: {retrieved_char.name}, Attributes: {retrieved_char.attributes}")
#     else:
#         print("Character not found.")
#
#     # Test updating world state
#     ws = agent.update_world_state("A mysterious portal opens", ["planar_instability"])
#     if ws:
#         print(f"World state updated: Event - {ws.current_event}, Effects - {ws.active_effects}")
#
#     ws2 = agent.update_world_state("The portal stabilizes", ["planar_instability", "portal_stable"])
#     if ws2:
#         print(f"World state updated again: Event - {ws2.current_event}, Effects - {ws2.active_effects}")
#
#     agent.close_session()
