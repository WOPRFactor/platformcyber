#!/usr/bin/env python3
"""Script para resetear la contraseña del admin"""

from app import create_app
from models import db, User

def reset_admin_password():
    app = create_app('development')
    
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        
        if user:
            print(f"✅ Usuario admin encontrado (ID: {user.id})")
            user.set_password('admin123')
            db.session.commit()
            print("✅ Contraseña reseteada a 'admin123'")
            print(f"Verificando contraseña: {user.check_password('admin123')}")
        else:
            print("❌ Usuario admin no encontrado, creando...")
            admin = User(
                username='admin',
                email='admin@pentesting.local',
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Usuario admin creado (ID: {admin.id})")

if __name__ == '__main__':
    reset_admin_password()


