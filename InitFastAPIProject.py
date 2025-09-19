import os
import time
import shutil

from utils import get_entities


def create_env_config(project_path="generated"):
    # region utils/core/config.py
    file_content = """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Configuration de base de données
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str

    # Configuration de sécurité
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
"""

    # ajouter les lignes de add_to_env.txt
    add_to_env_path = os.path.join("config/add_to_env.txt")
    if os.path.exists(add_to_env_path):
        with open(add_to_env_path, "r", encoding="utf-8") as add_file:
            for e in add_file.readlines():
                if e.__contains__("="):
                    file_content += "\n    " + e.split("=")[0] + ": str"

    file_content += """

    class Config:
        env_file = ".env"

settings = Settings()
"""

    with open(project_path + "/app/utils/core/config.py", "w", encoding="utf-8") as f:
        f.write(file_content)

    # endregion

    # region .env
    import random

    secret_key = random.SystemRandom().getrandbits(256)
    file_content = """# Variables d'environnement - remplir selon besoin
DEBUG=True

# Informations de connexion à la base de données
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=db_fastapi_project

# Configuration de sécurité
SECRET_KEY={}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
""".format(secret_key)

    # ajouter le contenu du fichier add_to_env.txt
    add_to_env_path = os.path.join("config/add_to_env.txt")
    if os.path.exists(add_to_env_path):
        with open(add_to_env_path, "r", encoding="utf-8") as add_file:
            file_content += "\n" + add_file.read()

    with open(project_path + "/.env", "w", encoding="utf-8") as f:
        f.write(file_content)
    
    with open(project_path + "/envs/dev.txt", "w", encoding="utf-8") as f:
        f.write(file_content)

    # TODO: Modifier les variables pour la prod
    with open(project_path + "/envs/docker.txt", "w", encoding="utf-8") as f:
        f.write(file_content)

    # endregion


def create_custom_entities(base_path="."):
    entities = get_entities()
    for entity in entities:
        filename = entity.lower() + ".py"
        sqlmodels_path = os.path.join(base_path, "app", "entities", filename)
        routers_path = os.path.join(base_path, "app", "routers", filename)
        repositories_path = os.path.join(
            base_path, "app", "repositories", entity.lower() + "_repository.py"
        )

        with open(sqlmodels_path, "w", encoding="utf-8") as f:
            f.write(generate_sql_model(entity, entities[entity]))
            print(f"📄 Fichier généré : {sqlmodels_path}")

        with open(routers_path, "w", encoding="utf-8") as f:
            f.write(generate_getters_routes(entity))
            print(f"📄 Fichier généré : {routers_path}")

        with open(repositories_path, "w", encoding="utf-8") as f:
            f.write(generate_repository(entity))
            print(f"📄 Fichier généré : {repositories_path}")


def generate_repository(entity_name: str):
    return f"""from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.entities.{entity_name.lower()} import {entity_name}

class {entity_name}Repository(BaseRepository[{entity_name}]):
    def __init__(self):
        super().__init__({entity_name})
"""


def generate_sql_model(entity_name: str, attributes: list):
    sql_content = "from sqlmodel import SQLModel, Field\n"
    sql_content += "from datetime import datetime, date\n\n"

    # Add imports for custom types
    custom_types = set()
    for attr in attributes:
        attr_parts = attr.split()
        if len(attr_parts) > 1 and _is_custom_type(attr_parts[1]):
            custom_types.add(attr_parts[1])
    
    for custom_type in custom_types:
        sql_content += f"from app.entities.{custom_type.lower()} import {custom_type}\n"

    sql_content += f"\nclass {entity_name}(SQLModel, table=True):\n"
    sql_content += f'    __tablename__ = "{entity_name.lower()}"\n\n'
    sql_content += "    id: int = Field(default=None, primary_key=True)\n"

    for attr in attributes:
        attr_parts = attr.split()
        var_name = attr_parts[0]
        var_type = attr_parts[1] if len(attr_parts) > 1 else "str"

        # Parse modifiers
        modifiers = _parse_attribute_modifiers(attr)
        
        # Convert Python types to SQLModel types
        field_type = _convert_type_to_sqlmodel(var_type)

        # Build Field parameters
        field_params = _build_field_parameters(modifiers, var_type)

        field_def = f"Field({', '.join(field_params)})" if field_params else "Field()"
        sql_content += f"    {var_name}: {field_type} = {field_def}\n"

    return sql_content


def _parse_attribute_modifiers(attr: str) -> dict:
    modifiers = {
        'not_null': '.nn' in attr,
        'unique': '.unique' in attr,
        'foreign_key': '.fk' in attr,
        'default': None,
        'max_length': None,
        'range_min': None,
        'range_max': None
    }
    
    # Parse default value
    if '.default(' in attr:
        try:
            start = attr.find('.default(') + len('.default(')
            end = attr.find(')', start)
            if end != -1:
                modifiers['default'] = attr[start:end].strip()
        except:  # noqa: E722
            pass
    
    # Parse max length - look for .len( followed by digits
    if '.len(' in attr:
        try:
            start = attr.find('.len(') + len('.len(')
            end = attr.find(')', start)
            if end != -1:
                modifiers['max_length'] = attr[start:end].strip()
        except:  # noqa: E722
            pass
    
    # Parse range - look for .range(min, max) or .range(min,) or .range(,max)
    if '.range(' in attr:
        try:
            start = attr.find('.range(') + len('.range(')
            end = attr.find(')', start)
            if end != -1:
                range_content = attr[start:end].strip()
                if ',' in range_content:
                    range_parts = [part.strip() for part in range_content.split(',')]
                    # Handle min value (first part)
                    if len(range_parts) >= 1 and range_parts[0]:
                        modifiers['range_min'] = range_parts[0]
                    # Handle max value (second part)
                    if len(range_parts) >= 2 and range_parts[1]:
                        modifiers['range_max'] = range_parts[1]
                else:
                    # Single value case - treat as both min and max
                    if range_content:
                        modifiers['range_min'] = range_content
                        modifiers['range_max'] = range_content
        except:  # noqa: E722
            pass
    
    return modifiers


def _convert_type_to_sqlmodel(var_type: str) -> str:
    type_mapping = {
        'int': 'int',
        'integer': 'int',
        'str': 'str', 
        'string': 'str',
        'float': 'float',
        'decimal': 'float',
        'bool': 'bool',
        'boolean': 'bool',
        'date': 'date',
        'datetime': 'datetime'
    }
    
    return type_mapping.get(var_type.lower(), var_type)


def _build_field_parameters(modifiers: dict, var_type: str) -> list:
    field_params = []
    
    if modifiers['default'] is not None:
        field_params.append(f"default={modifiers['default']}")
    elif not modifiers['not_null']:
        field_params.append("default=None")
    
    if modifiers['unique']:
        field_params.append("unique=True")
    
    if modifiers['foreign_key']:
        fk_table = var_type.lower()
        field_params.append(f'foreign_key="{fk_table}.id"')
    
    if modifiers['max_length'] and var_type.lower() in ['str', 'string']:
        field_params.append(f"max_length={modifiers['max_length']}")
    
    # Add range constraints for numeric types
    if var_type.lower() in ['int', 'integer', 'float', 'decimal']:
        if modifiers['range_min'] is not None:
            field_params.append(f"ge={modifiers['range_min']}")
        if modifiers['range_max'] is not None:
            field_params.append(f"le={modifiers['range_max']}")
    
    return field_params


def _is_custom_type(py_type: str) -> bool:
    built_in_types = {'int', 'str', 'float', 'date', 'datetime', 'bool', 'list', 'dict', 'integer', 'string', 'decimal', 'boolean'}
    return py_type.lower() not in built_in_types




def parse_py_types_to_sql_type(py_type: str) -> str:
    if py_type.lower() in ["int", "integer"]:
        return "Integer"
    elif py_type.lower() in ["str", "string"]:
        return "String"
    elif py_type.lower() in ["float", "decimal"]:
        return "Float"
    elif py_type.lower() in ["datetime"]:
        return "DateTime"
    elif py_type.lower() in ["date"]:
        return "Date"
    elif py_type.lower() in ["bool", "boolean"]:
        return "Boolean"
    else:
        print("⚠️ Type non reconnu : " + py_type)
        print("Le type sera ajouté tel quel")
        return py_type


def generate_getters_routes(entity_name: str) -> str:
    lname = entity_name.lower()
    plural = lname
    if lname.endswith("s"):
        plural = lname
    else:
        plural = lname + "s"

    return f'''from fastapi import Body, APIRouter, HTTPException, Depends
from app.entities.{lname} import {entity_name}
from sqlalchemy.orm import Session
from app.repositories.{lname}_repository import {entity_name}Repository
from app.utils.core.database import get_db


router = APIRouter(prefix="/{plural}", tags=["{entity_name}"])
repo = {entity_name}Repository()

@router.get("/", response_model=list[{entity_name}])
def get_all_{plural}(db: Session = Depends(get_db)):
    return repo.list(db)

@router.get("/{{id}}", response_model={entity_name})
def get_{lname}_by_id(id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return obj

@router.post("/", response_model={entity_name}, status_code=201)
def create_{lname}(payload: dict = Body(...), db: Session = Depends(get_db)):
    return repo.save(db, payload)

@router.put("/{{id}}", response_model={entity_name})
def update_{lname}(id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    obj = repo.save(db, id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return obj

@router.delete("/{{id}}", status_code=204)
def delete_{lname}(id: int, db: Session = Depends(get_db)):
    ok = repo.delete(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
'''


def copy_base_template(project_path):
    local_base_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "template")
    )
    dist_base_path = os.path.join(project_path)

    shutil.copytree(local_base_path, dist_base_path)


def init_fastapi_project():
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "generated"))

    print("Initialisation du projet FastAPI dans :", project_path)

    # Suppression robuste du dossier existant
    while os.path.exists(project_path):
        try:
            os.rmdir(project_path)
        except Exception:
            print("Erreur lors de la suppression du dossier :", project_path)
            time.sleep(0.25)

    copy_base_template(project_path)
    create_env_config(project_path)
    create_custom_entities(project_path)

    print("✅ Projet FastAPI initialisé avec succès !")


if __name__ == "__main__":
    init_fastapi_project()
