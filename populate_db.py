#!/usr/bin/env python3
"""
Complete database population script for AI Dungeon Master CLI.
Handles all tables including encounters, sessions, spells, and party management.
"""

import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from database.engine import init_db, get_session
from database.models import (
    Base, 
    # Core Models
    Character, CharacterSavingThrowProficiency, CharacterSkillProficiency, 
    CharacterLanguage, CharacterFeatureTrait, CharacterResource, 
    CharacterReclusionState, CharacterTitle, CharacterCompatibleElement,
    CharacterSpellSlot, CharacterKnownSpell, CharacterCondition,
    
    # Techniques and Spells
    Technique, CharacterKnownTechniques, Spell,
    
    # Combat and Actions
    Attack, InventoryItem, Condition,
    
    # World and Lore
    LoreTopic, CultivationRealm, Sect, Npc, Location,
    
    # Campaign Management
    CampaignEvent, Party, Session, Encounter, EncounterParticipant,
    
    # Dice and History
    DiceRollHistory,
    
    # DM and Rules
    DmGuidelineSet, DmSessionStructureItem, DmIntroCharShowField,
    RuleSet, WorldState
)
from config import DATABASE_URL

# --- Data Loading ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def _load_json(name: str) -> dict | list:
    """Load JSON data from the data directory."""
    path = os.path.join(DATA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load all JSON data
try:
    DM_RULES_DATA = _load_json("dm_rules.json")
    WORLD_RULES_DATA = _load_json("world_rules.json")
    FIRE_TECHNIQUES_DATA = _load_json("fire_techniques.json")
    NARRATIVE_EVENTS_DATA = _load_json("narrative_events.json")
    LIANG_WUZHAO_FULL_JSON = _load_json("liang_wuzhao.json")
    SPELLS_DATA = _load_json("spells.json")
    ATTACKS_DATA = _load_json("attacks.json")
    CHARACTERS_DATA = _load_json("characters.json")
    SECTS_DATA = _load_json("sects.json")
    NPCS_DATA = _load_json("npcs.json")
    CONDITIONS_DATA = _load_json("conditions.json")
    INVENTORY_DATA = _load_json("inventory_items.json")
    ELEMENTS_DATA = _load_json("elements.json")
    
    # Sample data for new features
    SAMPLE_ENCOUNTERS = {
        "encounters": [
            {
                "id": 1,
                "name": "Emboscada en el Valle Roto",
                "encounter_type": "combat",
                "difficulty": "medium",
                "expected_party_level": 3,
                "environment": "forest_valley",
                "status": "completed"
            }
        ]
    }
    
    SAMPLE_LOCATIONS = {
        "locations": [
            {
                "id": 1,
                "name": "Monasterio Silencioso",
                "location_type": "ruins",
                "region": "Valle del Eco Perdido",
                "description": "Ruinas del antiguo monasterio donde Liáng Wǔzhào entrenaba.",
                "current_status": "destroyed"
            },
            {
                "id": 2,
                "name": "Cruce de los Mil Vientos", 
                "location_type": "crossroads",
                "region": "Tierras Centrales",
                "description": "Importante cruce de caminos donde se encuentran viajeros de todas las sectas.",
                "current_status": "active"
            }
        ]
    }
    
except FileNotFoundError as e:
    print(f"Warning: Could not load some JSON files: {e}")
    print("Some features may not be populated. Ensure all JSON files exist in the data/ directory.")

# --- Population Functions ---

def populate_dm_guidelines(db_session: Session, data: dict):
    """Populate DM guidelines and rules."""
    print("Populating DM Guidelines...")
    
    rules_data = data.get("rules_for_dm_agent", {})
    guideline_name = "Directrices DM Completas - Mundo Wuxia Liáng Wǔzhào"
    
    guideline_set = db_session.query(DmGuidelineSet).filter_by(name=guideline_name).first()
    if not guideline_set:
        guideline_set = DmGuidelineSet(name=guideline_name)
        db_session.add(guideline_set)
        print(f"  DmGuidelineSet '{guideline_name}' created.")
    else:
        print(f"  DmGuidelineSet '{guideline_name}' already exists. Updating...")

    # Extract data from dm_rules.json structure
    guideline_set.system_base = "D&D 5e + Sistema Wuxia Personalizado"
    guideline_set.setting_description = "Mundo de cultivo con elementos de D&D 5e"
    guideline_set.dice_roll_rules = rules_data.get("2_manejo_de_dados", {}).get("modelo", {}).get("responsabilidades", [""])[0] if rules_data.get("2_manejo_de_dados") else None
    guideline_set.tone_difficulty = "Desafiante pero justo"
    guideline_set.tone_focus = rules_data.get("4_narracion_y_ambientacion", {}).get("tono", [""])[0] if rules_data.get("4_narracion_y_ambientacion") else None
    guideline_set.tone_style = rules_data.get("4_narracion_y_ambientacion", {}).get("estilo", "") if rules_data.get("4_narracion_y_ambientacion") else None

    # Session structure items
    guideline_set.session_structure_items.clear()
    session_structure = rules_data.get("5_estructura_de_aventura", {})
    if session_structure:
        for item in session_structure.get("resumen_de_progreso", []):
            guideline_set.session_structure_items.append(DmSessionStructureItem(item_description=item))
    
    # Character intro fields
    guideline_set.intro_chars_show_fields.clear()
    char_fields = rules_data.get("4_narracion_y_ambientacion", {}).get("personajes_relevantes", {}).get("mostrar", [])
    for field in char_fields:
        guideline_set.intro_chars_show_fields.append(DmIntroCharShowField(field_name=field))
    
    print(f"  DmGuidelineSet '{guideline_name}' populated/updated.")

def populate_world_lore(db_session: Session, data: dict):
    """Populate world lore and cultivation realms."""
    print("Populating World Lore...")
    
    world_rules = data.get("world_rules", {})
    
    # Create main lore topic for cultivation
    cultivation_topic_name = "Cultivo y Reinos de Poder"
    cultivation_topic = db_session.query(LoreTopic).filter_by(name=cultivation_topic_name).first()
    if not cultivation_topic:
        cultivation_topic = LoreTopic(
            name=cultivation_topic_name,
            topic_type="cultivation_realms",
            description="Sistema de progresión espiritual del mundo Wuxia"
        )
        db_session.add(cultivation_topic)
        print(f"  LoreTopic '{cultivation_topic_name}' created.")
    
    # Load cultivation realms from separate file if it exists
    try:
        cultivation_data = _load_json("cultivation_realms.json")
        realms_list = cultivation_data.get("cultivation_realms", {}).get("niveles", [])
        
        # Clear existing realms
        cultivation_topic.cultivation_realms.clear()
        db_session.flush()
        
        for realm_data in realms_list:
            new_realm = CultivationRealm(
                realm_order=realm_data.get("nivel", 1),
                name=realm_data.get("nombre", "Reino Desconocido"),
                level_range=f"Nivel {realm_data.get('nivel', 1)}",
                theme=realm_data.get("tema", ""),
                estado=realm_data.get("estado", ""),
                subetapa=realm_data.get("subetapa", ""),
                exp_required=realm_data.get("exp", 0)
            )
            cultivation_topic.cultivation_realms.append(new_realm)
        
        print(f"  Added {len(realms_list)} cultivation realms.")
    except FileNotFoundError:
        print("  No cultivation_realms.json found, skipping detailed realm population.")
    
    # Create other lore topics from world_rules
    for section_key, section_data in world_rules.items():
        if section_key == "5_tono_y_narrativa":
            topic_name = "Tono y Narrativa del Mundo"
            lore_topic = db_session.query(LoreTopic).filter_by(name=topic_name).first()
            if not lore_topic:
                lore_topic = LoreTopic(name=topic_name, topic_type="narrative_guide")
                db_session.add(lore_topic)
            
            lore_topic.description = "Directrices narrativas y de tono para el mundo"
            lore_topic.additional_data_json = section_data
            flag_modified(lore_topic, "additional_data_json")
    
    print("  World lore populated/updated.")

def populate_spells(db_session: Session, data: dict):
    """Populate D&D 5e spells."""
    print("Populating Spells...")
    
    spells_list = data.get("spells", [])
    for spell_data in spells_list:
        spell_name = spell_data.get("name")
        if not spell_name:
            continue
            
        spell = db_session.query(Spell).filter_by(name=spell_name).first()
        if not spell:
            spell = Spell(name=spell_name)
            db_session.add(spell)
            print(f"  Spell '{spell_name}' created.")
        else:
            print(f"  Spell '{spell_name}' already exists. Updating...")
        
        # Update spell properties
        spell.spell_level = spell_data.get("spell_level", 0)
        spell.school = spell_data.get("school", "evocation")
        spell.casting_time = spell_data.get("casting_time", "1 action")
        spell.range_distance = spell_data.get("range", "touch")
        spell.duration = spell_data.get("duration", "instantaneous")
        spell.components = spell_data.get("components", "V, S")
        spell.description = spell_data.get("description", "")
        spell.damage_dice = spell_data.get("damage")
        spell.damage_type = spell_data.get("damage_type")
        spell.save_type = spell_data.get("save_type")
        spell.ritual = spell_data.get("ritual", False)
        spell.concentration = spell_data.get("concentration", False)
        spell.classes_json = spell_data.get("classes", [])
        spell.wuxia_equivalent = spell_data.get("wuxia_equivalent")
        spell.upcast_formula = spell_data.get("upcast_formula")
        
        if spell.classes_json:
            flag_modified(spell, "classes_json")
    
    print(f"  {len(spells_list)} spells populated/updated.")

def populate_attacks(db_session: Session, data: dict):
    """Populate attack actions."""
    print("Populating Attacks...")
    
    attacks_list = data.get("attacks", [])
    for attack_data in attacks_list:
        attack_name = attack_data.get("name")
        if not attack_name:
            continue
            
        attack = db_session.query(Attack).filter_by(name=attack_name).first()
        if not attack:
            attack = Attack(name=attack_name)
            db_session.add(attack)
            print(f"  Attack '{attack_name}' created.")
        else:
            print(f"  Attack '{attack_name}' already exists. Updating...")
        
        attack.attack_bonus = attack_data.get("attack_bonus", 0)
        attack.damage_dice = attack_data.get("damage_dice")
        attack.damage_type = attack_data.get("damage_type", "bludgeoning")
        attack.range_distance = attack_data.get("range_distance", "5 ft")
        attack.attack_type = attack_data.get("attack_type", "melee")
        attack.description = attack_data.get("description", "")
    
    print(f"  {len(attacks_list)} attacks populated/updated.")

def populate_techniques(db_session: Session, elemental_techniques_data: dict):
    """Populate Wuxia techniques."""
    print("Populating Techniques...")
    
    elemental_list = elemental_techniques_data.get("elemental_techniques", [])
    
    for elemental_group in elemental_list:
        element_name = elemental_group.get("elemento", "Unknown")
        dao_source = elemental_group.get("dao", "Unknown Dao Source")
        print(f"  Processing element: {element_name}")

        for tech_data in elemental_group.get("tecnicas", []):
            tech_name = tech_data.get("nombre")
            if not tech_name:
                continue
            
            tech = db_session.query(Technique).filter_by(name=tech_name, element_association=element_name).first()
            if not tech:
                tech = Technique(name=tech_name, element_association=element_name)
                db_session.add(tech)
                print(f"    Technique '{tech_name}' ({element_name}) created.")
            else:
                print(f"    Technique '{tech_name}' ({element_name}) already exists. Updating...")

            tech.name_chinese = tech_data.get("nombre_chino")
            tech.description = tech_data.get("efecto")
            tech.level_required = tech_data.get("nivel", 1)
            tech.rank = tech_data.get("rango")
            tech.damage_string = tech_data.get("daño")
            tech.version = tech_data.get("version")
            tech.source_dao = dao_source
            tech.mana_cost = tech_data.get("mana_cost")
            tech.casting_time = tech_data.get("casting_time", "1 action")
            tech.range_distance = tech_data.get("range_distance", "touch")
            tech.duration = tech_data.get("duracion", "instantaneous")
            tech.dnd_equivalent = tech_data.get("dnd_equivalent")
            
            # Store other properties
            other_props = {k: v for k, v in tech_data.items() if k not in 
                           ['nombre', 'nombre_chino', 'efecto', 'nivel', 'rango', 'daño', 
                            'version', 'mana_cost', 'casting_time', 'range_distance', 
                            'duracion', 'dnd_equivalent']}
            tech.other_properties_json = other_props if other_props else None
            if tech.other_properties_json:
                flag_modified(tech, "other_properties_json")
    
    print("  Techniques populated/updated.")

def populate_conditions(db_session: Session, data: dict):
    """Populate status conditions."""
    print("Populating Conditions...")
    
    conditions_list = data.get("condiciones", [])
    for condition_data in conditions_list:
        condition_name = condition_data.get("nombre")
        if not condition_name:
            continue
            
        condition = db_session.query(Condition).filter_by(name=condition_name).first()
        if not condition:
            condition = Condition(name=condition_name)
            db_session.add(condition)
            print(f"  Condition '{condition_name}' created.")
        else:
            print(f"  Condition '{condition_name}' already exists. Updating...")
        
        condition.description = condition_data.get("descripcion")
        condition.condition_type = condition_data.get("tipo")
        condition.effects_json = condition_data.get("efectos_mecanicos")
        
        if condition.effects_json:
            flag_modified(condition, "effects_json")
    
    print(f"  {len(conditions_list)} conditions populated/updated.")

def populate_sects(db_session: Session, data: dict):
    """Populate Wuxia sects."""
    print("Populating Sects...")
    
    sects_list = data.get("sectas", [])
    for sect_data in sects_list:
        sect_name = sect_data.get("nombre")
        if not sect_name:
            continue
            
        sect = db_session.query(Sect).filter_by(name=sect_name).first()
        if not sect:
            sect = Sect(name=sect_name)
            db_session.add(sect)
            print(f"  Sect '{sect_name}' created.")
        else:
            print(f"  Sect '{sect_name}' already exists. Updating...")
        
        sect.founder = sect_data.get("fundador")
        sect.alignment = sect_data.get("alineamiento")
        sect.specialties_json = sect_data.get("especialidad")
        sect.reputation = sect_data.get("reputacion")
        sect.requirements = sect_data.get("requisitos_ingreso")
        
        if sect.specialties_json:
            flag_modified(sect, "specialties_json")
    
    print(f"  {len(sects_list)} sects populated/updated.")

def populate_locations(db_session: Session, data: dict):
    """Populate game world locations."""
    print("Populating Locations...")
    
    locations_list = data.get("locations", [])
    for location_data in locations_list:
        location_name = location_data.get("name")
        if not location_name:
            continue
            
        location = db_session.query(Location).filter_by(name=location_name).first()
        if not location:
            location = Location(name=location_name)
            db_session.add(location)
            print(f"  Location '{location_name}' created.")
        else:
            print(f"  Location '{location_name}' already exists. Updating...")
        
        location.location_type = location_data.get("location_type")
        location.region = location_data.get("region")
        location.description = location_data.get("description")
        location.current_status = location_data.get("current_status", "active")
        location.loot_available = location_data.get("loot_available", False)
        location.enemies_present = location_data.get("enemies_present", False)
        location.environmental_effects_json = location_data.get("environmental_effects")
        location.notable_features_json = location_data.get("notable_features")
        location.connections_json = location_data.get("connections")
        
        # Flag JSON fields as modified
        for json_field in ["environmental_effects_json", "notable_features_json", "connections_json"]:
            if getattr(location, json_field):
                flag_modified(location, json_field)
    
    print(f"  {len(locations_list)} locations populated/updated.")

def populate_campaign_events(db_session: Session, data: dict):
    """Populate campaign events and timeline."""
    print("Populating Campaign Events...")
    
    session_data = data.get("session", {})
    events_list = session_data.get("resumenes", [])
    
    for event_data in events_list:
        event_title = event_data.get("titulo")
        if not event_title:
            continue
        
        event = db_session.query(CampaignEvent).filter_by(title=event_title).first()
        if not event:
            event = CampaignEvent(title=event_title)
            db_session.add(event)
            print(f"  Campaign Event '{event_title}' created.")
        else:
            print(f"  Campaign Event '{event_title}' already exists. Updating...")

        # Parse day range
        day_str = event_data.get("dias", "")
        day_start, day_end = None, None
        if "-" in day_str:
            parts = day_str.split("-")
            try:
                day_start, day_end = int(parts[0]), int(parts[1])
            except ValueError:
                pass
        elif day_str:
            try:
                day_start = day_end = int(day_str)
            except ValueError:
                pass
        
        event.day_range_start = day_start
        event.day_range_end = day_end
        event.summary_content = event_data.get("contenido")
        event.event_type = "narrative"
        event.importance_level = "medium"
        
        # Store additional details
        details = {k: v for k, v in event_data.items() 
                  if k not in ['titulo', 'dias', 'contenido']}
        event.full_details_json = details if details else None
        if event.full_details_json:
            flag_modified(event, "full_details_json")
        
        event.event_tags_json = event_data.get("temas")
        if event.event_tags_json:
            flag_modified(event, "event_tags_json")
    
    print(f"  {len(events_list)} campaign events populated/updated.")

def populate_character_liang_wuzhao(db_session: Session, char_json_data: dict, techniques_data: dict):
    """Populate the main character Liáng Wǔzhào with full normalization."""
    print("Populating/Updating character Liáng Wǔzhào with normalized schema...")
    
    char_name = char_json_data["name"]
    char = db_session.query(Character).filter_by(name=char_name).first()

    if not char:
        char = Character(name=char_name)
        db_session.add(char)
        print(f"  Character '{char_name}' created.")
    else:
        print(f"  Character '{char_name}' already exists. Updating...")
        # Clear existing relationships for clean update
        char.saving_throw_proficiencies.clear()
        char.skill_proficiencies.clear()
        char.languages.clear()
        char.features_traits.clear()
        char.resources.clear()
        char.titles.clear()
        char.compatible_elements.clear()
        if char.reclusion_state:
            db_session.delete(char.reclusion_state)
        db_session.flush()

    # Direct field mapping
    direct_fields = [
        "level", "character_class", "race", "alignment", "background", "experience_points",
        "strength_score", "dexterity_score", "constitution_score", "intelligence_score",
        "wisdom_score", "charisma_score", "proficiency_bonus", "hp_max", "hp_current",
        "armor_class", "speed", "mana_max", "mana_current", "status_general",
        "dao_philosophy", "affiliation"
    ]
    
    for field in direct_fields:
        if field in char_json_data:
            setattr(char, field, char_json_data[field])
    
    # Calculate derived stats
    char.initiative_bonus = (char.dexterity_score - 10) // 2
    char.spell_save_dc = 8 + char.proficiency_bonus + ((char.intelligence_score - 10) // 2)
    
    # Store remaining custom properties
    char.custom_props_json = char_json_data.get("remaining_custom_props")
    if char.custom_props_json:
        flag_modified(char, "custom_props_json")

    # Populate relationships
    # Saving throws
    for attr, proficient in char_json_data.get("saving_throws_proficiencies", {}).items():
        char.saving_throw_proficiencies.append(
            CharacterSavingThrowProficiency(attribute_name=attr, is_proficient=proficient)
        )
    
    # Skills
    for skill, proficient in char_json_data.get("skill_proficiencies", {}).items():
        char.skill_proficiencies.append(
            CharacterSkillProficiency(skill_name=skill, is_proficient=proficient)
        )
    
    # Languages
    for lang_name in char_json_data.get("languages_known", []):
        char.languages.append(CharacterLanguage(language_name=lang_name))
    
    # Features and traits
    for ft_data in char_json_data.get("features_traits_list", []):
        char.features_traits.append(CharacterFeatureTrait(
            name=ft_data["name"],
            description=ft_data["description"],
            feature_type=ft_data.get("type"),
            uses_per_rest=ft_data.get("uses_per_rest"),
            rest_type=ft_data.get("rest_type", "long")
        ))
    
    # Resources
    resources_data = char_json_data.get("resources_data", {})
    for resource_name, resource_info in resources_data.items():
        char.resources.append(CharacterResource(
            resource_name=resource_name,
            current_value=resource_info["current"],
            max_value=resource_info["max"]
        ))
    
    # Reclusion state
    reclusion_data = char_json_data.get("reclusion_data")
    if reclusion_data:
        char.reclusion_state = CharacterReclusionState(
            start_day=reclusion_data.get("start_day"),
            end_day=reclusion_data.get("end_day"),
            days_remaining=reclusion_data.get("days_remaining"),
            reclusion_type=reclusion_data.get("reclusion_type", "meditation")
        )
    
    # Titles
    titles_data = char_json_data.get("titles_data", {})
    for title_name in titles_data.get("active", []):
        char.titles.append(CharacterTitle(title_name=title_name, is_active=True))
    for title_name in titles_data.get("retired", []):
        char.titles.append(CharacterTitle(title_name=title_name, is_active=False))

    # Compatible elements
    for element_desc in char_json_data.get("compatible_elements_data", []):
        char.compatible_elements.append(
            CharacterCompatibleElement(element_description=element_desc)
        )

    # Associate known techniques
    print(f"  Associating known techniques for '{char.name}'...")
    elemental_list = techniques_data.get("elemental_techniques", [])
    
    for elemental_group in elemental_list:
        if elemental_group.get("elemento") == "Fuego":
            # Learn first 3 fire techniques
            techs_to_learn = elemental_group.get("tecnicas", [])[:3]
            
            for tech_data in techs_to_learn:
                tech_name = tech_data.get("nombre")
                if not tech_name:
                    continue
                    
                technique_obj = db_session.query(Technique).filter_by(
                    name=tech_name, element_association="Fuego"
                ).first()
                
                if technique_obj:
                    # Check if already known
                    existing = db_session.query(CharacterKnownTechniques).filter_by(
                        character=char, technique=technique_obj
                    ).first()
                    
                    if not existing:
                        new_known_tech = CharacterKnownTechniques(
                            character=char,
                            technique=technique_obj,
                            mastery_level="learned"
                        )
                        char.known_techniques.append(new_known_tech)
                        print(f"    Technique '{tech_name}' associated with {char.name}.")
                else:
                    print(f"    Warning: Technique '{tech_name}' not found for association.")
    
    print(f"  Character '{char_name}' populated/updated with normalized schema.")

def create_sample_party(db_session: Session):
    """Create a sample party for the campaign."""
    print("Creating sample party...")
    
    party_name = "Los Buscadores del Dao Perdido"
    party = db_session.query(Party).filter_by(name=party_name).first()
    
    if not party:
        party = Party(
            name=party_name,
            is_active=True,
            shared_gold=125,
            current_location="Cruce de los Mil Vientos"
        )
        
        party.shared_resources_json = {
            "group_items": ["Mapa del Reino", "Carta de Recomendación"]
        }
        party.reputation_json = {
            "Secta de la Llama Partida": 75,
            "Monasterio de los Ecos Helados": -10,
            "Comerciantes Locales": 25
        }
        party.goals_json = [
            "Recuperar el Micronúcleo robado",
            "Encontrar al mentor traidor",
            "Restaurar el honor del Monasterio"
        ]
        
        db_session.add(party)
        
        # Add Liáng Wǔzhào to the party
        liang = db_session.query(Character).filter_by(name="Liáng Wǔzhào").first()
        if liang:
            party.members.append(liang)
        
        # Flag JSON fields as modified
        flag_modified(party, "shared_resources_json")
        flag_modified(party, "reputation_json")
        flag_modified(party, "goals_json")
        
        print(f"  Party '{party_name}' created with Liáng Wǔzhào as member.")
    else:
        print(f"  Party '{party_name}' already exists.")

def create_sample_session(db_session: Session):
    """Create a sample game session."""
    print("Creating sample session...")
    
    session = db_session.query(Session).filter_by(session_number=1).first()
    
    if not session:
        party = db_session.query(Party).filter_by(name="Los Buscadores del Dao Perdido").first()
        
        session = Session(
            session_number=1,
            title="El Inicio del Camino",
            duration_minutes=240,
            session_summary="Liáng Wǔzhào escapa del Monasterio destruido y comienza su búsqueda del Micronúcleo robado.",
            experience_awarded=450,
            status="completed",
            party=party
        )
        
        session.events_json = [
            "Destrucción del Monasterio Silencioso",
            "Primer encuentro con bandidos",
            "Descubrimiento de pistas sobre el mentor"
        ]
        
        session.treasure_found_json = {
            "gold": 25,
            "items": ["Poción de Curación Menor"]
        }
        
        db_session.add(session)
        flag_modified(session, "events_json")
        flag_modified(session, "treasure_found_json")
        
        print("  Sample session created.")
    else:
        print("  Sample session already exists.")

def initialize_world_state(db_session: Session):
    """Initialize the world state."""
    print("Initializing world state...")
    
    world_state = db_session.query(WorldState).first()
    
    if not world_state:
        world_state = WorldState(
            current_event="El mundo está en calma después de la destrucción del Monasterio Silencioso",
            current_day=1,
            weather="clear",
            time_of_day="morning",
            season="spring"
        )
        
        world_state.active_effects_json = [
            "energía_residual_monasterio",
            "búsqueda_activa_micronúcleo"
        ]
        
        db_session.add(world_state)
        flag_modified(world_state, "active_effects_json")
        
        print("  World state initialized.")
    else:
        print("  World state already exists.")

def populate():
    """Main population function."""
    print(f"Initializing database (complete normalized schema) at: {DATABASE_URL}")
    init_db(DATABASE_URL)
    
    db_session = get_session()
    if db_session is None:
        print("Error: Could not obtain database session.")
        return

    print("\nPopulating database with complete normalized data...")
    
    try:
        # Core data population
        populate_dm_guidelines(db_session, DM_RULES_DATA)
        populate_world_lore(db_session, WORLD_RULES_DATA)
        
        # Spells and techniques
        if 'SPELLS_DATA' in globals():
            populate_spells(db_session, SPELLS_DATA)
        if 'ATTACKS_DATA' in globals():
            populate_attacks(db_session, ATTACKS_DATA)
        populate_techniques(db_session, FIRE_TECHNIQUES_DATA)
        
        # World building
        if 'CONDITIONS_DATA' in globals():
            populate_conditions(db_session, CONDITIONS_DATA)
        if 'SECTS_DATA' in globals():
            populate_sects(db_session, SECTS_DATA)
        populate_locations(db_session, SAMPLE_LOCATIONS)
        
        # Campaign and characters
        populate_campaign_events(db_session, NARRATIVE_EVENTS_DATA)
        populate_character_liang_wuzhao(db_session, LIANG_WUZHAO_FULL_JSON, FIRE_TECHNIQUES_DATA)
        
        # Party and session management
        create_sample_party(db_session)
        create_sample_session(db_session)
        
        # World state
        initialize_world_state(db_session)

        db_session.commit()
        print("\nAll normalized data committed successfully.")
        
    except Exception as e:
        db_session.rollback()
        print(f"\nError populating normalized data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_session.close()
        print("Database session closed.")

if __name__ == "__main__":
    populate()