# Entorno de Mejoras - dev4-improvements

## Descripción

Este es el entorno de desarrollo para mejoras y nuevas funcionalidades. Está completamente separado del entorno estable (`dev3-refactor`) para permitir desarrollo y pruebas sin interferir con la versión funcional.

## Configuración de Puertos

### Backend
- **Puerto**: `5001`
- **URL**: `http://localhost:5001` o `http://192.168.0.11:5001`
- **API Base**: `http://localhost:5001/api/v1`

### Frontend
- **Puerto**: `5180`
- **URL**: `http://localhost:5180` o `http://192.168.0.11:5180`
- **Proxy**: Redirige `/api` a `http://localhost:5001`

### Redis
- **Puerto**: `6379` (mismo servidor)
- **Base de Datos**: `3` (separada de dev3-refactor que usa DB 2)
- **URL**: `redis://localhost:6379/3`

## Comparación con dev3-refactor

| Componente | dev3-refactor (Estable) | dev4-improvements (Mejoras) |
|------------|------------------------|----------------------------|
| Backend Port | 5000 | 5001 |
| Frontend Port | 5179 | 5180 |
| Redis DB | 2 | 3 |
| Base de Datos | `dev3_pentest.db` | `dev3_pentest.db` (puede cambiarse) |

## Inicio del Entorno

### Backend
```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
source venv/bin/activate  # Si usas venv
python app.py
```

El backend estará disponible en `http://localhost:5001`

### Frontend
```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/frontend
npm install  # Solo la primera vez
npm run dev
```

El frontend estará disponible en `http://localhost:5180`

## Configuración CORS

El backend está configurado para aceptar conexiones desde:
- `http://localhost:5180` (dev4-improvements)
- `http://192.168.0.11:5180` (dev4-improvements en LAN)
- También mantiene compatibilidad con puertos de dev3-refactor

## WebSocket

El WebSocket se conecta automáticamente a:
- Desarrollo: `http://192.168.0.11:5001`
- Producción: `http://192.168.0.11:5002`

## Notas Importantes

1. **Independencia Total**: Los dos entornos pueden ejecutarse simultáneamente sin conflictos.

2. **Base de Datos**: Por defecto comparten el mismo archivo SQLite. Si necesitas separación completa, cambia `SQLALCHEMY_DATABASE_URI` en `config/__init__.py`.

3. **Redis**: Usa bases de datos diferentes (2 vs 3), por lo que el cache está completamente separado.

4. **Logs**: Los logs se guardan en `logs/` dentro de cada entorno, por lo que están separados.

5. **Workspaces**: Los workspaces se guardan en `platform/workspaces/` dentro de cada entorno, por lo que están separados.

## Desarrollo de Mejoras

Este entorno está diseñado para:
- Probar nuevas funcionalidades
- Experimentar con mejoras
- Desarrollar features sin afectar el entorno estable
- Realizar refactorizaciones grandes

Una vez que las mejoras estén probadas y validadas, se pueden integrar al entorno estable (`dev3-refactor`).

## Migración de Mejoras a Estable

Cuando una mejora esté lista para producción:

1. Revisar cambios en `dev4-improvements`
2. Hacer merge/commit de los cambios
3. Aplicar cambios a `dev3-refactor`
4. Probar en `dev3-refactor`
5. Si todo está bien, la mejora está lista

## Troubleshooting

### Puerto en uso
Si el puerto 5001 o 5180 está en uso:
```bash
# Verificar qué proceso usa el puerto
lsof -i :5001
lsof -i :5180

# Detener proceso si es necesario
kill -9 <PID>
```

### CORS Errors
Si hay errores de CORS, verificar que:
1. El backend esté corriendo en puerto 5001
2. El frontend esté corriendo en puerto 5180
3. Los orígenes estén configurados en `app.py`

### Redis Connection
Si hay problemas con Redis:
```bash
# Verificar que Redis esté corriendo
redis-cli ping

# Verificar bases de datos
redis-cli
> SELECT 2  # dev3-refactor
> SELECT 3  # dev4-improvements
```


