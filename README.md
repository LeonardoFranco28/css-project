# CSS Analytics API 📊

Una API moderna construida con **FastAPI** que permite visualizar y analizar la planilla de empleados del CSS (Caja de Seguro Social) a través de dashboards interactivos y endpoints RESTful.

## 🚀 Características

- **API RESTful** con FastAPI para acceso a datos de empleados
- **Web Scraping** automatizado con Selenium y BeautifulSoup
- **Base de datos** MongoDB para almacenamiento eficiente
- **Análisis de datos** con Polars y Pandas
- **Dashboards interactivos** para visualización de datos
- **Containerización** con Docker para fácil despliegue
- **Documentación automática** con Swagger UI

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Python 3.8+**: Lenguaje de programación
- **Uvicorn**: Servidor ASGI de alto rendimiento

### Base de Datos
- **MongoDB**: Base de datos NoSQL para almacenamiento de documentos
- **PyMongo**: Driver oficial de Python para MongoDB

### Web Scraping & Análisis
- **Selenium**: Automatización de navegadores web
- **BeautifulSoup4**: Parsing de HTML
- **Polars**: Manipulación de datos de alta velocidad
- **Pandas**: Análisis de datos
- **Requests**: Cliente HTTP

### DevOps
- **Docker**: Containerización
- **WebDriver Manager**: Gestión automática de drivers

## 📋 Requisitos Previos

- Python 3.8 o superior
- MongoDB instalado y ejecutándose
- Docker (opcional, para containerización)
- Chrome/Chromium (para web scraping)

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd css-project
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crear un archivo `.env` en la raíz del proyecto:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=css_analytics
CSS_LOGIN_URL=https://css.gob.pa/login
CSS_USERNAME=tu_usuario
CSS_PASSWORD=tu_contraseña
```

## 🚀 Uso

### Ejecutar la aplicación
```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
python -m app.main
```

La API estará disponible en: `http://localhost:8000`

### Documentación interactiva
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🐳 Docker

### Construir imagen
```bash
docker build -t css-analytics .
```

### Ejecutar contenedor
```bash
docker run -p 8000:8000 css-analytics
```

## 📊 Endpoints de la API

### Salud del servicio
```
GET /
```
Verifica el estado de la API.

### Planilla de empleados
```
GET /empleados
```
Obtiene la lista completa de empleados del CSS.

### Dashboard de estadísticas
```
GET /dashboard/stats
```
Retorna estadísticas generales de empleados.

### Filtros avanzados
```
GET /empleados/filtro?departamento=IT&salario_min=1000
```
Permite filtrar empleados por diferentes criterios.

## 📈 Dashboards Disponibles

1. **Dashboard General**: Estadísticas generales de empleados
2. **Análisis Salarial**: Distribución de salarios por departamento
3. **Tendencias**: Evolución histórica de la planilla
4. **Departamentos**: Análisis por área de trabajo

## 🔒 Seguridad

- Autenticación JWT implementada
- Variables sensibles en archivos `.env`
- Validación de datos con Pydantic
- Rate limiting para prevenir abuso

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Con cobertura
pytest --cov=app tests/
```

## 📁 Estructura del Proyecto

```
css-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── db.py                # Configuración de base de datos
│   └── services/
│       ├── workers.py       # Workers para web scraping
│       └── data/            # Procesamiento de datos
├── cmd/
│   └── start.sh             # Script de inicio
├── tests/                   # Tests unitarios
├── .env                     # Variables de entorno
├── .gitignore              # Archivos ignorados por git
├── Dockerfile              # Configuración de Docker
├── requirements.txt        # Dependencias de Python
└── README.md              # Este archivo
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Roadmap

- [ ] Implementar autenticación OAuth2
- [ ] Añadir más tipos de dashboards
- [ ] Integrar notificaciones en tiempo real
- [ ] Implementar cache con Redis
- [ ] Añadir exportación a PDF/Excel
- [ ] Crear aplicación móvil

## 🐛 Reporte de Bugs

Si encuentras algún problema, por favor crea un issue en el repositorio con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado
- Screenshots (si aplica)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

- **Desarrollador Principal**: [Tu Nombre]
- **Email**: [tu-email@ejemplo.com]

## 🙏 Agradecimientos

- CSS de Panamá por proporcionar los datos
- Comunidad de FastAPI por la excelente documentación
- Contribuidores del proyecto

---

⭐ Si este proyecto te ha sido útil, ¡no olvides darle una estrella!