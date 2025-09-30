# region


def get_entities():
    """
    Lit le fichier 'entities.txt' et extrait les entités ainsi que leurs attributs.

    Le fichier doit être structuré de la façon suivante :
    Chaque entité est définie par une ligne sans indentation ni tiret, suivie de ses attributs précédés de '- '.
    Exemple :
        User .w Admin
        - name
        - email
        Product
        - title
        - price

    Returns:
        dict: Un dictionnaire où les clés sont les noms des entités (str) et les valeurs sont des listes d'attributs (list[str]).
    """
    entities = {}
    entity_name = ""

    with open("config/entities.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    for line in lines:
        if not line.startswith(" ") and not line.startswith("- "):
            entity_name = line.split(" ")[0].strip()
            if entity_name != "":
                entities[entity_name] = []

        elif line.startswith("- "):
            entities[entity_name].append(line.strip()[2:])

    return entities


# endregion


def get_acces_for_entities(entity: str) -> tuple[list[str], list[str], list[str]]:
    """
    Extrait les rôles d'accès en lecture, écriture et suppression pour une entité donnée.

    Args:
        entity (str): Le nom de l'entité.
    Returns:
        tuple: Un tuple contenant les rôles d'accès en lecture, écriture et suppression (str).
    """
    read_role = []
    write_role = []
    delete_role = []
    with open("config/entities.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]


    for line in lines:
        if line.startswith(entity + " "):
            parts = line.split(" ")
            for part in range(1, len(parts)):
                if parts[part].startswith(".r"):
                    read_role = parts[part+1].split(",")  # Extrait le rôle après '.r'
                elif parts[part].startswith(".w"):
                    write_role = parts[part+1].split(",")  # Extrait le rôle après '.w'
                elif parts[part].startswith(".d"):
                    delete_role = parts[part+1].split(",")  # Extrait le rôle après '.d'

    if read_role == []:
        read_role = ["any"]
    if write_role == []:
        write_role = ["any"]
    if delete_role == []:
        delete_role = ["any"]
    print(f"Rôles pour l'entité '{entity}': Lecture: {read_role}, Écriture: {write_role}, Suppression: {delete_role}")  # Debug

    return read_role, write_role, delete_role