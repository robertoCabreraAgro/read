import json # For parsing JSON arguments from CLI
from agent.dm_agent import DmAgent
from config import DATABASE_URL # Import DATABASE_URL from config

def main():
    # Use DATABASE_URL from config by default for the DmAgent.
    # The DmAgent's __init__ will use this if no specific db_url is passed.
    # For the CLI, we can let DmAgent use its default logic which now reads from config.
    # If you wanted the CLI to specifically override the config for some reason, 
    # you could pass db_url=यहां_specific_cli_db_url, but usually, you'd want config to rule.
    
    print(f"DmAgent will attempt to use database configured via DATABASE_URL (default: {DATABASE_URL})")
    
    try:
        # DmAgent will use DATABASE_URL from config if its db_url param is None (which is its new default)
        agent = DmAgent() 
    except Exception as e:
        print(f"Critical error during DmAgent initialization: {e}")
        print("This could be due to database issues or problems with engine initializations.")
        print("Please check database paths/permissions and API key configurations for engines.")
        return # Exit if agent cannot be initialized

    print("\n--- AI Dungeon Master CLI Initialized ---")
    if agent.ai_enabled: # Check DmAgent's AI status (related to its own direct OpenAI usage)
        print("OpenAI API Key found for DmAgent. AI is active for direct agent responses.")
    else:
        print("Warning: OpenAI API Key not found or AI disabled for DmAgent. Direct AI responses will be limited.")
    
    # Check Narrative Engine's AI status - NarrativeEngine prints its own status during its __init__
    # which is called when DmAgent is initialized. DmAgent also prints its own AI status.
    
    print("Type 'help' for a list of commands.")
    print("--------------------------------------")

    while True:
        try:
            user_input = input("DM-CLI > ").strip()
            if not user_input:
                continue

            parts = user_input.split(maxsplit=1) # Split command from the rest of the args
            command = parts[0].lower()
            args_str = parts[1] if len(parts) > 1 else ""
            
            # Simple arg splitting, more robust parsing might be needed for complex args
            # For commands taking multiple string args, we'll often join them.
            # For commands taking specific numbers of args (like addchar), we'll split more carefully.

            if command == "quit":
                print("Exiting DM-CLI...")
                break
            elif command == "help":
                print("\nAvailable Commands:")
                print("  quit                          - Exit the CLI.")
                print("  help                          - Show this help message.")
                print("  say <text>                    - Send <text> to the DM (AI processed).")
                print("  describe <topic>              - Get an AI-generated description of <topic>.")
                print("  check rule <keyword>          - Check rules for <keyword>.")
                print("  addchar <name> '<attrs_json>' '<inv_json>' <status> - Add a new character.")
                print("    Example: addchar Frodo '{\"str\":8,\"dex\":16}' '[\"ring\",\"lembas\"]' \"Weary\"")
                print("  getchar <name>                - Get character details for <name>.")
                print("  setworld '<event_desc>' '<effects_json>' - Set/update the world state.")
                print("    Example: setworld \"A red sun rises\" '[\"ominous_sky\",\"eerie_calm\"]'")
                print("--------------------------------------")
            
            elif command == "say":
                if args_str:
                    response = agent.process_input(args_str)
                    print(f"DM: {response}")
                else:
                    print("Usage: say <text to send to DM>")
            
            elif command == "describe":
                if args_str:
                    response = agent.trigger_narrative_engine(args_str)
                    print(f"Narrative: {response}")
                else:
                    print("Usage: describe <topic>")
            
            elif command == "check" and args_str.startswith("rule "):
                keyword = args_str.replace("rule ", "", 1).strip()
                if keyword:
                    response = agent.trigger_rules_engine_check(keyword)
                    print(f"RulesEngine: {response}")
                else:
                    print("Usage: check rule <keyword>")

            elif command == "addchar":
                # Expects: name '{"attr":"val"}' '["item"]' status
                try:
                    # A more robust parser would be better than simple split for quoted strings
                    # This is a basic attempt, assuming simple space separation for now after command.
                    # For JSON, it's better to pass them as single arguments.
                    # e.g. addchar Pippin '{"str":8}' '["pipe"]' Healthy
                    # A real CLI might use argparse or a library.
                    
                    # Temporary crude parsing: find first ' {', then ' [', then the rest
                    name_end_idx = args_str.find(" '{")
                    if name_end_idx == -1: raise ValueError("Attributes JSON string not found or malformed start.")
                    name = args_str[:name_end_idx]
                    
                    attrs_json_start_idx = name_end_idx + 1
                    attrs_json_end_idx = args_str.find("}' ", attrs_json_start_idx) # find end of json + space
                    if attrs_json_end_idx == -1: raise ValueError("Inventory JSON string not found or malformed start after attributes.")
                    attrs_json_str = args_str[attrs_json_start_idx : attrs_json_end_idx+1]
                    
                    inv_json_start_idx = attrs_json_end_idx + 2 # skip space and '{'
                    inv_json_end_idx = args_str.find("]' ", inv_json_start_idx)
                    if inv_json_end_idx == -1: raise ValueError("Status not found or malformed start after inventory.")
                    inv_json_str = args_str[inv_json_start_idx : inv_json_end_idx+1]
                    
                    status = args_str[inv_json_end_idx+2:].strip()

                    if not name or not status: # Basic check
                        raise ValueError("Name and status cannot be empty.")

                    attributes = json.loads(attrs_json_str)
                    inventory = json.loads(inv_json_str)
                    
                    char_data = {"name": name, "attributes": attributes, "inventory": inventory, "status": status}
                    new_char = agent.save_character_data(char_data)
                    if new_char:
                        print(f"Character '{new_char.name}' saved with ID {new_char.id}.")
                    else:
                        print("Failed to save character.")
                except json.JSONDecodeError as je:
                    print(f"Error: Invalid JSON provided. Details: {je}")
                    print("Usage: addchar <name> '<attrs_json>' '<inv_json>' <status>")
                    print("Example: addchar Frodo '{\"str\":8,\"dex\":16}' '[\"ring\",\"lembas\"]' \"Weary\"")
                    print("Ensure JSON strings are enclosed in single quotes and use double quotes for internal keys/strings.")
                except ValueError as ve:
                    print(f"Error parsing arguments for addchar: {ve}")
                    print("Usage: addchar <name> '<attrs_json>' '<inv_json>' <status>")
                    print("Example: addchar Frodo '{\"str\":8,\"dex\":16}' '[\"ring\",\"lembas\"]' \"Weary\"")
                except Exception as e:
                    print(f"An unexpected error occurred with addchar: {e}")

            elif command == "getchar":
                if args_str:
                    name = args_str.strip()
                    character = agent.get_character_data(name)
                    if character:
                        print(f"Character: {character.name}")
                        print(f"  ID: {character.id}")
                        print(f"  Attributes: {character.attributes}")
                        print(f"  Inventory: {character.inventory}")
                        print(f"  Status: {character.status}")
                    else:
                        print(f"Character '{name}' not found.")
                else:
                    print("Usage: getchar <name>")

            elif command == "setworld":
                try:
                    # Expects: "event description" '["effect1", "effect2"]'
                    desc_end_idx = args_str.find("' '") # End of description quote, start of effects quote
                    if desc_end_idx == -1 or not args_str.startswith("'") or not args_str.endswith("'"):
                         raise ValueError("Invalid format. Ensure event description and effects JSON are quoted.")

                    event_desc_str = args_str[1:desc_end_idx] # Remove leading quote
                    effects_json_str = args_str[desc_end_idx+2:] # Remove "' '" and get the rest
                    
                    if not effects_json_str.startswith("'") or not effects_json_str.endswith("'"):
                        raise ValueError("Effects JSON must be enclosed in single quotes.")
                    effects_json_str = effects_json_str[1:-1] # Remove outer quotes for effects JSON

                    active_effects = json.loads(effects_json_str)
                    
                    world_state = agent.update_world_state(event_desc_str, active_effects)
                    if world_state:
                        print(f"World state updated: Event - '{world_state.current_event}', Effects - {world_state.active_effects}")
                    else:
                        print("Failed to update world state.")
                except json.JSONDecodeError as je:
                    print(f"Error: Invalid JSON for effects. Details: {je}")
                    print("Usage: setworld '<event_desc>' '<effects_json>'")
                    print("Example: setworld 'A red sun rises' '[\"ominous_sky\",\"eerie_calm\"]'")
                    print("Ensure JSON strings are enclosed in single quotes and use double quotes for internal keys/strings.")
                except ValueError as ve:
                    print(f"Error parsing arguments for setworld: {ve}")
                    print("Usage: setworld '<event_desc>' '<effects_json>'")
                except Exception as e:
                    print(f"An unexpected error occurred with setworld: {e}")
            
            else:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

        except Exception as e:
            print(f"An error occurred in the command loop: {e}")
            # import traceback # For debugging
            # traceback.print_exc() # For debugging

    if agent:
        agent.close_session()
    print("CLI session closed.")

if __name__ == "__main__":
    main()
