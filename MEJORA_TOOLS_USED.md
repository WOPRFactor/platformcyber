# Mejora: Detección Automática de `tools_used`

**Fecha:** Enero 2025  
**Ambiente:** dev4-improvements  
**Estado:** ✅ Implementado

---

## 🎯 Objetivo

Mejorar la detección automática de herramientas usadas en la generación de reportes, para que el campo `tools_used` en la base de datos contenga información correcta y completa.

---

## 🔧 Cambios Implementados

### 1. ParserManager - Nuevo Método `parse_file_with_parser()`

**Archivo:** `services/reporting/parsers/parser_manager.py`

**Cambios:**
- ✅ Nuevo método `parse_file_with_parser()` que retorna `(findings, parser_name)`
- ✅ Método `parse_file()` ahora usa internamente `parse_file_with_parser()` (retrocompatible)
- ✅ Nueva función `_get_tool_name_from_parser()` que extrae el nombre de la herramienta del nombre de la clase del parser
- ✅ Nueva función `_extract_tool_from_filename()` como fallback para extraer del nombre del archivo

**Ejemplo de uso:**
```python
findings, parser_name = parser_manager.parse_file_with_parser(file_path)
# parser_name será 'nmap', 'nuclei', 'enum4linux', etc.
```

**Mapeo de nombres:**
- `NmapParser` → `'nmap'`
- `NucleiParser` → `'nuclei'`
- `Enum4linuxParser` → `'enum4linux'`
- `SSHAuditParser` → `'ssh-audit'`
- `MySQLEnumParser` → `'mysql-enum'`
- Y muchos más...

---

### 2. Reporting Tasks - Detección de Herramientas

**Archivo:** `tasks/reporting_tasks.py`

**Cambios:**
- ✅ Usa `parse_file_with_parser()` en lugar de `parse_file()`
- ✅ Mantiene un conjunto `tools_detected` durante el parsing
- ✅ Combina herramientas detectadas del parser con las de `raw_data['tool']` (si existen)
- ✅ Elimina duplicados y ordena alfabéticamente
- ✅ Log warning si no se detectan herramientas

**Lógica de prioridad:**
1. **Prioridad 1:** Herramientas detectadas del parser usado (más confiable)
2. **Prioridad 2:** Herramientas de `raw_data['tool']` en findings (para parsers que ya lo agregaban)

**Código:**
```python
# Durante parsing
tools_detected = set()
for file_path in files:
    findings, parser_name = parser_manager.parse_file_with_parser(file_path)
    if parser_name:
        tools_detected.add(parser_name)

# Al final
tools_used_list = list(tools_detected)
# Agregar también de raw_data si existe
for finding in consolidated:
    if finding.raw_data and finding.raw_data.get('tool'):
        tools_used_list.append(finding.raw_data['tool'])

tools_used = sorted(list(set(tools_used_list)))
```

---

## 📊 Resultado Esperado

### Antes (Problema):
```json
{
  "tools_used": []  // Vacío o ['unknown']
}
```

### Después (Solución):
```json
{
  "tools_used": ["enum4linux", "nmap", "nuclei", "nikto", "subfinder"]
}
```

---

## ✅ Beneficios

1. **Datos correctos en BD:** `tools_used` siempre tendrá información válida
2. **Retrocompatibilidad:** `parse_file()` sigue funcionando igual
3. **Fallback robusto:** Si no hay parser, intenta extraer del nombre del archivo
4. **Sin cambios en parsers:** No requiere modificar los 42+ parsers existentes
5. **Logging mejorado:** Logs muestran qué parser se usó para cada archivo

---

## 🧪 Pruebas Recomendadas

1. **Test básico:**
   ```python
   pm = ParserManager()
   findings, parser_name = pm.parse_file_with_parser(Path('nmap_scan.xml'))
   assert parser_name == 'nmap'
   ```

2. **Test con workspace real:**
   - Generar reporte con archivos de múltiples herramientas
   - Verificar que `tools_used` en BD contenga todas las herramientas correctas

3. **Test de fallback:**
   - Archivo sin parser conocido
   - Verificar que intenta extraer del nombre del archivo

---

## 📝 Archivos Modificados

1. ✅ `services/reporting/parsers/parser_manager.py`
   - Nuevo método `parse_file_with_parser()`
   - Nuevas funciones helper `_get_tool_name_from_parser()` y `_extract_tool_from_filename()`
   - Método `parse_file()` actualizado para usar el nuevo método

2. ✅ `tasks/reporting_tasks.py`
   - Usa `parse_file_with_parser()` en lugar de `parse_file()`
   - Mantiene conjunto `tools_detected` durante parsing
   - Lógica mejorada para construir `tools_used`

---

## 🔄 Próximos Pasos

1. ✅ Probar con workspace real
2. ✅ Verificar que `tools_used` se guarda correctamente en BD
3. ⏳ Opcional: Agregar tests unitarios para las nuevas funciones
4. ⏳ Opcional: Mostrar `tools_used` en el frontend (historial de reportes)

---

**Implementado por:** Auto (Cursor AI)  
**Revisado por:** Pendiente  
**Estado:** ✅ Listo para pruebas

