# Instrucciones de Migración de Base de Datos

## Migración: add_workspace_target_fields.sql

### Descripción
Esta migración agrega campos necesarios para el sistema mejorado de workspaces, permitiendo asociar cada workspace con un target principal y definir el scope del proyecto.

### Campos Agregados

**Target Principal:**
- `target_domain` (VARCHAR 255): Dominio o URL principal del proyecto
- `target_ip` (VARCHAR 50): Dirección IP del target (opcional)
- `target_type` (VARCHAR 50): Tipo de aplicación (web, api, mobile, network, other)

**Scope del Proyecto:**
- `in_scope` (TEXT): Elementos dentro del alcance
- `out_of_scope` (TEXT): Elementos fuera del alcance

**Fechas:**
- `start_date` (DATE): Fecha de inicio del proyecto
- `end_date` (DATE): Fecha límite del proyecto

**Notas:**
- `notes` (TEXT): Notas adicionales del proyecto

### Cómo Ejecutar

#### Opción 1: Ejecución Manual (PostgreSQL)

```bash
# Conectar a la base de datos
psql -U postgres -d pentesting_platform

# Ejecutar migración
\i /home/kali/Proyectos/cybersecurity/environments/dev3-refactor/platform/backend/migrations/add_workspace_target_fields.sql

# Verificar columnas agregadas
\d workspaces
```

#### Opción 2: Desde Python/Flask

```python
from models import db
import os

# Leer el archivo SQL
migration_file = os.path.join(
    os.path.dirname(__file__),
    'migrations',
    'add_workspace_target_fields.sql'
)

with open(migration_file, 'r') as f:
    sql = f.read()

# Ejecutar migración
db.session.execute(sql)
db.session.commit()
```

#### Opción 3: Script de Shell

```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev3-refactor/platform/backend

# Ejecutar migración
psql -U postgres -d pentesting_platform -f migrations/add_workspace_target_fields.sql
```

### Verificación Post-Migración

```sql
-- Verificar que las columnas existan
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'workspaces'
AND column_name IN (
    'target_domain', 'target_ip', 'target_type',
    'in_scope', 'out_of_scope',
    'start_date', 'end_date', 'notes'
);

-- Verificar índices
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'workspaces'
AND indexname LIKE 'idx_workspaces_target%';
```

### Rollback (Si es necesario)

```sql
-- Eliminar columnas agregadas
ALTER TABLE workspaces DROP COLUMN IF EXISTS target_domain;
ALTER TABLE workspaces DROP COLUMN IF EXISTS target_ip;
ALTER TABLE workspaces DROP COLUMN IF EXISTS target_type;
ALTER TABLE workspaces DROP COLUMN IF EXISTS in_scope;
ALTER TABLE workspaces DROP COLUMN IF EXISTS out_of_scope;
ALTER TABLE workspaces DROP COLUMN IF EXISTS start_date;
ALTER TABLE workspaces DROP COLUMN IF EXISTS end_date;
ALTER TABLE workspaces DROP COLUMN IF EXISTS notes;

-- Eliminar índices
DROP INDEX IF EXISTS idx_workspaces_target_domain;
DROP INDEX IF EXISTS idx_workspaces_target_type;
```

### Notas Importantes

1. **Retrocompatibilidad**: Todas las columnas nuevas son NULL-able, por lo que los workspaces existentes no se verán afectados.

2. **Valores por Defecto**: No se requieren valores por defecto; el frontend manejará valores null apropiadamente.

3. **Backup**: Se recomienda hacer un backup de la base de datos antes de ejecutar la migración:
   ```bash
   pg_dump -U postgres pentesting_platform > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql
   ```

4. **Testing**: Después de la migración, verificar que:
   - Los workspaces existentes aún funcionan correctamente
   - Se pueden crear nuevos workspaces con los campos adicionales
   - Las actualizaciones de workspaces funcionan correctamente

### Estado de la Aplicación

**Backend:**
- ✅ Modelo actualizado (workspace.py)
- ✅ Repository actualizado (workspace_repository.py)
- ✅ API actualizada (workspaces.py)

**Frontend:**
- ⏳ Pendiente: Actualizar interfaces TypeScript
- ⏳ Pendiente: Crear WorkspaceFormModal
- ⏳ Pendiente: Implementar auto-complete en scans

**Base de Datos:**
- ✅ Script de migración creado
- ⏳ Pendiente: Ejecutar migración




