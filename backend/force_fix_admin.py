#!/usr/bin/env python3
"""Script para forzar la creación/actualización del admin usando SQL directo"""

import bcrypt
import sqlite3
from datetime import datetime

# Conectar directamente
conn = sqlite3.connect('dev3_pentest.db', check_same_thread=False)
cursor = conn.cursor()

# Generar nuevo hash
pwd_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
now = datetime.utcnow().isoformat()

# Eliminar usuario existente si hay
cursor.execute('DELETE FROM users WHERE username = ?', ('admin',))

# Insertar nuevo usuario
cursor.execute('''
    INSERT INTO users (username, email, password_hash, role, is_active, is_verified, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('admin', 'admin@pentesting.local', pwd_hash, 'admin', 1, 1, now, now))

conn.commit()

# Verificar
cursor.execute('SELECT username, is_active, is_verified FROM users WHERE username = ?', ('admin',))
row = cursor.fetchone()
conn.close()

if row:
    print(f"✅ Usuario admin {'actualizado' if row[0] == 'admin' else 'creado'}")
    print(f"   Activo: {row[1]}, Verificado: {row[2]}")
    print("✅ Credenciales:")
    print("   Usuario: admin")
    print("   Password: admin123")
else:
    print("❌ Error al crear usuario")


