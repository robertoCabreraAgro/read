import os
import json 
import openai 
from config import DATABASE_URL, OPENAI_API_KEY 
from database.engine import init_db, get_session
from database.models import (
    Character, WorldState, RuleSet, LoreTopic,
import json 
import openai 
from config import DATABASE_URL, OPENAI_API_KEY 
from database.engine import init_db, get_session
from database.models import (
    Character, WorldState, RuleSet, LoreTopic,
    CharacterLanguage, CharacterResource, CharacterTitle, CharacterCompatibleElement, CharacterReclusionState, 
    Technique, CharacterKnownTechniques, # For Technique integration
import json 
import openai 
from config import DATABASE_URL, OPENAI_API_KEY 
from database.engine import init_db, get_session
from database.models import (
    Character, WorldState, RuleSet, LoreTopic,
    CharacterLanguage, CharacterResource, CharacterTitle, CharacterCompatibleElement, CharacterReclusionState, 
    Technique, CharacterKnownTechniques, 
    DmGuidelineSet, CultivationRealm, CampaignEvent, DmSessionStructureItem 
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, or_ # Added or_ for keyword search
from sqlalchemy.orm import joinedload 
from engine.rules_engine import RulesEngine 
from engine.narrative_engine import NarrativeEngine 

class DmAgent:
    def __init__(self, db_url: str = None): 
        current_db_url = db_url if db_url is not None else DATABASE_URL
        init_db(current_db_url) 
        self.db_session = get_session()
        print(f"DmAgent initialized with DB session for URL: {current_db_url}")
        if current_db_url == "sqlite:///./default_dm_database.db": # Check against the actual default from config.py
            print("INFO: Using default SQLite database. For production, consider setting DATABASE_URL environment variable.")

        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY 
            self.ai_enabled = True
            print("DmAgent: OpenAI API key LOADED from config.")
        else:
            print("DmAgent Error: OPENAI_API_KEY not found in environment/config. AI features will be disabled.")
            self.ai_enabled = False
            
        self.rules_engine = RulesEngine(db_session=self.db_session)
        self.narrative_engine = NarrativeEngine() 
        print("RulesEngine and NarrativeEngine initialized within DmAgent.")

        # Load default DM Guidelines
        self.dm_guidelines: DmGuidelineSet | None = self.get_dm_guideline() # Default name is used
        if not self.dm_guidelines:
            print("Warning: Default DM Guidelines 'Directrices DM Completas - Mundo Wuxia Liáng Wǔzhào' not found in the database.")
        else:
            print(f"Default DM Guidelines '{self.dm_guidelines.name}' loaded.")

    # --- New Query Methods ---
    def get_dm_guideline(self, guideline_name: str = "Directrices DM Completas - Mundo Wuxia Liáng Wǔzhào") -> DmGuidelineSet | None:
        try:
            # Eager load related items if frequently accessed together
            # from sqlalchemy.orm import joinedload
            # return self.db_session.query(DmGuidelineSet).\
            #     options(joinedload(DmGuidelineSet.session_structure_items), joinedload(DmGuidelineSet.intro_chars_show_fields)).\
            #     filter_by(name=guideline_name).first()
            return self.db_session.query(DmGuidelineSet).filter_by(name=guideline_name).first()
        except SQLAlchemyError as e:
            print(f"Database error fetching DM Guideline '{guideline_name}': {e}")
            return None

    def get_lore_topic_by_name(self, topic_name: str) -> LoreTopic | None:
        try:
            return self.db_session.query(LoreTopic).filter_by(name=topic_name).first()
        except SQLAlchemyError as e:
            print(f"Database error fetching LoreTopic '{topic_name}': {e}")
            return None

    def get_all_cultivation_realms(self) -> list[CultivationRealm]:
        try:
            return self.db_session.query(CultivationRealm).order_by(CultivationRealm.realm_order).all()
        except SQLAlchemyError as e:
            print(f"Database error fetching Cultivation Realms: {e}")
            return []

    def get_recent_campaign_events(self, limit: int = 3) -> list[CampaignEvent]:
        try:
            return self.db_session.query(CampaignEvent).order_by(desc(CampaignEvent.id)).limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Database error fetching recent Campaign Events: {e}")
            return []
            
    def get_character_info_for_prompt(self, character_name: str) -> dict | None:
        character = self.get_character_data(character_name) 
        if not character:
            return None
        
        info = {
            "name": character.name,
            "level": character.level,
            "class": character.character_class,
            "race": character.race,
            "status": character.status_general,
            "dao": character.dao_philosophy,
            "affiliation": character.affiliation,
            "hp": f"{character.hp_current}/{character.hp_max}",
            "mana": f"{character.mana_current}/{character.mana_max}" if character.mana_max is not None else "N/A",
        }
        
        active_titles = [t.title_name for t in character.titles if t.is_active]
        if active_titles:
            info["titles"] = ", ".join(active_titles)
            
        compatible_elements = [ce.element_description for ce in character.compatible_elements]
        if compatible_elements:
            info["elements"] = ", ".join(compatible_elements)

        if character.reclusion_state:
            info["reclusion"] = (
                f"Start: Day {character.reclusion_state.start_day}, "
                f"End: Day {character.reclusion_state.end_day}, "
                f"Remaining: {character.reclusion_state.days_remaining} days"
            )
        return info

    # --- New Technique Query Methods ---
    def get_technique_details(self, technique_name: str) -> Technique | None:
        try:
            # Case-insensitive search can be useful here if technique names might vary slightly
            # from sqlalchemy import func
            # return self.db_session.query(Technique).filter(func.lower(Technique.name) == func.lower(technique_name)).first()
            return self.db_session.query(Technique).filter_by(name=technique_name).first()
        except SQLAlchemyError as e:
            print(f"Database error fetching Technique '{technique_name}': {e}")
            return None

    def get_character_known_techniques_objects(self, character_name: str) -> list[CharacterKnownTechniques]:
        character = self.get_character_data(character_name) # Existing method
        if character:
            # Eager load the technique details along with the association object
            return self.db_session.query(CharacterKnownTechniques).\
                options(joinedload(CharacterKnownTechniques.technique)).\
                filter_by(character_id=character.id).all()
        return []

    def get_formatted_known_techniques_for_prompt(self, character_name: str) -> str | None:
        known_techniques_associations = self.get_character_known_techniques_objects(character_name)
        if not known_techniques_associations:
            return None
        
        formatted_list = []
        for ckt in known_techniques_associations:
            if ckt.technique: # Ensure the technique object is loaded
                tech = ckt.technique
                desc_snippet = (tech.description[:50] + "...") if tech.description and len(tech.description) > 50 else tech.description
                formatted_list.append(
                    f"- {tech.name} (Rango: {tech.rank or 'N/A'}, Elemento: {tech.element_association or 'N/A'}, Coste: {tech.mana_cost or 'N/A'}). Efecto: {desc_snippet or 'No especificado'}."
                )
        return "\n".join(formatted_list) if formatted_list else None

    def find_campaign_events_by_keyword(self, keyword: str, limit: int = 10) -> list[CampaignEvent]:
        try:
            search_pattern = f"%{keyword}%"
            return self.db_session.query(CampaignEvent).filter(
                or_(
                    CampaignEvent.title.ilike(search_pattern),
                    CampaignEvent.summary_content.ilike(search_pattern),
                    CampaignEvent.event_tags_json.ilike(search_pattern) # Assumes tags are stored as JSON string list
                )
            ).order_by(desc(CampaignEvent.id)).limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Database error searching Campaign Events for keyword '{keyword}': {e}")
            return []

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
            rule_response_str = f"Rule check for '{action_to_check}': {rule_check_result.get('message')}"
            if rule_check_result.get('outcome') == 'success' and rule_check_result.get('rule_applied'):
                rule_response_str += f" Details: {rule_check_result.get('rule_applied')}"
            return rule_response_str

        if not self.ai_enabled or not openai.api_key:
            return "Error: AI functionality is not available. Check API key configuration."

        # --- Context Building ---
        context_parts = []
        if self.dm_guidelines:
            context_parts.append(f"Estilo del DM: {self.dm_guidelines.tone_style or 'No especificado'}.")
            context_parts.append(f"Enfoque del DM: {self.dm_guidelines.tone_focus or 'No especificado'}.")
            if self.dm_guidelines.dice_roll_rules: # Check specific attribute
                 context_parts.append(f"Reglas de Dados Clave: {self.dm_guidelines.dice_roll_rules.split('.')[0]}.") 
        
        char_info = self.get_character_info_for_prompt("Liáng Wǔzhào") # Assuming this is the main character for context
        if char_info:
            char_summary = f"Personaje Principal: {char_info['name']} (Nivel {char_info['level']} {char_info.get('class','N/A')}, {char_info.get('race','N/A')}). " \
                           f"Estado: {char_info.get('status','N/A')}. Dao: {char_info.get('dao','N/A')}. Afiliación: {char_info.get('affiliation','N/A')}. " \
                           f"HP: {char_info['hp']}, Mana: {char_info['mana']}."
            if char_info.get('titles'): char_summary += f" Títulos: {char_info['titles']}."
            if char_info.get('reclusion'): char_summary += f" Reclusión: {char_info['reclusion']}."
            context_parts.append(char_summary)

        recent_events = self.get_recent_campaign_events(limit=1)
        if recent_events:
            event = recent_events[0]
            event_days = f"(Días {event.day_range_start}"
            if event.day_range_end and event.day_range_end != event.day_range_start:
                event_days += f"-{event.day_range_end}"
            event_days += ")"
            context_parts.append(f"Evento Reciente {event_days}: {event.title} - {event.summary_content[:100]}...")

        # Basic keyword-based context fetching
        user_input_lower = user_input.lower()
        if "cultivo" in user_input_lower or "reino" in user_input_lower or "nivel de cultivo" in user_input_lower :
            realms = self.get_all_cultivation_realms()
            if realms:
                realm_list_str = ", ".join([f"{r.name} (Nivel aprox. PJ: {r.level_range})" for r in realms])
                context_parts.append(f"Reinos de Cultivo Conocidos: {realm_list_str}")
        
        if "flujo de energía" in user_input_lower or "chi/maná" in user_input_lower: # Example specific lore
            flujo_lore = self.get_lore_topic_by_name("Flujo de Energía Primordial (Chi/Maná)")
            if flujo_lore and flujo_lore.description:
                context_parts.append(f"Sobre Flujo de Energía: {flujo_lore.description[:150]}...")

        known_techniques_str = self.get_formatted_known_techniques_for_prompt("Liáng Wǔzhào")
        if known_techniques_str:
            context_parts.append(f"Técnicas Conocidas por Liáng Wǔzhào:\n{known_techniques_str}")


        # --- Prompt Formatting ---
        context_str = "\n".join([f"- {part}" for part in context_parts])
        
        system_prompt_content = "Eres un Dungeon Master (DM) para un juego de rol de texto estilo Wuxia. " \
                                "Tu objetivo es narrar eventos, describir situaciones, interpretar NPCs, y responder a las acciones del jugador " \
                                "de forma creativa y coherente con el mundo y las directrices proporcionadas."
        if self.dm_guidelines and self.dm_guidelines.system_base:
            system_prompt_content += f" El sistema de juego base es: {self.dm_guidelines.system_base}."
        
        action_context_str = ""
        # --- Detección y Contextualización del Uso de Técnicas (Simplificado) ---
        # Keywords for technique usage, ensure they are space-padded to avoid matching parts of words.
        technique_keywords = ["uso ", "activo ", "lanzo ", "utilizo ", "ejecuto "] 
        extracted_technique_name = None

        for keyword in technique_keywords:
            if keyword in user_input_lower:
                # Extract text after the keyword as potential technique name
                potential_name = user_input_lower.split(keyword, 1)[1].strip()
                # Further refinement: remove common follow-up words if any, e.g., "uso X y luego Y"
                # This is very basic; a proper NLP approach would be better.
                # For now, assume the first few words after keyword are the technique.
                extracted_technique_name = " ".join(potential_name.split()[:4]).strip(".!") # Take up to 4 words
                break
        
        if extracted_technique_name:
            # Check if Liáng Wǔzhào knows this technique or if it's a general technique
            # For simplicity, first check known techniques for a partial match (case-insensitive)
            lw_known_techs_objs = self.get_character_known_techniques_objects("Liáng Wǔzhào")
            found_known_tech_obj = None
            if lw_known_techs_objs:
                for ckt in lw_known_techs_objs:
                    if ckt.technique and extracted_technique_name.lower() in ckt.technique.name.lower():
                        found_known_tech_obj = ckt.technique
                        break
            
            technique_to_detail = found_known_tech_obj
            if not technique_to_detail: # If not in known, try to get general details
                technique_to_detail = self.get_technique_details(extracted_technique_name) # This requires exact match for now

            if technique_to_detail:
                tech_details = technique_to_detail
                action_context_str = (
                    f"\n[ACCIÓN DE TÉCNICA DECLARADA POR EL JUGADOR]\n"
                    f"Técnica: {tech_details.name} (Rango: {tech_details.rank or 'N/A'}, Elemento: {tech_details.element_association or 'N/A'})\n"
                    f"Descripción: {tech_details.description or 'No detallada.'}\n"
                    f"Efectos/Daño: {tech_details.damage_string or 'No especificado.'}\n"
                    f"Coste de Maná: {tech_details.mana_cost or 'N/A'}\n"
                    f"Por favor, narra la activación y el resultado inmediato de esta técnica. "
                    f"Asume un resultado exitoso o describe posibles consecuencias si la situación lo amerita. "
                    f"Las tiradas de dados y la validación final de reglas las gestionará el sistema de juego aparte."
                )
        
        full_prompt = f"[CONTEXTO DEL MUNDO Y DIRECTRICES]\n{context_str}\n{action_context_str}\n---\nEl jugador dice: \"{user_input}\"\n\nRespuesta del DM (narrando como IA Dungeon Master):"
        
        # print(f"\n--- PROMPT PARA IA ---\n{system_prompt_content}\n{full_prompt}\n---------------------\n") # For debugging

        messages_for_openai = [
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": full_prompt} 
        ]

        if os.getenv("DEBUG_DM_PROMPT", "False").lower() == "true":
            print("\n" + "="*20 + " PROMPT COMPLETO PARA OPENAI " + "="*20)
            for message in messages_for_openai:
                print(f"--- ROLE: {message['role']} ---")
                print(message['content'])
                print("-" * 60) # Separador más largo para el contenido
            print("="*60 + "\n")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=messages_for_openai
            )
            ai_response = response.choices[0].message['content'].strip()
            return ai_response
        except openai.APIAuthenticationError as e: # Specific error first
            print(f"OpenAI API Authentication Error: {e}")
            return "OpenAI API Key es inválido o no está autorizado. Por favor, verifica tu API key."
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
            # self.db_session.rollback() # Optional: rollback on error, though typically not needed for reads
            return None

    def save_character_data(self, character_data: dict) -> Character | None:
        """
        Creates or updates a Character object from a dictionary, focusing on direct fields
        and simple related data like languages and basic resources.
        If a character with the same name exists, it updates fields. Otherwise, creates new.
        """
        char_name = character_data.get("name")
        if not char_name:
            print("Error: Character name is required to save character data.")
            return None

        existing_char = self.db_session.query(Character).filter_by(name=char_name).first()

        try:
            if existing_char:
                print(f"Updating existing character: {char_name}")
                char = existing_char
            else:
                print(f"Creating new character: {char_name}")
                char = Character(name=char_name)
                self.db_session.add(char)

            direct_fields = [
                "level", "character_class", "race", "alignment", "background", 
                "experience_points", "strength_score", "dexterity_score", 
                "constitution_score", "intelligence_score", "wisdom_score", 
                "charisma_score", "proficiency_bonus", "hp_max", "hp_current", 
                "armor_class", "speed", "mana_max", "mana_current", "status_general"
            ]
            for field in direct_fields:
                if field in character_data:
                    setattr(char, field, character_data[field])
            
            # Handle custom_props_json
            if "custom_props_json" in character_data:
                if isinstance(character_data["custom_props_json"], (dict, list)):
                    char.custom_props_json = character_data["custom_props_json"]
                elif isinstance(character_data["custom_props_json"], str):
                    try:
                        char.custom_props_json = json.loads(character_data["custom_props_json"])
                    except json.JSONDecodeError:
                        print(f"Warning: custom_props_json for '{char_name}' is not valid JSON string. Skipping.")
                else:
                     print(f"Warning: custom_props_json for '{char_name}' is not a dict, list, or string. Skipping.")


            # Handle simple related data: Languages
            if "languages_known" in character_data and isinstance(character_data["languages_known"], list):
                if existing_char: # Clear old languages if updating
                    char.languages.clear() 
                for lang_name in character_data["languages_known"]:
                    if isinstance(lang_name, str): # Basic validation
                        char.languages.append(CharacterLanguage(language_name=lang_name))
            
            # Handle simple related data: Resources (e.g., micronucleo)
            if "simple_resources" in character_data and isinstance(character_data["simple_resources"], dict):
                if existing_char: # Clear old resources or implement more specific update logic
                    # For simplicity, clearing all and re-adding from this input.
                    # A more robust update would match resource by name.
                    char.resources.clear() 
                for res_name, res_data in character_data["simple_resources"].items():
                    if isinstance(res_data, dict) and "current" in res_data and "max" in res_data:
                        char.resources.append(CharacterResource(
                            resource_name=res_name,
                            current_value=res_data["current"],
                            max_value=res_data["max"]
                        ))
            
            self.db_session.commit()
            self.db_session.refresh(char) # Refresh to get ID and eager load what's set by default
            print(f"Character '{char.name}' (ID: {char.id}) saved/updated successfully.")
            return char
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Database error saving character '{char_name}': {e}")
            return None
        except Exception as e: # Catch other unexpected errors
            self.db_session.rollback() # Rollback on any error during this process
            print(f"Unexpected error saving character '{char_name}': {e}")
            # import traceback; traceback.print_exc() # For debugging
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

if __name__ == '__main__':
    # This test assumes populate_db.py has been run successfully with the new schema.
    print("Initializing DmAgent for Technique Integration testing (uses DATABASE_URL from config)...")
    agent = DmAgent() 

    if not agent.ai_enabled:
        print("AI is not enabled. Some functionalities might be limited or provide placeholder responses.")

    print("\n--- Testing DM Guideline Loading (from DmAgent.__init__) ---")
    if agent.dm_guidelines:
        print(f"Guidelines cargadas: {agent.dm_guidelines.name}")
        print(f"  Tono y Estilo: {agent.dm_guidelines.tone_style}")
        print(f"  Foco: {agent.dm_guidelines.tone_focus}")
        if agent.dm_guidelines.session_structure_items: # Check if the list is not empty
             print(f"  Estructura Sesión (1er item): {agent.dm_guidelines.session_structure_items[0].item_description}")
    else:
        print("DM Guidelines no se cargaron. Verifica que 'populate_db.py' haya sido ejecutado y el nombre sea correcto.")

    print("\n--- Testing LoreTopic Query ---")
    cultivation_lore = agent.get_lore_topic_by_name("Cultivo y Reinos de Poder")
    if cultivation_lore:
        print(f"LoreTopic encontrado: {cultivation_lore.name}")
        # print(f"  Descripción: {cultivation_lore.description[:100] if cultivation_lore.description else 'N/A'}...")
        if cultivation_lore.cultivation_realms:
            print(f"  Primer Reino de Cultivo (desde LoreTopic): {cultivation_lore.cultivation_realms[0].name} (Orden: {cultivation_lore.cultivation_realms[0].realm_order})")
    else:
        print("LoreTopic 'Cultivo y Reinos de Poder' no encontrado.")

    print("\n--- Testing Cultivation Realm Query ---")
    all_realms = agent.get_all_cultivation_realms()
    if all_realms:
        print(f"Total de Reinos de Cultivo encontrados: {len(all_realms)}")
        for realm_idx, realm in enumerate(all_realms):
            if realm_idx < 2 : # Print first 2
                print(f"  - {realm.name} (Orden: {realm.realm_order}, Rango Nivel PJ: {realm.level_range})")
    else:
        print("No se encontraron Reinos de Cultivo.")

    print("\n--- Testing Recent Campaign Events Query ---")
    recent_events = agent.get_recent_campaign_events(limit=2)
    if recent_events:
        print(f"Eventos Recientes (hasta 2):")
        for event in recent_events:
            event_days_str = f"Días {event.day_range_start}"
            if event.day_range_end and event.day_range_end != event.day_range_start:
                event_days_str += f"-{event.day_range_end}"
            print(f"  - Título: {event.title} ({event_days_str}), Resumen: {event.summary_content[:60]}...")
    else:
        print("No se encontraron eventos de campaña recientes.")
        
    print("\n--- Testing Character Info for Prompt (Liáng Wǔzhào) ---")
    liang_info = agent.get_character_info_for_prompt("Liáng Wǔzhào")
    if liang_info:
        print("Información de Liáng Wǔzhào para prompt:")
        for key, value in liang_info.items(): # Python 3.6+ dicts are ordered
            print(f"  {key.capitalize()}: {value}")
    else:
        print("No se encontró información para Liáng Wǔzhào (Asegúrate que populate_db.py haya sido ejecutado).")

    print("\n--- Testing Technique Query Methods ---")
    sample_tech_name = "Disparo de Fuego Primario" # Asumiendo que existe por populate_db.py
    tech_details = agent.get_technique_details(sample_tech_name)
    if tech_details:
        print(f"Detalles de '{sample_tech_name}': Rango {tech_details.rank}, Elemento {tech_details.element_association}, Coste Maná: {tech_details.mana_cost}")
        print(f"  Descripción: {tech_details.description}")
    else:
        print(f"Técnica '{sample_tech_name}' no encontrada.")

    print("\n--- Testing Known Techniques for Liáng Wǔzhào ---")
    lw_known_tech_objs = agent.get_character_known_techniques_objects("Liáng Wǔzhào")
    if lw_known_tech_objs:
        print(f"Liáng Wǔzhào conoce {len(lw_known_tech_objs)} técnicas (objetos CharacterKnownTechniques):")
        for ckt_obj in lw_known_tech_objs:
            if ckt_obj.technique:
                 print(f"  - {ckt_obj.technique.name} (Maestría: {ckt_obj.mastery_level or 'N/A'})")
    else:
        print("Liáng Wǔzhào no parece conocer técnicas o no se encontró el personaje.")

    formatted_known_techs = agent.get_formatted_known_techniques_for_prompt("Liáng Wǔzhào")
    if formatted_known_techs:
        print("\nTécnicas Conocidas por Liáng Wǔzhào (formateado para prompt):")
        print(formatted_known_techs)
    else:
        print("\nNo se pudieron formatear las técnicas conocidas de Liáng Wǔzhào para el prompt.")
    
    print("\n--- Testing save_character_data (simple character) - Opcional, mantener si es relevante ---")
    test_char_data = {
        "name": "Test Dummy", "level": 1, "character_class": "Común", "race": "Humano",
        "status_general": "Probando", "dao_philosophy": "Pragmatismo", "affiliation": "Ninguna"
    }
    saved_dummy = agent.save_character_data(test_char_data)
    if saved_dummy:
        print(f"Personaje de prueba '{saved_dummy.name}' guardado con ID {saved_dummy.id}.")
        retrieved_dummy = agent.get_character_info_for_prompt("Test Dummy")
        if retrieved_dummy:
            print(f"  Recuperado para prompt: {retrieved_dummy}")
    else:
        print("No se pudo guardar el personaje de prueba.")


    # Test process_input con el nuevo contexto de técnicas
    print("\n--- Testing process_input (con contexto de BD y Técnicas) ---")
    if agent.ai_enabled:
        user_queries_for_process_input = [
            "Qué opciones tengo?",
            "Uso mi Hoja de Fuego Adaptativa contra el espantapájaros!", # Assumes this tech is known
            "Activo mi Rayo Congelante Instantáneo!" # Assumes this tech is not known / fake
        ]
        for query in user_queries_for_process_input:
            print(f"\nJugador dice: \"{query}\"")
            ai_response = agent.process_input(query)
            print(f"DM (AI): {ai_response}")
    else:
        print("Skipping AI process_input test as AI is disabled.")

    print("\n--- Testing find_campaign_events_by_keyword ---")
    # Assuming populate_db.py created an event with "Monasterio" in title or summary
    found_events = agent.find_campaign_events_by_keyword(keyword="Monasterio")
    if found_events:
        print(f"Eventos encontrados para 'Monasterio':")
        for event in found_events:
            print(f"  - {event.title} (Días: {event.day_range_start}-{event.day_range_end})")
    else:
        print("No se encontraron eventos para 'Monasterio'. (populate_db.py debe crear alguno con este término)")
    
    print("\n--- Testing 'check rule for:' (sin cambios directos aquí) ---")
    rule_check_response = agent.process_input("check rule for: iniciativa") 
    print(f"DM (Rule Check para 'iniciativa'): {rule_check_response}")

    print("\n--- DmAgent technique and event integration example complete ---")
    agent.close_session()
