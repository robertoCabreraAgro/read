# populate_db.py
import json
import os
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from database.engine import init_db, get_session
from database.models import (
    Base, 
    DmGuidelineSet, DmSessionStructureItem, DmIntroCharShowField,
    LoreTopic, CultivationRealm,
    Character, CharacterSavingThrowProficiency, CharacterSkillProficiency, CharacterLanguage,
    CharacterFeatureTrait, CharacterResource, CharacterInventoryItem, CharacterReclusionState,
    CharacterTitle, CharacterCompatibleElement,
    Technique, CharacterKnownTechniques, 
    CampaignEvent,
    RuleSet, WorldState # Mantener RuleSet y WorldState por si se usan genéricamente
)
from config import DATABASE_URL

# --- JSON Data Structures ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def _load_json(name: str) -> dict | list:
    path = os.path.join(DATA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

DM_RULES_DATA = _load_json("dm_rules.json")
WORLD_RULES_DATA = _load_json("world_rules.json")
FIRE_TECHNIQUES_DATA = _load_json("fire_techniques.json")
NARRATIVE_EVENTS_DATA = _load_json("narrative_events.json")
LIANG_WUZHAO_FULL_JSON = _load_json("liang_wuzhao.json")
# --- Funciones de Población ---

def populate_dm_guidelines(db_session: Session, data: dict):
    print("Poblando Directrices del DM...")
    guideline_name = data.get("nombre_guidelines", "Directrices DM por Defecto")
    
    guideline_set = db_session.query(DmGuidelineSet).filter_by(name=guideline_name).first()
    if not guideline_set:
        guideline_set = DmGuidelineSet(name=guideline_name)
        db_session.add(guideline_set)
        print(f"  DmGuidelineSet '{guideline_name}' creado.")
    else:
        print(f"  DmGuidelineSet '{guideline_name}' ya existe. Actualizando...")

    guideline_set.system_base = data.get("system_base")
    guideline_set.setting_description = data.get("setting_description")
    guideline_set.mode_directed = data.get("mode_directed")
    guideline_set.dice_roll_responsible = data.get("dice_roll_responsible")
    guideline_set.dice_roll_rules = data.get("dice_roll_rules")
    guideline_set.tone_difficulty = data.get("tone_difficulty")
    guideline_set.tone_focus = data.get("tone_focus")
    guideline_set.tone_style = data.get("tone_style")
    guideline_set.relevant_chars_narration = data.get("relevant_chars_narration")
    guideline_set.intro_chars_restriction = data.get("intro_chars_restriction")

    # Session Structure Items
    guideline_set.session_structure_items.clear() # Limpiar para actualizar
    for item_desc in data.get("session_structure", []):
        guideline_set.session_structure_items.append(DmSessionStructureItem(item_description=item_desc))
    
    # Intro Char Show Fields
    guideline_set.intro_chars_show_fields.clear() # Limpiar para actualizar
    for field_n in data.get("intro_chars_show_fields", []):
        guideline_set.intro_chars_show_fields.append(DmIntroCharShowField(field_name=field_n))
    
    print(f"  DmGuidelineSet '{guideline_name}' poblado/actualizado.")

def populate_world_lore(db_session: Session, data: dict):
    print("Poblando Lore del Mundo...")
    for section in data.get("secciones", []):
        topic_name = section.get("titulo")
        topic_type = section.get("tipo", "lore_general")
        if not topic_name:
            continue

        lore_topic = db_session.query(LoreTopic).filter_by(name=topic_name).first()
        if not lore_topic:
            lore_topic = LoreTopic(name=topic_name)
            db_session.add(lore_topic)
            print(f"  LoreTopic '{topic_name}' creado.")
        else:
            print(f"  LoreTopic '{topic_name}' ya existe. Actualizando...")

        if topic_type == "cultivation_realms":
            lore_topic.description = section.get("nota")
            # Limpiar reinos existentes para este LoreTopic antes de añadir nuevos
            lore_topic.cultivation_realms.clear() 
            db_session.flush() # Aplicar el clear
            for realm_data in section.get("estructura", []):
                new_realm = CultivationRealm(
                    name=realm_data.get("nombre_reino"),
                    realm_order=realm_data.get("orden"),
                    level_range=realm_data.get("rango_nivel_pj"),
                    theme=realm_data.get("tema")
                )
                lore_topic.cultivation_realms.append(new_realm) # Asocia al LoreTopic
            if lore_topic.description: flag_modified(lore_topic, "description")

        elif topic_type == "lore_general":
            content = section.get("contenido")
            if isinstance(content, (dict, list)):
                # Si el contenido es complejo y queremos guardarlo tal cual en additional_data_json
                lore_topic.description = content.get("descripcion") if isinstance(content, dict) else None
                lore_topic.additional_data_json = content
                if lore_topic.description: flag_modified(lore_topic, "description")
                if lore_topic.additional_data_json: flag_modified(lore_topic, "additional_data_json")
            else:
                lore_topic.description = str(content)
                if lore_topic.description: flag_modified(lore_topic, "description")
        
        print(f"  LoreTopic '{topic_name}' poblado/actualizado.")


def populate_techniques(db_session: Session, elemental_techniques_list: list):
    print("Poblando Técnicas...")
    if not isinstance(elemental_techniques_list, list):
        print("  Error: Se esperaba una lista de datos de técnicas elementales.")
        return

    for elemental_group in elemental_techniques_list:
        element_name = elemental_group.get("elemento", "Desconocido")
        dao_source = elemental_group.get("dao", "Fuente Dao Desconocida")
        print(f"  Procesando elemento: {element_name}")

        for tech_data in elemental_group.get("tecnicas", []):
            tech_name = tech_data.get("nombre")
            if not tech_name: continue
            
            tech = db_session.query(Technique).filter_by(name=tech_name, element_association=element_name).first()
            if not tech:
                tech = Technique(name=tech_name, element_association=element_name)
                db_session.add(tech)
                print(f"    Técnica '{tech_name}' ({element_name}) creada.")
            else:
                print(f"    Técnica '{tech_name}' ({element_name}) ya existe. Actualizando...")

            tech.name_chinese = tech_data.get("nombre_chino")
            tech.description = tech_data.get("efecto")
            tech.level_required = tech_data.get("nivel")
            tech.rank = tech_data.get("rango")
            tech.damage_string = tech_data.get("daño")
            tech.version = tech_data.get("version")
            tech.source_dao = dao_source
            tech.mana_cost = tech_data.get("mana_cost_inicial") or tech_data.get("mana_cost")
            
            other_props = {k: v for k, v in tech_data.items() if k not in 
                           ['nombre', 'nombre_chino', 'efecto', 'nivel', 'rango', 'daño', 
                            'version', 'mana_cost_inicial', 'mana_cost']}
            tech.other_properties_json = other_props if other_props else None
            if tech.other_properties_json: flag_modified(tech, "other_properties_json")
    print("  Técnicas pobladas/actualizadas.")


def populate_campaign_events(db_session: Session, data: dict):
    print("Poblando Eventos de Campaña...")
    for event_data in data.get("resumenes", []):
        event_title = event_data.get("titulo")
        if not event_title: continue
        
        event = db_session.query(CampaignEvent).filter_by(title=event_title).first()
        if not event:
            event = CampaignEvent(title=event_title)
            db_session.add(event)
            print(f"  Evento de Campaña '{event_title}' creado.")
        else:
            print(f"  Evento de Campaña '{event_title}' ya existe. Actualizando...")

        day_str = event_data.get("dias", "")
        day_start, day_end = None, None
        if "-" in day_str:
            parts = day_str.split("-")
            try: day_start, day_end = int(parts[0]), int(parts[1])
            except ValueError: pass
        elif day_str:
            try: day_start = day_end = int(day_str)
            except ValueError: pass
        
        event.day_range_start = day_start
        event.day_range_end = day_end
        event.summary_content = event_data.get("contenido")
        
        details = {k: v for k, v in event_data.items() if k not in ['titulo', 'dias', 'contenido', 'temas']}
        event.full_details_json = details if details else None
        if event.full_details_json: flag_modified(event, "full_details_json")
        
        event.event_tags_json = event_data.get("temas") if event_data.get("temas") else None
        if event.event_tags_json: flag_modified(event, "event_tags_json")
    print("  Eventos de Campaña poblados/actualizados.")


def populate_character_liang_wuzhao(db_session: Session, char_json_data: dict, techniques_to_associate_data: list):
    print("Poblando/Actualizando personaje Liáng Wǔzhào con esquema normalizado...")
    char_name = char_json_data["name"]
    char = db_session.query(Character).filter_by(name=char_name).first()

    if not char:
        char = Character(name=char_name)
        db_session.add(char)
        print(f"  Personaje '{char_name}' creado.")
    else:
        print(f"  Personaje '{char_name}' ya existe. Actualizando...")
        # Limpiar relaciones para actualizacion completa desde JSON
        char.saving_throw_proficiencies.clear()
        char.skill_proficiencies.clear()
        char.languages.clear()
        char.features_traits.clear()
        char.resources.clear()
        char.titles.clear()
        char.compatible_elements.clear()
        # char.known_techniques.clear() # Se maneja específicamente abajo para no perder mastery_level si no se actualiza
        if char.reclusion_state: db_session.delete(char.reclusion_state) # Para one-to-one
        db_session.flush()

    # Campos directos
    direct_fields = ["level", "character_class", "race", "alignment", "background", "experience_points",
                     "strength_score", "dexterity_score", "constitution_score", "intelligence_score",
                     "wisdom_score", "charisma_score", "proficiency_bonus", "hp_max", "hp_current",
                     "armor_class", "speed", "mana_max", "mana_current", "status_general",
                     "dao_philosophy", "affiliation"]
    for field in direct_fields:
        if field in char_json_data:
            setattr(char, field, char_json_data[field])
    
    char.custom_props_json = char_json_data.get("remaining_custom_props")
    if char.custom_props_json: flag_modified(char, "custom_props_json")

    # Relaciones
    for attr, proficient in char_json_data.get("saving_throws_proficiencies", {}).items():
        char.saving_throw_proficiencies.append(CharacterSavingThrowProficiency(attribute_name=attr, is_proficient=proficient))
    for skill, proficient in char_json_data.get("skill_proficiencies", {}).items():
        char.skill_proficiencies.append(CharacterSkillProficiency(skill_name=skill, is_proficient=proficient))
    for lang_name in char_json_data.get("languages_known", []):
        char.languages.append(CharacterLanguage(language_name=lang_name))
    for ft_data in char_json_data.get("features_traits_list", []):
        char.features_traits.append(CharacterFeatureTrait(name=ft_data["name"], description=ft_data["description"], type=ft_data.get("type")))
    
    if "micronucleo" in char_json_data.get("resources_data", {}):
        res_data = char_json_data["resources_data"]["micronucleo"]
        char.resources.append(CharacterResource(resource_name="micronucleo", current_value=res_data["current"], max_value=res_data["max"]))

    # Nuevas relaciones normalizadas
    reclusion_data = char_json_data.get("reclusion_data")
    if reclusion_data:
        char.reclusion_state = CharacterReclusionState(
            start_day=reclusion_data.get("start_day"),
            end_day=reclusion_data.get("end_day"),
            days_remaining=reclusion_data.get("days_remaining")
        )
    
    titles_data = char_json_data.get("titles_data", {})
    for title_name in titles_data.get("active", []):
        char.titles.append(CharacterTitle(title_name=title_name, is_active=True))
    for title_name in titles_data.get("retired", []):
        char.titles.append(CharacterTitle(title_name=title_name, is_active=False))

    for element_desc in char_json_data.get("compatible_elements_data", []):
        char.compatible_elements.append(CharacterCompatibleElement(element_description=element_desc))

    # Asociación de Técnicas Conocidas
    print(f"  Asociando/Actualizando técnicas conocidas para '{char.name}'...")
    tech_names_to_learn = []
    if techniques_to_associate_data and isinstance(techniques_to_associate_data, list) and len(techniques_to_associate_data) > 0:
        fire_dao_obj = techniques_to_associate_data[0]
        if fire_dao_obj.get("elemento") == "Fuego":
             tech_names_to_learn = [tech.get("nombre") for i, tech in enumerate(fire_dao_obj.get("tecnicas", [])) if i < 3] # Aprende las primeras 3

    # Actualizar o añadir técnicas conocidas
    existing_known_tech_map = {kt.technique.name: kt for kt in char.known_techniques if kt.technique} # Asume que technique está cargada o se puede cargar

    for tech_name in tech_names_to_learn:
        if not tech_name: continue
        technique_obj = db_session.query(Technique).filter_by(name=tech_name, element_association="Fuego").first()
        if technique_obj:
            if tech_name not in existing_known_tech_map: # Técnica no conocida previamente
                new_known_tech = CharacterKnownTechniques(character=char, technique=technique_obj, mastery_level="Aprendida")
                # db_session.add(new_known_tech) # No es necesario si se usa append a la relación con cascade
                char.known_techniques.append(new_known_tech)
                print(f"    Técnica '{tech_name}' (Fuego) asociada a {char.name}.")
            else: # Técnica ya conocida, se podría actualizar mastery_level aquí si se quisiera
                print(f"    {char.name} ya conoce '{tech_name}'. Verificando/actualizando maestría (no implementado).")
        else:
            print(f"    Advertencia: Técnica '{tech_name}' (Fuego) no encontrada para asociar.")
    
    print(f"  Personaje '{char_name}' poblado/actualizado con esquema normalizado.")


def populate():
    print(f"Inicializando base de datos (esquema normalizado) en: {DATABASE_URL}")
    init_db(DATABASE_URL) 
    
    db_session = get_session()
    if db_session is None:
        print("Error: No se pudo obtener la sesión de la base de datos.")
        return

    print("\nPoblando la base de datos con datos normalizados...")
    try:
        populate_dm_guidelines(db_session, DM_RULES_DATA)
        populate_world_lore(db_session, WORLD_RULES_DATA)
        populate_techniques(db_session, FIRE_TECHNIQUES_DATA)
        populate_campaign_events(db_session, NARRATIVE_EVENTS_DATA)
        
        populate_character_liang_wuzhao(db_session, LIANG_WUZHAO_FULL_JSON, FIRE_TECHNIQUES_DATA)

        db_session.commit()
        print("\nCommit de todos los datos normalizados realizado exitosamente.")
    except Exception as e:
        db_session.rollback()
        print(f"\nError al insertar datos normalizados: {e}")
        import traceback
        traceback.print_exc() 
    finally:
        db_session.close()
        print("Sesión de base de datos cerrada.")

if __name__ == "__main__":
    populate()

