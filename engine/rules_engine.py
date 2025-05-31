import json
from sqlalchemy.orm import Session
from database.models import RuleSet # Assuming RuleSet is defined in your models

class RulesEngine:
    def __init__(self, db_session: Session):
        if db_session is None:
            raise ValueError("RulesEngine requires a valid database session.")
        self.db_session = db_session
        print("RulesEngine initialized with database session.")

    def check_rule(self, action_keyword: str, character_id: int = None) -> dict:
        """
        Checks for rules related to a given action_keyword.
        Character_id is not used yet but is a placeholder for future rule personalization.
        """
        try:
            all_rulesets = self.db_session.query(RuleSet).all()
            if not all_rulesets:
                return {"outcome": "no_rulesets", "message": "No rulesets found in the database."}

            found_rule_detail = None
            ruleset_name_origin = None

            for ruleset in all_rulesets:
                if ruleset.rules_json is None:
                    continue # Skip if rules field is null

                try:
                    # The 'rules' field in RuleSet model is expected to be JSON.
                    # SQLAlchemy's JSON type might automatically deserialize it to Python dict/list.
                    # If it's a string, json.loads() is needed.
                    if isinstance(ruleset.rules_json, str):
                        rules_data = json.loads(ruleset.rules_json)
                    else:
                        rules_data = ruleset.rules_json  # Assumed to be already parsed Python object by SQLAlchemy
                
                except json.JSONDecodeError as je:
                    print(f"JSONDecodeError for ruleset '{ruleset.name}': {je}. Rules: '{ruleset.rules_json}'")
                    continue # Skip this ruleset if JSON is malformed

                if isinstance(rules_data, list):
                    # Assumes a list of rule objects, e.g., [{"keyword": "attack", "details": ...}, ...]
                    for rule in rules_data:
                        if isinstance(rule, dict) and rule.get("keyword") == action_keyword:
                            found_rule_detail = rule
                            ruleset_name_origin = ruleset.name
                            break 
                elif isinstance(rules_data, dict):
                    # Assumes a dictionary where keys are action_keywords, e.g., {"attack": {"details": ...}, ...}
                    if action_keyword in rules_data:
                        found_rule_detail = rules_data[action_keyword]
                        ruleset_name_origin = ruleset.name
                        break 
                
                if found_rule_detail:
                    break # Found a rule, no need to check other rulesets

            if found_rule_detail:
                return {
                    "outcome": "success",
                    "ruleset_name": ruleset_name_origin,
                    "rule_applied": found_rule_detail,
                    "message": f"Rule for '{action_keyword}' found in ruleset '{ruleset_name_origin}'."
                }
            else:
                return {
                    "outcome": "not_found",
                    "message": f"No specific rule found for action '{action_keyword}' across all rulesets."
                }

        except Exception as e:
            # Catching generic Exception to ensure some response, but more specific errors are better.
            # For example, SQLAlchemyError for database issues.
            print(f"Error in RulesEngine.check_rule: {e}")
            # Consider logging the full traceback here for debugging
            # import traceback
            # print(traceback.format_exc())
            return {"outcome": "error", "message": f"An error occurred while checking rules for '{action_keyword}'."}

# Example of how to add a RuleSet (for manual testing with a DB session)
# if __name__ == '__main__':
#     from sqlalchemy import create_engine
#     from database.models import Base # Assuming Base is in your models
#     from database.engine import get_session, init_db
#
#     # Setup a temporary in-memory SQLite DB for this example
#     TEST_DB_URL = "sqlite:///:memory:"
#     init_db(TEST_DB_URL) # This initializes engine and creates tables
#     session = get_session()
#
#     # 1. Create and add a RuleSet with list-based rules
#     rules_list_json = json.dumps([
#         {"keyword": "stealth", "description": "Roll Dexterity (Stealth) vs Perception.", "difficulty_class_info": "Varies by situation"},
#         {"keyword": "persuade", "description": "Roll Charisma (Persuasion) vs Insight or fixed DC.", "difficulty_class_info": "DC 10 for simple, DC 20 for hard"}
#     ])
#     ruleset1 = RuleSet(name="Core Mechanics", rules_json=rules_list_json)
#     session.add(ruleset1)
#
#     # 2. Create and add a RuleSet with dictionary-based rules
#     rules_dict_json = json.dumps({
#         "magic_missile": {"spell_level": 1, "damage": "3d4+3 force", "range": "120 feet", "description": "Automatically hits."},
#         "fireball": {"spell_level": 3, "damage": "8d6 fire", "range": "150 feet", "radius": "20 feet", "save_type": "Dexterity for half"}
#     })
#     ruleset2 = RuleSet(name="Spell Rules", rules_json=rules_dict_json)
#     session.add(ruleset2)
#     
#     session.commit()
#     print("Added example rulesets to in-memory DB.")
#
#     # Initialize RulesEngine with the session
#     rules_engine = RulesEngine(db_session=session)
#
#     # Test check_rule
#     print("\n--- RulesEngine Tests ---")
#     action1 = "stealth"
#     result1 = rules_engine.check_rule(action1)
#     print(f"Check for '{action1}': {result1}")
#
#     action2 = "fireball"
#     result2 = rules_engine.check_rule(action2)
#     print(f"Check for '{action2}': {result2}")
#
#     action3 = "nonexistent_action"
#     result3 = rules_engine.check_rule(action3)
#     print(f"Check for '{action3}': {result3}")
#
#     action4 = "persuade" # From list
#     result4 = rules_engine.check_rule(action4)
#     print(f"Check for '{action4}': {result4}")
#
#     session.close()
#     print("Test session closed.")
