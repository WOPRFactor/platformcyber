#!/usr/bin/env python3
import bcrypt
import sqlite3
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect('dev3_pentest.db')
cursor = conn.cursor()

# Generar hash de la contraseña
pwd_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verificar si existe el usuario
cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
exists = cursor.fetchone()[0] > 0

if exists:
    # Actualizar usuario existente
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?, 
            is_active = 1, 
            is_verified = 1,
            updated_at = ?
        WHERE username = ?
    ''', (pwd_hash, datetime.utcnow(), 'admin'))
    print('✅ Usuario admin actualizado')
else:
    # Crear nuevo usuario
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, is_active, is_verified, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin@pentesting.local', pwd_hash, 'admin', 1, 1, datetime.utcnow(), datetime.utcnow()))
    print('✅ Usuario admin creado')

conn.commit()
conn.close()
print('✅ Base de datos actualizada')
print('Usuario: admin')
print('Password: admin123')


