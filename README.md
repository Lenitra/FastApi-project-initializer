# FastAPI Project Initializer

Un générateur automatique de projets FastAPI avec architecture modulaire et système de CRUD complet.

## 🎯 Vue d'ensemble

Ce générateur crée automatiquement une application FastAPI structurée avec :
- **Architecture 3-tiers** : Entity, Repository, Service
- **CRUD automatique** : Génération complète des endpoints REST
- **Authentification JWT** : Système d'auth avec gestion des rôles
- **Configuration flexible** : Variables d'environnement centralisées
- **Types de données avancés** : Support complet des contraintes SQLModel

## 🚀 Démarrage rapide

### 1. Configuration des entités
Éditez le fichier `config/entities.txt` pour définir vos entités :

```txt
User .r user .w admin .d admin
- email str .nn .unique
- name str .nn .len(100)
- age int .range(0, 120)
- is_active bool .default(True)
- created_at datetime

Product .w manager .d admin
- name str .nn .len(255)
- price float .nn .range(0, 99999)
- description str
- stock int .default(0)
- category_id int .fk
```

### 2. Génération du projet
```bash
scripts/run.bat
```

### 3. Lancement de l'application
```bash
cd generated
setup.bat    # Installation des dépendances
run.bat      # Démarrage du serveur
```

L'API sera disponible sur http://127.0.0.1:8000  
Documentation interactive : http://127.0.0.1:8000/docs

## 📁 Structure générée

```
generated/
├── app/
│   ├── main.py                     # Point d'entrée FastAPI
│   ├── utils/
│   │   └── core/
│   │       ├── config.py           # Configuration Pydantic
│   │       └── database.py         # Session SQLAlchemy
│   ├── entities/                   # Modèles SQLModel
│   │   ├── user.py
│   │   └── [entity].py
│   ├── repositories/               # Couche d'accès données
│   │   ├── base_repository.py      # Repository générique
│   │   ├── user_repository.py
│   │   └── [entity]_repository.py
│   ├── routers/                    # Endpoints REST
│   │   ├── auth.py                 # Authentification JWT
│   │   └── [entity].py             # CRUD complet par entité
│   └── middleware/
│       └── auth_checker.py         # Validation des rôles
├── .env                            # Variables d'environnement
├── .env.example                    # Template de configuration
├── requirements.txt                # Dépendances Python
├── setup.bat                       # Script d'installation
└── run.bat                         # Script de lancement
```

## 🔧 Format du fichier entities.txt

### Syntaxe des entités

```txt
EntityName .r Role,Role .w Role .d any
- attribute_name type.modifier1.modifier2
```

**Rôles d'autorisation :**
- `.r role` : Lecture (GET)
- `.w role` : Écriture (POST, PUT, PATCH) 
- `.d role` : Suppression (DELETE)
- `any`, `*` ou non défini : Tous les rôles
⚠️ Pas d'espace entre les rôles et les virgules dans le cas de multiples rôles.

### Types supportés

| Type | Description |
|------|-------------|
| `str`, `string` | Chaîne de caractères |
| `int`, `integer` | Nombre entier |
| `float`, `decimal` | Nombre décimal |
| `bool`, `boolean` | Booléen |
| `date` | Date |
| `datetime` | Date et heure |
| `EntityName` | Relation vers une autre entité |

### Modifiers disponibles

| Modifier | Description | Exemple |
|----------|-------------|---------|
| `.nn` | Non nullable (obligatoire) | `name str .nn` |
| `.unique` | Valeur unique | `email str.unique` |
| `.default(value)` | Valeur par défaut | `active bool .default(True)` |
| `.len(n)` | Longueur maximale | `name str .len(100)` |
| `.range(min, max)` | Plage de valeurs | `age int .range(0, 120)` |
| `.fk` | Clé étrangère | `user_id int .fk` |

## 📋 Exemples complets

### Entité utilisateur
```txt
User .r user .w admin .d admin
- email str .nn .unique
- username str .nn .len(50)
- password_hash str .nn
- age int .range(13, 99)
- is_active bool .default(True)
- role str .default("user")
- created_at datetime
- updated_at datetime
```

### Entité avec relation
```txt
Category
- name str .nn .unique.len(100)
- description str .len(500)

Product .w manager .d admin
- name str .nn .len(255)
- description str
- price float .nn .range(0, 99999.99)
- stock int .default(0) .range(0, 999999)
- category_id int .fk
- is_available bool .default(True)
- created_at datetime
```

## 🔨 Génération automatique

Pour chaque entité, le générateur crée :

### 1. Entity (SQLModel)
```python
# app/entities/user.py
class User(SQLModel, table=True):
    __tablename__ = "user"
    
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    username: str = Field(max_length=50)
    age: int = Field(ge=13, le=99)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default=None)
```

### 2. Repository
```python
# app/repositories/user_repository.py
class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)
```

### 3. Router CRUD complet
```python
# app/routers/user.py
@router.get("/", response_model=list[User])
def get_all_users(db: Session = Depends(get_db), role = Depends(require_role(["any"]))):
    return repo.list(db)

@router.get("/{id}", response_model=User)
def get_user_by_id(id: int, db: Session = Depends(get_db), role = Depends(require_role(["any"]))):
    # ...

@router.post("/", response_model=User, status_code=201)
def create_user(payload: dict = Body(...), db: Session = Depends(get_db), role = Depends(require_role(["user", "admin"]))):
    # ...

@router.patch("/{id}", response_model=User)
def update_user(id: int, payload: dict = Body(...), db: Session = Depends(get_db), role = Depends(require_role(["user", "admin"]))):
    # ...

@router.delete("/{id}", status_code=204)
def delete_user(id: int, db: Session = Depends(get_db), role = Depends(require_role(["admin", "manager"]))):
    # ...
```

## 🔐 Authentification

Le système génère automatiquement :
- Endpoints de connexion/déconnexion : `/auth/login`
- Gestion des tokens JWT
- Protection des endpoints selon les rôles définis

## ⚙️ Configuration

Le fichier par défaut `.env` généré contient :
```env
# Base de données
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=db_fastapi_project

# Sécurité JWT
SECRET_KEY=[généré automatiquement]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Debug
DEBUG=True
```
Ajoutez vos variables personnalisées dans `config/add_to_env.txt` avant la génération.

## 🔄 Workflow de développement

1. **Définir** vos entités dans `config/entities.txt`
2. **Définir** vos variables d'environnement supplémentaires `config/add_to_env.txt`
3. **Générer** le projet avec `python InitFastAPIProject.py`
4. **Personnaliser** la configuration dans `generated/.env`
5. **Lancer en local** installer les dépendances avec `generated/script/setup.bat` puis executer `generated/script/run.bat`
6. **Déployer sur docker** l'application avec `generated/script/deploy_docker.bat`

## 📚 Fonctionnalités avancées

- **BaseRepository** : Méthodes CRUD génériques (list, get, save, delete)
- **Contraintes de validation** : Types, longueurs, plages de valeurs
- **Relations automatiques** : Foreign keys et imports d'entités
- **Environment flexible** : Configuration via `config/add_to_env.txt`
- **Scripts de déploiement** : Setup et run automatiques
- **Environnements multiples** : dev, docker via `envs/`

---

## ToDo List :

- Support des attributs de type List, Dict, Set
- Création dynamique d'utilisateurs initiaux via un fichier de config
- Pouvoir mettre de la doc swagger dans les endpoints et les paramètres depuis entities.txt
- Ajouter la gestion des migrations de base de données (intégration Alembic)
- Remplacer le fichier txt avec le modèle de données par un fichier json ?

