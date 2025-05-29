# populate_db.py
import json
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

DM_RULES_DATA = {
    "nombre_guidelines": "Directrices DM Completas - Mundo Wuxia Liáng Wǔzhào",
    "system_base": "Sistema propio con adaptaciones de D&D 5e y elementos de PbtA para narrativa.",
    "setting_description": "Mundo de fantasía Wuxia con énfasis en el cultivo de Chi, artes marciales místicas y filosofías ancestrales. La tecnología es limitada, similar a la China dinástica, pero con artefactos de poder.",
    "mode_directed": "Dirigido por el DM, con alta agencia de los jugadores para influir en la narrativa y el mundo. Se busca un equilibrio entre sandbox y arcos argumentales definidos.",
    "dice_roll_responsible": "DM y Jugadores. DM para NPCs y eventos mundiales; Jugadores para sus acciones. Regla de 'fallar hacia adelante' preferida.",
    "dice_roll_rules": "Pruebas de habilidad: D20 + Modificador vs CD. Combate: D20 + Mod Ataque vs AC. Daño: Según técnica/arma. Salvaciones: D20 + Mod vs CD Técnica/Efecto.",
    "tone_difficulty": "Épico y Desafiante. Los jugadores son héroes (o anti-héroes) capaces, pero los peligros son reales y las decisiones tienen peso. La dificultad escala con la progresión.",
    "tone_focus": "Aventura, Misterio, Desarrollo Personal, Intriga Política. Énfasis en la evolución del personaje y su impacto en el mundo.",
    "tone_style": "Cinematográfico y Descriptivo. Se buscan momentos memorables y una atmósfera inmersiva. Humor es bienvenido si encaja.",
    "relevant_chars_narration": "Todos los PJs son protagonistas. NPCs importantes tendrán arcos propios. El mundo reacciona a las acciones de los PJs.",
    "intro_chars_restriction": "Los PJs deben tener una razón para estar en la región inicial y una motivación (aunque sea vaga) para la aventura. Se prefiere que tengan lazos (positivos o negativos) con al menos otro PJ.",
    "session_structure": [
        "Resumen de sesión anterior (DM o Jugador voluntario).",
        "Foco en objetivos actuales de los PJs.",
        "Introducción de nuevos elementos/conflictos.",
        "Clímax o punto de inflexión.",
        "Espacio para roleo y desarrollo de personajes.",
        "Conclusión y preparación para la siguiente sesión (puede incluir 'cliffhanger')."
    ],
    "intro_chars_show_fields": [
        "Nombre y Título (si aplica)",
        "Concepto Breve (ej. 'Monje exiliado en busca de la verdad tras la destrucción de su templo')",
        "Apariencia General y Primera Impresión",
        "Motivación Principal Aparente"
    ]
}

WORLD_RULES_DATA = {
    "nombre_mundo": "Mundo de Aethelgard - Era del Despertar Fragmentado",
    "descripcion_general": "Un mundo donde la energía primordial (Chi o Maná) fluye de manera inestable tras un cataclismo conocido como 'La Disrupción'. Las civilizaciones intentan reconstruirse y dominar nuevas formas de poder, mientras antiguas verdades y peligros resurgen.",
    "secciones": [
        {
            "titulo": "Flujo de Energía Primordial (Chi/Maná)",
            "tipo": "lore_general", # Tipo para diferenciar el manejo
            "contenido": {
                "descripcion": "El Chi (o Maná) es la energía vital. Su flujo es inestable, con nodos y vacíos.",
                "reglas_basicas": [
                    "Nodos de Poder: Potencian técnicas, pueden ser peligrosos.",
                    "Zonas de Vacío: Debilitan técnicas, causan fatiga.",
                    "Resonancia Elemental: Áreas alineadas con elementos afectan técnicas.",
                    "Meditación y Cultivo: Prácticas para refinar y manipular Chi."
                ]
            }
        },
        {
            "titulo": "Cultivo y Reinos de Poder", # Esta sección define los reinos
            "tipo": "cultivation_realms",
            "nota": "Los Reinos de Cultivo representan niveles de entendimiento y control sobre el Chi. Cada reino desbloquea nuevas capacidades y percepciones. La progresión no es solo poder bruto, sino también comprensión filosófica y armonía con el Dao personal.",
            "estructura": [
                {"orden": 1, "nombre_reino": "Fundación del Núcleo", "rango_nivel_pj": "1-3", "tema": "Despertar del Chi, fortalecimiento básico del cuerpo y la mente, primeras técnicas."},
                {"orden": 2, "nombre_reino": "Establecimiento del Flujo", "rango_nivel_pj": "4-6", "tema": "Control consciente del flujo interno de Chi, técnicas elementales básicas, mayor resistencia y capacidad sensorial."},
                {"orden": 3, "nombre_reino": "Resonancia Elemental", "rango_nivel_pj": "7-9", "tema": "Afinidad profunda con uno o más elementos, manifestación de poder elemental avanzado, comprensión de patrones energéticos."},
                {"orden": 4, "nombre_reino": "Geometría del Dao", "rango_nivel_pj": "10-12", "tema": "Percepción y manipulación de las estructuras fundamentales del Chi y la realidad, técnicas complejas que alteran el entorno, inicio de la trascendencia."},
                {"orden": 5, "nombre_reino": "Unidad con el Vacío (Teórico)", "rango_nivel_pj": "13+", "tema": "Comprensión de la interconexión de todo, manipulación del Chi a nivel conceptual, habilidades legendarias o semi-divinas. Pocos han alcanzado este estado."}
            ]
        },
        {
            "titulo": "Leyes Físicas y Naturales",
            "tipo": "lore_general",
            "contenido": {
                "descripcion": "Física similar a la Tierra, pero alterable por Chi.",
                "puntos_clave": [
                    "Gravedad: Estándar, técnicas de levitación existen.",
                    "Ciclos Naturales: Normales, pueden afectar el Chi.",
                    "Materiales Exóticos: Infundidos con Chi, propiedades únicas."
                ]
            }
        }
        # ... (otras secciones de WORLD_RULES_DATA como Cosmología, Sociedad, etc.)
    ]
}

FIRE_TECHNIQUES_DATA = [ 
    {
        "elemento": "Fuego",
        "dao": "Presión Térmica y Geometría de Flujo – Enfoque en la adaptabilidad estructural y la eficiencia termodinámica del Chi de Fuego.",
        "tecnicas": [
            {"nombre": "Disparo de Fuego Primario", "nombre_chino": "初级火焰发射", "rango": "Básica", "version": "V0", "nivel": 0, "efecto": "Proyecta una pequeña esfera de fuego.", "daño": "1d4 Fuego"},
            {"nombre": "Escudo de Flujo Térmico", "nombre_chino": "热流护盾", "rango": "Básica", "version": "V1", "nivel": 1, "efecto": "Crea barrera de aire caliente.", "defensa": "+1 AC vs proyectiles"},
            {"nombre": "Hoja de Fuego Adaptativa", "nombre_chino": "适应火刃", "rango": "Intermedia", "version": "V1.5", "nivel": 2, "efecto": "Manifiesta hoja de fuego variable.", "daño": "2d6 Fuego + Mod. INT", "mana_cost_inicial": 15},
            {"nombre": "Geometría de Combustión Interna", "nombre_chino": "内燃几何", "rango": "Intermedia", "version": "V2", "nivel": 3, "efecto": "Infunde objeto/área con fuego inestable.", "daño_detonacion": "3d8 Fuego"},
            {"nombre": "Vórtice de Presión Cinética-Térmica", "nombre_chino": "动热压力涡旋", "rango": "Avanzada", "version": "V1", "nivel": 4, "efecto": "Genera torbellino de fuego.", "daño_continuo": "2d10 Fuego"},
            {"nombre": "Singularidad de Fuego Estructural (Prototipo)", "nombre_chino": "结构火焰奇点", "rango": "Maestra", "version": "V3 - Prototipo Delta", "nivel": 5, "efecto": "Requiere Micronúcleo. Explosión o buff.", "daño_explosion": "10d10 Fuego", "costo_micronucleo": "50 unidades"}
        ]
    }
]

NARRATIVE_EVENTS_DATA = {
    "nombre_campaña": "El Despertar del Dao Geométrico",
    "resumenes": [
        {"titulo": "La Disrupción del Monasterio Silencioso", "dias": "0-5", "contenido": "Destrucción del Monasterio, Liáng Wǔzhào escapa con el Micronúcleo.", "personajes_clave": ["Liáng Wǔzhào", "Mentor"], "impacto_inicial": ["Pérdida de base", "Motivación"]},
        {"titulo": "El Encuentro en el Cruce de los Mil Vientos", "dias": "10-20", "contenido": "Liáng Wǔzhào conoce a otros PJs/NPCs. Posible misión colaborativa.", "temas": ["Formación de grupo", "Intercambio de información"]},
        {"titulo": "La Prueba de la Pagoda Escondida", "dias": "30-50", "contenido": "Búsqueda de lugar de antiguo poder. Pruebas y revelaciones.", "desafios": ["Guardianes", "Acertijos"], "recompensa_potencial": ["Nuevas técnicas", "Mejora Micronúcleo"]},
    ]
}

LIANG_WUZHAO_FULL_JSON = {
    "name": "Liáng Wǔzhào", "level": 5, "character_class": "Monk (Custom Subclass: Dao Geométrico)", "race": "Human",
    "alignment": "Lawful Neutral", "background": "Hermit", "experience_points": 29600,
    "strength_score": 10, "dexterity_score": 16, "constitution_score": 12, "intelligence_score": 20, "wisdom_score": 16, "charisma_score": 10,
    "proficiency_bonus": 3, "hp_max": 40, "hp_current": 40, "armor_class": 14, "speed": 30,
    "mana_max": 4730, "mana_current": 4730,
    "status_general": "En Reclusión Estructural Completa", # Mapea a status_general
    "dao_philosophy": "Razonado", # Nuevo campo directo
    "affiliation": "Secta de la Llama Partida (Cuatro Estandartes)", # Nuevo campo directo
    "saving_throws_proficiencies": {"strength": False, "dexterity": True, "constitution": False, "intelligence": True, "wisdom": True, "charisma": False},
    "skill_proficiencies": {"arcana": True, "insight": True, "perception": True, "acrobatics": True, "history": True},
    "languages_known": ["Common", "Celestial", "Primordial"],
    "features_traits_list": [
      {"name": "Micronúcleo Feature", "description": "Contenedor comprimido de chi...", "type": "Class Feature"},
      {"name": "Silencio del Diseño Absoluto", "description": "Durante una meditación...", "type": "Special Trait"},
      {"name": "Sistema Elemental Adaptativo – Matriz Bernoulli Multi-Módulo", "description": "Permite seleccionar una afinidad elemental...", "type": "Class Feature"},
    ],
    "resources_data": {"micronucleo": {"current": 132, "max": 132}}, # Mana ya está en campos directos
    # Datos para campos normalizados (antes en custom_properties_dict)
    "reclusion_data": {"start_day": 115, "end_day": 470, "days_remaining": 355},
    "titles_data": {"active": ["Portador del Silencio del Diseño Absoluto"], "retired": ["El que Rediseñó su Reflejo", "El que Cortó la Escritura", "Variable Estable"]},
    "compatible_elements_data": ["Fuego – Presión térmica", "Físico – Biomecánica", "Aire – Evasión", "Agua – Recuperación", "Luz – Precisión", "Vacío – Reacción anti-signatura"],
    # custom_props_json remanente (si algo no se normalizó)
    "remaining_custom_props": {"notas_generales": "Personaje complejo con enfoque en la manipulación del Chi mediante la comprensión de su estructura fundamental."}
}

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

```
