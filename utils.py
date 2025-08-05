

#region 

def get_entities():
    """
    Lit le fichier 'entities.txt' et extrait les entités ainsi que leurs attributs.

    Le fichier doit être structuré de la façon suivante :
    Chaque entité est définie par une ligne sans indentation ni tiret, suivie de ses attributs précédés de '- '.
    Exemple :
        User
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

    with open("entities.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    for line in lines:
        if not line.startswith(" ") and not line.startswith("- "):
            entity_name = line.strip()
            if entity_name != "":
                entities[entity_name] = []

        elif line.startswith("- "):
            entities[entity_name].append(line.strip()[2:])

    return entities

#endregion