#!/usr/bin/env python3
import bcrypt
import sqlite3
from app import create_app
from models import db, User

# Test 1: Verificar directamente en SQLite
print("=== TEST 1: Verificación directa en SQLite ===")
conn = sqlite3.connect('dev3_pentest.db')
cursor = conn.cursor()
cursor.execute('SELECT username, password_hash, is_active, is_verified FROM users WHERE username = ?', ('admin',))
row = cursor.fetchone()
conn.close()

if row:
    username, pwd_hash, is_active, is_verified = row
    print(f"✅ Usuario encontrado en BD: {username}")
    print(f"   Activo: {is_active}, Verificado: {is_verified}")
    print(f"   Hash: {pwd_hash[:30]}...")
    result = bcrypt.checkpw('admin123'.encode('utf-8'), pwd_hash.encode('utf-8'))
    print(f"   Password check directo: {result}")
else:
    print("❌ Usuario NO encontrado en BD")

# Test 2: Verificar con SQLAlchemy
print("\n=== TEST 2: Verificación con SQLAlchemy ===")
app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f"✅ Usuario encontrado con SQLAlchemy: {user.username}")
        print(f"   Activo: {user.is_active}, Verificado: {user.is_verified}")
        print(f"   Hash: {user.password_hash[:30] if user.password_hash else 'None'}...")
        print(f"   Password check: {user.check_password('admin123')}")
    else:
        print("❌ Usuario NO encontrado con SQLAlchemy")


