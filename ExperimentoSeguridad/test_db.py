#!/usr/bin/env python3
"""
Script de prueba para verificar la inicialización de la base de datos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.user_service import init_db, engine
from app.models.db_models import Base, DBUser
from sqlalchemy import inspect

def test_database():
    print("🧪 Probando inicialización de base de datos...")
    
    try:
        # Inicializar BD
        init_db()
        
        # Verificar tablas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tablas creadas: {tables}")
        
        # Verificar estructura de la tabla users
        if 'users' in tables:
            columns = inspector.get_columns('users')
            print(f"🔍 Columnas de la tabla 'users':")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        
        print("✅ Base de datos funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()
