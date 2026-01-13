# 🧪 Tests Directory

Esta carpeta contiene todos los archivos de prueba del proyecto organizados por tipo.

## 📁 Estructura

```
tests/
├── backend/           # Tests del backend (API, servicios, lógica de negocio)
│   ├── test_fixes.py  # Test completo de las correcciones implementadas
│   └── test_full_flow.py # Test del flujo completo de la aplicación
└── frontend/          # Tests del frontend (UI, estados, interacciones)
    ├── test_frontend.html # Test de accesibilidad del frontend
    ├── test.html         # Test básico de la interfaz
    └── debug.html        # Página de debug para desarrollo
```

## 🚀 Cómo ejecutar los tests

### Backend Tests
```bash
# Activar el entorno virtual
venv\Scripts\activate

# Ejecutar test de correcciones
python tests\backend\test_fixes.py

# Ejecutar test de flujo completo
python tests\backend\test_full_flow.py
```

### Frontend Tests
```bash
# Abrir en el navegador
http://localhost:8080/tests/frontend/test_frontend.html
http://localhost:8080/tests/frontend/test.html
http://localhost:8080/tests/frontend/debug.html
```

## 📋 Descripción de Tests

### Backend
- **test_fixes.py**: Verifica que todas las correcciones implementadas funcionen correctamente
- **test_full_flow.py**: Prueba el flujo completo desde creación de sesión hasta chat

### Frontend  
- **test_frontend.html**: Verifica conectividad y carga de recursos
- **test.html**: Test básico de la interfaz de usuario
- **debug.html**: Herramientas de debug para desarrollo