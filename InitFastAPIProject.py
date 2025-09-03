import os
import time
import shutil

from utils import get_entities


def create_env_config(project_path="/generated"):
    # region utils/core/config.py
    file_content = """from pydantic_settings import BaseSettings
from typing import Optional

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
    with open(project_path + "/.env.example", "w", encoding="utf-8") as f:
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
            f.write(generate_sql_schema(entity, entities[entity]))
            print(f"📄 Fichier généré : {sqlmodels_path}")

        with open(routers_path, "w", encoding="utf-8") as f:
            f.write(generate_getters_routes(entity))
            print(f"📄 Fichier généré : {routers_path}")

        with open(repositories_path, "w", encoding="utf-8") as f:
            f.write(generate_repository(entity))
            print(f"📄 Fichier généré : {repositories_path}")


def generate_repository(entity_name: str):
    return f"""from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from app.sqlmodels.{entity_name.lower()} import {entity_name}

class {entity_name}Repository(BaseRepository[{entity_name}]):
    def __init__(self):
        super().__init__({entity_name})
"""


def generate_sql_schema(entity_name: str, attributes: list):
    sql_content = "from sqlmodel import SQLModel, Field, Column\n"
    sql_content += "from typing import Optional\n"
    sql_content += "from datetime import datetime, date\n\n"

    # Add imports for custom types
    for attr in attributes:
        if is_custom_type(attr.split()[1]):
            sql_content += f"from app.sqlmodels.{attr.split()[1].lower()} import {attr.split()[1]}\n"

    sql_content += f"\nclass {entity_name}(SQLModel, table=True):\n"
    sql_content += f'    __tablename__ = "{entity_name.lower()}"\n\n'
    sql_content += "    id: Optional[int] = Field(default=None, primary_key=True)\n"

    for attr in attributes:
        var_name = attr.split()[0]
        var_type = attr.split()[1] if len(attr.split()) > 1 else "str"

        not_null = ".nn" in attr
        unique = ".unique" in attr
        fk = ".fk" in attr

        default = None
        try:
            default = attr.split(".default(")[1].strip().split(")")[0].strip()
        except Exception:
            default = None

        max_length = None
        if ".max" in attr:
            max_length = attr.split(".max")[1].split()[0].strip()

        # Convert Python types to SQLModel types
        if var_type.lower() in ["int", "integer"]:
            field_type = "int"
        elif var_type.lower() in ["str", "string"]:
            field_type = "str"
        elif var_type.lower() in ["float", "decimal"]:
            field_type = "float"
        elif var_type.lower() in ["bool", "boolean"]:
            field_type = "bool"
        elif var_type.lower() in ["date"]:
            field_type = "date"
        elif var_type.lower() in ["datetime"]:
            field_type = "datetime"
        else:
            field_type = var_type

        # Make optional if not required
        if not not_null:
            field_type = f"Optional[{field_type}]"

        # Build Field parameters
        field_params = []
        if default is not None:
            field_params.append(f"default={default}")
        elif not not_null:
            field_params.append("default=None")

        if unique:
            field_params.append("unique=True")

        if fk:
            fk_table = var_type.lower()
            field_params.append(f'foreign_key="{fk_table}.id"')

        if max_length and field_type.startswith(("str", "Optional[str]")):
            field_params.append(f"max_length={max_length}")

        field_def = f"Field({', '.join(field_params)})" if field_params else "Field()"
        sql_content += f"    {var_name}: {field_type} = {field_def}\n"

    return sql_content


def is_custom_type(py_type: str) -> bool:
    not_custom = ["int", "str", "float", "date", "bool", "list", "dict"]
    return not any(py_type.startswith(simple_type) for simple_type in not_custom)


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
from app.sqlmodels.{lname} import {entity_name}
from app.services.{lname}_service import {entity_name}Service
from sqlalchemy.orm import Session
from app.core.database import get_db


router = APIRouter()
service = {entity_name}Service()

@router.get("/", response_model=list[{entity_name}])
def get_all_{plural}(db: Session = Depends(get_db)):
    return service.list_{plural}(db)

@router.get("/{{id}}", response_model={entity_name})
def get_{lname}_by_id(id: int, db: Session = Depends(get_db)):
    obj = service.get_{lname}(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return obj

@router.post("/", response_model={entity_name}, status_code=201)
def create_{lname}(payload: dict = Body(...), db: Session = Depends(get_db)):
    return service.create_{lname}(db, payload)

@router.patch("/{{id}}", response_model={entity_name})
def update_{lname}(id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    obj = service.update_{lname}(db, id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return obj

@router.delete("/{{id}}", status_code=204)
def delete_{lname}(id: int, db: Session = Depends(get_db)):
    ok = service.delete_{lname}(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
'''


def copy_entities_txt(project_path):
    local_entities_txt = "config/entities.txt"
    dist_entities_txt = os.path.join(project_path, "entities.txt")

    with open(local_entities_txt, "r") as f:
        content = f.read()

    with open(dist_entities_txt, "w") as f:
        f.write(content)


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
    copy_entities_txt(project_path)

    print("✅ Projet FastAPI initialisé avec succès !")


if __name__ == "__main__":
    init_fastapi_project()
