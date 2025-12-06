#!/usr/bin/env python3
"""
Script para crear usuario admin inicial
"""

from app import create_app
from models import db, User, Workspace

def create_admin_user():
    """Crea usuario admin y workspace por defecto."""
    app = create_app('development')
    
    with app.app_context():
        # Verificar si ya existe
        existing_user = User.query.filter_by(username='admin').first()
        
        if existing_user:
            print("❌ Usuario 'admin' ya existe")
            return
        
        # Crear usuario admin
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
        
        print(f"✅ Usuario admin creado con ID: {admin.id}")
        
        # Crear workspace por defecto
        workspace = Workspace(
            name='Default Workspace',
            description='Workspace principal para pentesting',
            owner_id=admin.id,
            is_active=True
        )
        
        db.session.add(workspace)
        db.session.commit()
        
        print(f"✅ Workspace creado con ID: {workspace.id}")
        print("\n" + "="*50)
        print("CREDENCIALES:")
        print("="*50)
        print(f"Usuario: admin")
        print(f"Password: admin123")
        print(f"Email: admin@pentesting.local")
        print(f"Workspace ID: {workspace.id}")
        print("="*50)

if __name__ == '__main__':
    create_admin_user()


