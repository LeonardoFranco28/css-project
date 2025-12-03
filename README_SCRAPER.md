# CSS Scraper - Extractor de Planillas

## 📋 Descripción

Este proyecto permite extraer datos de empleados de la página de transparencia de la Caja de Seguro Social de Panamá. El scraper ha sido refactorizado para incluir funcionalidades avanzadas como navegación automática por páginas y configuración de cantidad de registros.

## 🚀 Características

### ✨ Nuevas Funcionalidades

1. **Configuración de registros por página**: Cambia automáticamente entre 10, 20 o 50 registros por página
2. **Navegación automática**: Extrae datos de múltiples páginas automáticamente
3. **Scraping inteligente**: Detecta automáticamente la estructura de la página CSS
4. **Múltiples formatos de salida**: CSV y Parquet para mejor rendimiento
5. **Logs detallados**: Seguimiento completo del proceso de extracción

### 📊 Datos Extraídos

El scraper extrae la siguiente información de cada empleado:

- Identificación/Posición
- Cédula
- Nombre completo
- Cargo
- Departamento
- Estatus (Permanente, etc.)
- Inicio en planilla
- Salario
- Gastos
- Sobre sueldo
- Total
- Objeto de gasto

## 🛠 Instalación

### Prerrequisitos

- Python 3.8+
- Google Chrome instalado
- Conexión a internet

### Dependencias

```bash
pip install selenium polars webdriver-manager
```

## 📖 Uso

### 1. Uso Básico - Una página

```python
from app.services.workers import extract

# Extraer datos de una sola página (10 registros por defecto)
url = "https://transparencia.css.gob.pa/planilla/grid_defensoria/"
data = extract(url)
print(f"Registros extraídos: {data.shape[0]}")
```

### 2. Uso Avanzado - Múltiples páginas

```python
from app.services.workers import extract_all_pages

# Extraer datos de múltiples páginas con 50 registros por página
data = extract_all_pages(
    url="https://transparencia.css.gob.pa/planilla/grid_defensoria/",
    records_per_page=50,  # Opciones: 10, 20, 50
    max_pages=10         # Número máximo de páginas
)
print(f"Total de registros: {data.shape[0]}")
```

### 3. Configuración Personalizada

```python
from app.services.workers import scrape_with_config

# Configuración personalizada
config = {
    'records_per_page': 50,  # 10, 20 o 50
    'max_pages': 15,         # Máximo de páginas
    'headless': True,        # Ejecutar sin interfaz
    'wait_time': 5          # Tiempo de espera en segundos
}

data = scrape_with_config(url, config)
```

### 4. Trabajar con Archivo Local

```python
from app.services.workers import extract_from_local_html

# Si tienes un archivo HTML descargado
data = extract_from_local_html("path/to/page.html")
```

### 5. Ejecutar Ejemplo Completo

```bash
python ejemplo_scraping.py
```

## 📁 Estructura del Proyecto

```
css-project/
├── app/
│   ├── services/
│   │   └── workers.py          # Módulo principal de scraping
│   ├── db.py                   # Base de datos (si aplica)
│   └── main.py                 # Aplicación principal
├── ejemplo_scraping.py         # Ejemplo de uso
├── page.html                   # Página HTML de muestra
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

## 🔧 Funciones Principales

### `extract_all_pages()`

Función principal para scraping de múltiples páginas.

**Parámetros:**
- `url`: URL del sitio web
- `records_per_page`: Cantidad de registros por página (10, 20, 50)
- `max_pages`: Número máximo de páginas a extraer

### `scrape_with_config()`

Scraping con configuración personalizada.

**Parámetros:**
- `url`: URL del sitio web
- `config`: Diccionario con configuración personalizada

### `extract_from_local_html()`

Extrae datos de un archivo HTML local.

**Parámetros:**
- `file_path`: Ruta al archivo HTML local

## 📝 Ejemplos de Salida

### Archivos Generados

El scraper genera automáticamente:

- `employees_data.csv`: Datos en formato CSV
- `employees_data.parquet`: Datos en formato Parquet (más eficiente)

### Estadísticas de Ejemplo

```
=== INFORMACIÓN DEL DATASET ===
Filas: 250
Columnas: 12

Columnas disponibles: ['Identificacion / Posicion', 'Cédula', 'Nombre completo', ...]

=== PRIMERAS 5 FILAS ===
┌─────────────────────┬───────────┬─────────────────┬──────────────────┬─────────────────┐
│ Identificacion /... │ Cédula    │ Nombre completo │ Cargo            │ Departamento    │
├─────────────────────┼───────────┼─────────────────┼──────────────────┼─────────────────┤
│ 10202000165         │ 1-721-2263│ JEROME CAITO    │ ALMACENISTA I    │ ADMINISTRACION  │
│ 10202000166         │ 1-46-410  │ LEONARDO ESP... │ GUARDIAN         │ ADMINISTRACION  │
└─────────────────────┴───────────┴─────────────────┴──────────────────┴─────────────────┘
```

## ⚠️ Consideraciones

### Rendimiento

- **50 registros por página**: Más eficiente para grandes volúmenes
- **Tiempo de espera**: Aumentar `wait_time` si la conexión es lenta
- **Headless mode**: Usar `headless=True` para mejor rendimiento

### Buenas Prácticas

1. **Respeta el sitio web**: No hagas demasiadas requests muy rápido
2. **Maneja errores**: El scraper incluye manejo de errores robusto
3. **Guarda regularmente**: Los datos se guardan automáticamente
4. **Monitorea logs**: Usa los logs para detectar problemas

## 🐛 Solución de Problemas

### Error: "No se encontraron filas de datos"

- Verificar que la URL sea correcta
- Aumentar el tiempo de espera
- Comprobar la conectividad a internet

### Error: "Timeout"

- Aumentar `wait_time` en la configuración
- Verificar la estabilidad de la conexión
- Reintentar con menos páginas

### Chrome Driver Issues

El script usa `webdriver-manager` para manejar automáticamente Chrome Driver. Si hay problemas:

```bash
pip install --upgrade webdriver-manager
```

## 📊 Análisis Posterior

### Con Pandas

```python
import pandas as pd

# Leer datos guardados
df = pd.read_csv('employees_data.csv')

# Análisis por departamento
dept_analysis = df.groupby('Departamento')['Salario'].agg(['count', 'mean', 'sum'])
print(dept_analysis)
```

### Con Polars (Recomendado)

```python
import polars as pl

# Leer datos (más eficiente)
df = pl.read_parquet('employees_data.parquet')

# Análisis rápido
analysis = df.group_by('Departamento').agg([
    pl.count().alias('empleados'),
    pl.col('Salario').mean().alias('salario_promedio'),
    pl.col('Salario').sum().alias('total_salarios')
])
print(analysis)
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🔗 Links Útiles

- [Página de Transparencia CSS](https://transparencia.css.gob.pa/planilla/grid_defensoria/)
- [Documentación de Selenium](https://selenium-python.readthedocs.io/)
- [Documentación de Polars](https://pola-rs.github.io/polars-book/)