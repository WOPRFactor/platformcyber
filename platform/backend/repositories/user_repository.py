"""
User Repository
===============

Repository para operaciones de usuarios.
"""

from typing import Optional, List
from models import db, User


class UserRepository:
    """Repository para gestión de usuarios."""
    
    @staticmethod
    def create(username: str, email: str, password: str, role: str = 'analyst') -> User:
        """
        Crea un nuevo usuario.
        
        Args:
            username: Nombre de usuario
            email: Email
            password: Contraseña (será hasheada)
            role: Rol del usuario
        
        Returns:
            Usuario creado
        """
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def find_by_id(user_id: int) -> Optional[User]:
        """Busca usuario por ID."""
        return User.query.get(user_id)
    
    @staticmethod
    def find_by_username(username: str) -> Optional[User]:
        """Busca usuario por username."""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email: str) -> Optional[User]:
        """Busca usuario por email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_all(is_active: Optional[bool] = None) -> List[User]:
        """
        Lista todos los usuarios.
        
        Args:
            is_active: Filtrar por estado activo (opcional)
        
        Returns:
            Lista de usuarios
        """
        query = User.query
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        return query.all()
    
    @staticmethod
    def update(user: User) -> User:
        """Actualiza un usuario."""
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user: User) -> None:
        """Elimina un usuario."""
        db.session.delete(user)
        db.session.commit()
    
    @staticmethod
    def exists(username: str = None, email: str = None) -> bool:
        """
        Verifica si existe un usuario.
        
        Args:
            username: Username a verificar
            email: Email a verificar
        
        Returns:
            True si existe
        """
        query = User.query
        
        if username:
            query = query.filter_by(username=username)
        
        if email:
            query = query.filter_by(email=email)
        
        return query.first() is not None



