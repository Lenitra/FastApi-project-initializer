# Format du fichier entities.txt

Ce document décrit le format du fichier `config/entities.txt` utilisé par le générateur FastAPI pour définir les entités de votre application.

## Structure générale

```
EntityName .r Role .w Role .d Role
- attribute_name type .modifier1 .modifier2
- another_attribute type .modifier
- ...

AnotherEntity
- ...
```

## Règles de syntaxe

### Nom d'entité
- **Format** : `EntityName .r Role .w Role .d Role` (PascalCase recommandé)
- **Rôles** :
    - `.r Role` : Rôle autorisé en lecture
    - `.w Role` : Rôle autorisé en écriture
    - `.d Role` : Rôle autorisé en suppression
    - Si pas de rôle spécifié, endpoint non protégé par l'authentification
- **Ligne dédiée** : Le nom d'entité (et ses rôles éventuels) doit être seul sur sa ligne
- **Exemple** :
    - `TLE .r admin .w admin .d admin`
    - `User .r user .w manager .d admin`
    - `Product .w manager .d admin`

### Attributs
- **Format** : `- attribute_name type .modifier1 .modifier2`
- **Préfixe** : Chaque attribut commence par `- `
- **Nom** : `snake_case` recommandé
- **Type** : Type Python standard ou personnalisé
- **Modifiers** : Optionnels, préfixés par `.`

## Types supportés

### Types de base
- `str` / `string` → String
- `int` / `integer` → Integer  
- `float` / `decimal` → Float
- `bool` / `boolean` → Boolean
- `date` → Date
- `datetime` → DateTime

### Types personnalisés
- Nom de classe personnalisée (ex: `Category`, `User`)
- Génère automatiquement les imports nécessaires

## Modifiers disponibles

### Contraintes de validation

#### `.nn` - Non Nullable
Rend le champ obligatoire (non nullable).
```
- nom str .nn
```
→ `nom: str`

#### `.unique` - Valeur unique
Ajoute une contrainte d'unicité en base de données.
```
- email str .unique
```
→ `email: str | None = Field(default=None, unique=True)`

#### `.default(value)` - Valeur par défaut
Définit une valeur par défaut.
```
- active bool .default(True)
- status str .default("pending")
```
→ `active: bool | None = Field(default=True)`

### Contraintes de longueur

#### `.maxlen(n)` - Longueur maximale (strings)
Limite la longueur d'une chaîne de caractères.
```
- nom str .maxlen(24)
```
→ `nom: str | None = Field(default=None, max_length=24)`

#### `.len(n)` - Longueur exacte (strings)
Force une longueur exacte (utilisé pour les chaînes fixes).
```
- ligne1 str .len(69)
```
→ `ligne1: str | None = Field(default=None, max_length=69)`

### Contraintes de valeur

#### `.range(min..max)` - Plage de valeurs
Définit une plage de valeurs autorisées (documentation seulement, validation à implémenter).
```
- type_element int .range(0..9)
- excentricite float .range(0..1)
```
→ `type_element: int | None = Field(default=None)` + commentaire

### Relations

#### `.fk EntityName` - Clé étrangère
Crée une relation avec une autre **entité**. Ca pointera vers l'attribut `id` de l'entité cible.
```
- category_id int .fk Category
```
→ 
```python
category_id: int | None = Field(default=None, foreign_key="category.id")
category: 'Category' | None = Relationship(back_populates="products")
```

## Exemples complets

### Entité simple
```
User
- email str .unique .nn
- nom str .maxlen(50)
- age int .range(0..120)
- active bool .default(True)
- created_at datetime
```

### Entité avec relations
```
Product
- name str .maxlen(100) .nn
- price float .nn
- description str
- category_id int .fk Category
- stock int .default(0)
- active bool .default(True)

Category
- name str .maxlen(50) .unique .nn
- description str
```

## Génération automatique

Pour chaque entité définie, le générateur crée automatiquement :

1. **Entity class** : `app/entities/entity_name.py`
   ```python
   class TLE(SQLModel, table=True):
       __tablename__ = "tle"
       id: int | None = Field(default=None, primary_key=True)
       nom: str | None = Field(default=None, max_length=24)
       # ...
   ```

2. **Repository class** : `app/repositories/entity_name_repository.py`
   ```python
   class TLERepository(BaseRepository[TLE]):
       def __init__(self):
           super().__init__(TLE)
   ```

3. **Router** : `app/routers/entity_name.py`
   ```python
   @router.get("/", response_model=list[TLE])
   def get_all_tles(db: Session = Depends(get_db)):
       return repo.list(db)
   # ...
   ```
