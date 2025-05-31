import json  # For parsing JSON arguments from CLI
import os  # For checking DEBUG_DM_PROMPT in main's startup message
from agent.dm_agent import DmAgent
from config import DATABASE_URL  # Import DATABASE_URL from config

def main():
    # Use DATABASE_URL from config by default for the DmAgent.
    print(f"DmAgent will attempt to use database configured via DATABASE_URL (default: {DATABASE_URL})")
    if os.getenv("DEBUG_DM_PROMPT", "False").lower() == "true":
        print("INFO: DEBUG_DM_PROMPT is set to True. Full AI prompts will be printed.")
    
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
                print("  addchar <name> <level> <class> <race> - Add a new basic character.")
                print("    Example: addchar Frodo 1 Hobbit Rogue")
                print("  getchar <name>                - Get detailed character sheet for <name>.")
                print("  setworld '<event_desc>' '<effects_json>' - Set/update the world state.")
                print("    Example: setworld \"A red sun rises\" '[\"ominous_sky\",\"eerie_calm\"]'")
                print("  addevent \"<title>\" \"<summary>\" <day_start> [day_end] [tags_json] - Add a new campaign event.")
                print("  history [N]                   - Show the N most recent campaign events (default N=5).")
                print("  find event <keyword>          - Search campaign events by keyword in title, summary, or tags.")
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
                # Simplified: addchar <name> <level> <class> <race>
                try:
                    args = args_str.split(maxsplit=3) # name, level, class, race (race can have spaces)
                    if len(args) < 4:
                        raise ValueError("Not enough arguments.")
                    
                    name = args[0]
                    try:
                        level = int(args[1])
                    except ValueError:
                        raise ValueError("Level must be an integer.")
                    char_class = args[2]
                    race = args[3]

                    character_data = {
                        "name": name,
                        "level": level,
                        "character_class": char_class,
                        "race": race,
                        # Default other essential fields or let save_character_data handle defaults
                        "hp_max": 10 + (level -1) * 5, # Example default HP
                        "hp_current": 10 + (level-1) * 5,
                        "strength_score": 10, # Example defaults
                        "dexterity_score": 10,
                        "constitution_score": 10,
                        "intelligence_score": 10,
                        "wisdom_score": 10,
                        "charisma_score": 10,
                    }
                    new_char = agent.save_character_data(character_data)
                    if new_char:
                        print(f"Character '{new_char.name}' (Level {new_char.level} {new_char.race} {new_char.character_class}) saved with ID {new_char.id}.")
                    else:
                        print(f"Failed to save character '{name}'. Check logs for details.")
                except ValueError as ve:
                    print(f"Error: {ve}")
                    print("Usage: addchar <name> <level> <class> <race>")
                    print("Example: addchar Frodo 1 Hobbit Rogue")
                except Exception as e:
                    print(f"An unexpected error occurred with addchar: {e}")

            elif command == "getchar":
                if args_str:
                    name = args_str.strip()
                    character = agent.get_character_data(name)
                    if character:
                        print(f"\n--- Character Sheet: {character.name} ---")
                        print(f"ID: {character.id}")
                        print(f"Level: {character.level} {character.race} {character.character_class}")
                        print(f"Alignment: {character.alignment if character.alignment else 'N/A'}")
                        print(f"Background: {character.background if character.background else 'N/A'}")
                        print(f"XP: {character.experience_points}")
                        print(f"HP: {character.hp_current}/{character.hp_max}")
                        ac_str = str(character.armor_class) if character.armor_class is not None else "N/A"
                        speed_str = str(character.speed) if character.speed is not None else "N/A"
                        print(f"AC: {ac_str}, Speed: {speed_str} ft")
                        
                        mana_str = "N/A"
                        if character.mana_max is not None:
                            mana_str = f"{character.mana_current}/{character.mana_max}"
                        print(f"Mana: {mana_str}")
                        print(f"Status: {character.status_general if character.status_general else 'N/A'}")
                        print(f"Proficiency Bonus: +{character.proficiency_bonus}")

                        print("\nAttributes:")
                        print(f"  STR: {character.strength_score}, DEX: {character.dexterity_score}, CON: {character.constitution_score}")
                        print(f"  INT: {character.intelligence_score}, WIS: {character.wisdom_score}, CHA: {character.charisma_score}")

                        print("\nSaving Throw Proficiencies:")
                        profs = [stp.attribute_name for stp in character.saving_throw_proficiencies if stp.is_proficient]
                        print(f"  {', '.join(profs) if profs else 'None'}")

                        print("\nSkill Proficiencies:")
                        skill_profs = [sp.skill_name for sp in character.skill_proficiencies if sp.is_proficient]
                        print(f"  {', '.join(skill_profs) if skill_profs else 'None'}")
                        
                        print("\nLanguages:")
                        langs = [lang.language_name for lang in character.languages]
                        print(f"  {', '.join(langs) if langs else 'None'}")

                        print("\nFeatures & Traits:")
                        if character.features_traits:
                            for ft in character.features_traits:
                                type_str = f" ({ft.type})" if ft.type else ""
                                print(f"  - {ft.name}{type_str}: {ft.description[:70] + '...' if ft.description and len(ft.description) > 70 else ft.description if ft.description else 'No description.'}")
                        else:
                            print("  None")

                        print("\nResources:")
                        if character.resources:
                            for res in character.resources:
                                print(f"  - {res.resource_name}: {res.current_value}/{res.max_value}")
                        else:
                            print("  None")

                        print("\nInventory:")
                        if character.inventory_items:
                            for item in character.inventory_items:
                                equipped_str = " (Equipped)" if item.is_equipped else ""
                                print(f"  - {item.item_name} (x{item.quantity}){equipped_str}")
                        else:
                            print("  None")
                        
                        print("\nCustom Properties:")
                        if character.custom_props_json:
                            # Assuming custom_props_json is already a dict due to SQLAlchemy JSON type
                            print(json.dumps(character.custom_props_json, indent=2))
                        else:
                            print("  None")
                        print("--------------------------------------")
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
                        print(f"World state updated: Event - '{world_state.current_event}', Effects - {world_state.active_effects_json}")
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

            elif command == "addevent":
                import shlex
                try:
                    parts = shlex.split(args_str)
                    if len(parts) < 3:
                        raise ValueError("Not enough arguments.")
                    title = parts[0]
                    summary = parts[1]
                    day_start = int(parts[2])
                    day_end = int(parts[3]) if len(parts) > 3 else None
                    tags = json.loads(parts[4]) if len(parts) > 4 else None
                    event = agent.create_campaign_event(title, summary, day_start, day_end, tags)
                    if event:
                        print(f"Campaign event '{event.title}' added with ID {event.id}.")
                    else:
                        print("Failed to add campaign event.")
                except ValueError as ve:
                    print(f"Error: {ve}")
                    print("Usage: addevent \"<title>\" \"<summary>\" <day_start> [day_end] [tags_json]")
                except json.JSONDecodeError as je:
                    print(f"Error parsing tags JSON: {je}")
                except Exception as e:
                    print(f"An unexpected error occurred with addevent: {e}")

            elif command == "history":
                limit = 5 # Default limit
                if args_str:
                    try:
                        limit = int(args_str)
                        if limit <= 0:
                            print("Error: Number of events (N) must be positive.")
                            continue
                    except ValueError:
                        print(f"Error: '{args_str}' is not a valid number for N. Using default N={limit}.")
                
                events = agent.get_recent_campaign_events(limit=limit)
                if events:
                    print(f"\n--- Historial Reciente de la Campaña (Últimos {len(events)} eventos) ---")
                    for event in events:
                        days_str = f"Días {event.day_range_start}"
                        if event.day_range_end and event.day_range_end != event.day_range_start:
                            days_str += f"-{event.day_range_end}"
                        
                        print(f"{days_str}: {event.title}")
                        print(f"  Resumen: {event.summary_content}")
                        if event.full_details_json: # Print some details if available
                            details_to_show = {k: v for k, v in event.full_details_json.items() if k in ["personajes_clave", "impacto_inicial", "temas"]}
                            if details_to_show : print(f"  Detalles clave: {json.dumps(details_to_show, ensure_ascii=False)}")
                        print("---")
                else:
                    print("No hay eventos recientes en la campaña.")

            elif command == "find" and args_str.startswith("event "):
                keyword = args_str.replace("event ", "", 1).strip()
                if not keyword:
                    print("Usage: find event <keyword>")
                    continue
                
                events = agent.find_campaign_events_by_keyword(keyword=keyword)
                if events:
                    print(f"\n--- Eventos Encontrados para \"{keyword}\" ---")
                    for event in events:
                        days_str = f"Días {event.day_range_start}"
                        if event.day_range_end and event.day_range_end != event.day_range_start:
                            days_str += f"-{event.day_range_end}"
                        print(f"{days_str}: {event.title}")
                        print(f"  Resumen: {event.summary_content}")
                        if event.event_tags_json: print(f"  Tags: {event.event_tags_json}")
                        print("---")
                else:
                    print(f"No se encontraron eventos para \"{keyword}\".")
            
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
