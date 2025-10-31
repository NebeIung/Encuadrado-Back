# Encuadrado-Back

Prueba Software Engineer (2025) - Encuadrado

## 📋 Descripción

Este proyecto es el backend de la aplicación Encuadrado, desarrollado como parte de la prueba técnica para la posición de Software Engineer 2025. Proporciona una API RESTful construida con Python.

## 🚀 Tecnologías

- **Python** (100%)
- Framework: Flask
- Base de datos: PostgreSQL hosteada en Aiven
- ORM: SQLAlchemy

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/NebeIung/Encuadrado-Back.git

# Navegar al directorio del proyecto
cd Encuadrado-Back

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

1. Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql://avnadmin:AVNS_mU0itWKTz3C7WoyFVS1@encuadrado-encuadrado.d.aivencloud.com:21762/defaultdb?sslmode=require

# CORS Configuration
FRONTEND_URL=http://localhost:5173
```

## 🏃‍♂️ Ejecución

```bash
# Activar entorno virtual (si no está activado)
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Ejecutar servidor de desarrollo
python main.py
```

## 🏗️ Estructura del Proyecto

```
Encuadrado-Back/
├── src/
│   ├── models/          # Modelos de base de datos
│   ├── routes/          # Endpoints de la API
│   ├── services/        # Lógica de negocio
│   ├── schemas/         # Esquemas de validación
│   ├── utils/           # Utilidades
│   └── config/          # Configuraciones
├── tests/               # Tests unitarios e integración
├── migrations/          # Migraciones de base de datos
├── requirements.txt     # Dependencias del proyecto
├── .env.example         # Ejemplo de variables de entorno
└── README.md
```

## 🔒 Seguridad

- Autenticación mediante JWT
- Encriptación de contraseñas con bcrypt
- Validación de datos de entrada
- Protección CORS configurada

## 📦 Dependencias Principales

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
psycopg2-binary>=2.9.9
```

## 👤 Autor

**NebeIung**

- GitHub: [@NebeIung](https://github.com/NebeIung)


## 🤝 Contribuciones

Este proyecto es parte de una prueba técnica.

---

⭐️ Desarrollado como parte de la prueba técnica para Encuadrado
