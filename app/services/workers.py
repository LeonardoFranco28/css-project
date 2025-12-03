# ------------------------------------ LIBRERIAS ------------------
import requests
import polars as pl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------ FUNCIONES ------------------

def extract_from_local_html(file_path: str) -> pl.DataFrame:
    """
    Extrae datos de un archivo HTML local que contiene una tabla de empleados
    
    Args:
        file_path: Ruta al archivo HTML local
    
    Returns:
        DataFrame de Polars con los datos extraídos
    """
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Convertir ruta a URL de archivo
        file_url = f"file:///{file_path.replace('\\', '/')}"
        logger.info(f"Abriendo archivo: {file_url}")
        driver.get(file_url)
        
        # Esperar a que la página cargue
        time.sleep(2)
        
        # Extraer headers de la tabla - buscar elementos con clase scGridLabelFont
        header_elements = driver.find_elements(By.CSS_SELECTOR, ".scGridLabelFont a")
        table_headers = []
        
        for header in header_elements:
            # Extraer solo el texto del enlace, ignorando la imagen
            header_text = header.text.strip()
            if header_text:  # Solo agregar headers no vacíos
                table_headers.append(header_text)
        
        logger.info(f"Headers encontrados: {table_headers}")
        
        # Extraer filas de datos - buscar filas con clase scGridFieldOdd o scGridFieldEven
        data_rows = driver.find_elements(By.CSS_SELECTOR, ".scGridFieldOdd, .scGridFieldEven")
        
        if not data_rows:
            logger.warning("No se encontraron filas de datos")
            return pl.DataFrame()
        
        extracted_data = []
        
        for i, row in enumerate(data_rows, 1):
            # Encontrar todas las celdas de datos en la fila (excluyendo la primera que es el botón de detalles)
            cells = row.find_elements(By.CSS_SELECTOR, "td span[id^='id_sc_field_']")
            
            if cells:
                row_data = []
                for cell in cells:
                    cell_text = cell.text.strip()
                    row_data.append(cell_text)
                
                if row_data:  # Solo agregar si la fila tiene datos
                    extracted_data.append(row_data)
                    logger.debug(f"Fila {i}: {row_data}")
        
        logger.info(f"Se extrajeron {len(extracted_data)} filas de datos")
        
        # Crear DataFrame
        if extracted_data and table_headers:
            # Asegurar que todas las filas tengan el mismo número de columnas que los headers
            max_cols = len(table_headers)
            normalized_rows = []
            
            for row in extracted_data:
                # Ajustar fila para que coincida con el número de columnas
                if len(row) > max_cols:
                    normalized_row = row[:max_cols]  # Truncar si es muy larga
                else:
                    normalized_row = row + [''] * (max_cols - len(row))  # Rellenar si es muy corta
                normalized_rows.append(normalized_row)
            
            # Crear DataFrame con los headers como nombres de columna
            df = pl.DataFrame(normalized_rows, schema=table_headers)
            
            # Limpiar y convertir tipos de datos
            df = clean_and_convert_data(df)
            
            return df
        else:
            logger.warning("No se pudieron extraer datos válidos")
            return pl.DataFrame()
            
    except Exception as e:
        logger.error(f"Error durante la extracción: {str(e)}")
        return pl.DataFrame()
    finally:
        if driver:
            driver.quit()


def extract_all_pages(url: str, records_per_page: int = 50, max_pages: int = 10) -> pl.DataFrame:
    """
    Extrae datos de múltiples páginas de la tabla de empleados
    
    Args:
        url: URL del sitio web
        records_per_page: Número de registros por página (10, 20, 50)
        max_pages: Número máximo de páginas a extraer
    
    Returns:
        DataFrame de Polars con todos los datos extraídos
    """
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    all_data = []
    
    try:
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info(f"Navegando a: {url}")
        driver.get(url)
        
        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".scGridLabelFont, table"))
        )
        
        time.sleep(3)
        
        # Paso 1: Cambiar cantidad de registros por página
        if records_per_page != 10:  # Solo cambiar si no es el valor por defecto
            try:
                logger.info(f"Cambiando a {records_per_page} registros por página...")
                
                # Buscar el selector de cantidad de líneas
                quantity_select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "quant_linhas_f0_bot"))
                )
                
                # Seleccionar la opción deseada
                from selenium.webdriver.support.ui import Select
                select = Select(quantity_select)
                select.select_by_value(str(records_per_page))
                
                # Esperar a que la página se recargue con la nueva cantidad
                time.sleep(5)
                
                # Verificar que el cambio se aplicó
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".scGridFieldOdd, .scGridFieldEven"))
                )
                
                logger.info(f"Cantidad de registros cambiada exitosamente a {records_per_page}")
                
            except Exception as e:
                logger.warning(f"No se pudo cambiar la cantidad de registros: {e}")
        
        # Paso 2: Extraer headers (solo una vez)
        table_headers = extract_headers(driver)
        logger.info(f"Headers encontrados: {table_headers}")
        
        # Paso 3: Extraer datos de múltiples páginas
        for page_num in range(1, max_pages + 1):
            try:
                logger.info(f"Extrayendo datos de la página {page_num}...")
                
                # Extraer datos de la página actual
                page_data = extract_page_data(driver)
                
                if page_data:
                    all_data.extend(page_data)
                    logger.info(f"Página {page_num}: {len(page_data)} registros extraídos")
                else:
                    logger.warning(f"No se encontraron datos en la página {page_num}")
                
                # Verificar si hay más páginas disponibles
                if page_num < max_pages:
                    if not navigate_to_next_page(driver, page_num):
                        logger.info(f"No hay más páginas disponibles después de la página {page_num}")
                        break
                
            except Exception as e:
                logger.error(f"Error al extraer página {page_num}: {e}")
                break
        
        # Crear DataFrame con todos los datos
        if all_data and table_headers:
            logger.info(f"Total de registros extraídos: {len(all_data)}")
            
            # Normalizar filas
            max_cols = len(table_headers)
            normalized_rows = []
            
            for row in all_data:
                if len(row) > max_cols:
                    normalized_row = row[:max_cols]
                else:
                    normalized_row = row + [''] * (max_cols - len(row))
                normalized_rows.append(normalized_row)
            
            df = pl.DataFrame(normalized_rows, schema=table_headers)
            return clean_and_convert_data(df)
        else:
            logger.warning("No se pudieron extraer datos de ninguna página")
            return pl.DataFrame()
            
    except Exception as e:
        logger.error(f"Error durante la extracción multi-página: {str(e)}")
        return pl.DataFrame()
    finally:
        if driver:
            driver.quit()


def extract_headers(driver) -> list:
    """Extrae los headers de la tabla"""
    header_elements = driver.find_elements(By.CSS_SELECTOR, ".scGridLabelFont a")
    table_headers = []
    
    for header in header_elements:
        header_text = header.text.strip()
        if header_text:
            table_headers.append(header_text)
    
    return table_headers


def extract_page_data(driver) -> list:
    """Extrae los datos de la página actual"""
    data_rows = driver.find_elements(By.CSS_SELECTOR, ".scGridFieldOdd, .scGridFieldEven")
    extracted_data = []
    
    for row in data_rows:
        cells = row.find_elements(By.CSS_SELECTOR, "td span[id^='id_sc_field_']")
        if cells:
            row_data = [cell.text.strip() for cell in cells]
            if row_data:
                extracted_data.append(row_data)
    
    return extracted_data


def navigate_to_next_page(driver, current_page: int) -> bool:
    """
    Navega a la siguiente página
    
    Args:
        driver: WebDriver instance
        current_page: Número de página actual
    
    Returns:
        True si se pudo navegar, False si no hay más páginas
    """
    try:
        next_page = current_page + 1
        
        # Buscar el enlace de la siguiente página
        next_page_links = driver.find_elements(By.CSS_SELECTOR, f"a.scGridToolbarNav[href*='nm_gp_submit_rec({current_page * 10 + 1})']")
        
        if next_page_links:
            # Hacer clic en el enlace de la siguiente página
            next_page_links[0].click()
            time.sleep(3)
            
            # Esperar a que la página se cargue
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".scGridFieldOdd, .scGridFieldEven"))
            )
            
            return True
        else:
            # Intentar usar el botón "forward"
            forward_button = driver.find_element(By.ID, "forward_bot")
            if forward_button and "disabled" not in forward_button.find_element(By.TAG_NAME, "img").get_attribute("src"):
                forward_button.click()
                time.sleep(3)
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".scGridFieldOdd, .scGridFieldEven"))
                )
                
                return True
            
            return False
    
    except Exception as e:
        logger.warning(f"No se pudo navegar a la página {next_page}: {e}")
        return False


def clean_and_convert_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Limpia y convierte los tipos de datos del DataFrame
    
    Args:
        df: DataFrame original
    
    Returns:
        DataFrame con tipos de datos corregidos
    """
    try:
        # Limpiar datos numéricos (remover comas de miles)
        numeric_columns = ['Salario', 'Gastos', 'Sobre sueldo', 'Total']
        
        for col in numeric_columns:
            if col in df.columns:
                df = df.with_columns(
                    pl.col(col).str.replace_all(",", "").cast(pl.Float64, strict=False).alias(col)
                )
        
        # Convertir Identificacion/Posicion a entero si es posible
        if 'Identificacion / Posicion' in df.columns:
            df = df.with_columns(
                pl.col('Identificacion / Posicion').cast(pl.Int64, strict=False)
            )
        
        logger.info("Datos limpiados y tipos convertidos exitosamente")
        return df
        
    except Exception as e:
        logger.warning(f"Error al limpiar datos: {str(e)}")
        return df


def extract(url: str, headers: dict = None) -> pl.DataFrame:
    """
    Extrae datos de una tabla HTML de empleados desde una URL
    
    Args:
        url: URL del sitio web
        headers: Diccionario con los nombres de las columnas y sus tipos (opcional)
    
    Returns:
        DataFrame de Polars con los datos extraídos
    """
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info(f"Navegando a: {url}")
        driver.get(url)
        
        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".scGridLabelFont, table"))
        )
        
        # Esperar un poco más para que AJAX termine de cargar
        time.sleep(3)
        
        # Intentar extraer con el nuevo método (para la estructura específica de CSS)
        try:
            return extract_css_table_structure(driver)
        except Exception as e:
            logger.warning(f"Método específico de CSS falló: {e}")
            # Fallback al método original
            return extract_generic_table_structure(driver, headers)
            
    except TimeoutException:
        logger.error("Timeout: La página no se cargó en el tiempo esperado")
        return pl.DataFrame()
    except Exception as e:
        logger.error(f"Error durante la extracción: {str(e)}")
        return pl.DataFrame()
    finally:
        if driver:
            driver.quit()


def extract_css_table_structure(driver) -> pl.DataFrame:
    """
    Extrae datos usando la estructura específica del sitio CSS
    """
    # Extraer headers
    header_elements = driver.find_elements(By.CSS_SELECTOR, ".scGridLabelFont a")
    table_headers = []
    
    for header in header_elements:
        header_text = header.text.strip()
        if header_text:
            table_headers.append(header_text)
    
    logger.info(f"Headers encontrados: {table_headers}")
    
    # Extraer filas de datos
    data_rows = driver.find_elements(By.CSS_SELECTOR, ".scGridFieldOdd, .scGridFieldEven")
    
    if not data_rows:
        raise Exception("No se encontraron filas de datos con estructura CSS")
    
    extracted_data = []
    
    for i, row in enumerate(data_rows, 1):
        # Encontrar celdas de datos (excluyendo botones)
        cells = row.find_elements(By.CSS_SELECTOR, "td span[id^='id_sc_field_']")
        
        if cells:
            row_data = [cell.text.strip() for cell in cells]
            if row_data:
                extracted_data.append(row_data)
                logger.debug(f"Fila {i}: {row_data}")
    
    # Crear DataFrame
    if extracted_data and table_headers:
        max_cols = len(table_headers)
        normalized_rows = []
        
        for row in extracted_data:
            if len(row) > max_cols:
                normalized_row = row[:max_cols]
            else:
                normalized_row = row + [''] * (max_cols - len(row))
            normalized_rows.append(normalized_row)
        
        df = pl.DataFrame(normalized_rows, schema=table_headers)
        return clean_and_convert_data(df)
    
    raise Exception("No se pudieron crear datos válidos")


def extract_generic_table_structure(driver, headers: dict = None) -> pl.DataFrame:
    """
    Método fallback para extraer datos de tablas HTML genéricas
    """
    # Buscar la tabla
    table = driver.find_element(By.TAG_NAME, "table")
    
    # Extraer headers de la tabla
    header_elements = table.find_elements(By.CSS_SELECTOR, "thead tr th, tr th")
    table_headers = [th.text.strip() for th in header_elements if th.text.strip()]
    
    if not table_headers:
        # Si no hay headers en th, buscar en la primera fila
        first_row = table.find_element(By.CSS_SELECTOR, "tr")
        header_elements = first_row.find_elements(By.TAG_NAME, "td")
        table_headers = [th.text.strip() for th in header_elements if th.text.strip()]
    
    logger.info(f"Headers encontrados (método genérico): {table_headers}")
    
    # Extraer filas de datos
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr, tr")
    
    if not rows:
        return pl.DataFrame()
    
    # Extraer datos de cada fila
    data_rows = []
    for row in rows[1:]:  # Saltar la primera fila si contiene headers
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            row_data = [cell.text.strip() for cell in cells]
            data_rows.append(row_data)
    
    logger.info(f"Se extrajeron {len(data_rows)} filas de datos")
    
    # Crear DataFrame con los datos extraídos
    if data_rows and table_headers:
        max_cols = max(len(row) for row in data_rows)
        normalized_rows = []
        for row in data_rows:
            normalized_row = row + [''] * (max_cols - len(row))
            normalized_rows.append(normalized_row[:max_cols])
        
        df = pl.DataFrame(normalized_rows, schema=[f"col_{i}" for i in range(max_cols)])
        
        # Asignar nombres de columnas si están disponibles
        if len(table_headers) == max_cols:
            column_mapping = {f"col_{i}": header for i, header in enumerate(table_headers)}
            df = df.rename(column_mapping)
        
        return df
    
    return pl.DataFrame()



# ------------------------------------ CONFIGURACIÓN ------------------

# Headers esperados (mantenido por compatibilidad)
headers = {
    "Identificacion / Posicion": {"type": "number"},
    "Cédula": {"type": "string"},
    "Nombre completo": {"type": "string"},
    "Cargo": {"type": "string"},
    "Departamento": {"type": "string"},
    "Estatus": {"type": "string"},
    "Inicio Planilla": {"type": "string"},
    "Salario": {"type": "number"},
    "Gastos": {"type": "number"},
    "Sobre sueldo": {"type": "number"},
    "Total": {"type": "number"},
    "Objeto De Gasto": {"type": "string"}
}


def save_data(df: pl.DataFrame, base_filename: str = "employees_data"):
    """
    Guarda el DataFrame en múltiples formatos
    
    Args:
        df: DataFrame de Polars
        base_filename: Nombre base para los archivos
    """
    if df.is_empty():
        logger.warning("No hay datos para guardar")
        return
    
    try:
        # Guardar en CSV
        csv_file = f"{base_filename}.csv"
        df.write_csv(csv_file)
        logger.info(f"Datos guardados en CSV: {csv_file}")
        
        
        # Guardar en Parquet para mejor rendimiento
        parquet_file = f"{base_filename}.parquet"
        df.write_parquet(parquet_file)
        logger.info(f"Datos guardados en Parquet: {parquet_file}")
        
    except Exception as e:
        logger.error(f"Error al guardar datos: {e}")


def scrape_with_config(url: str, config: dict = None) -> pl.DataFrame:
    """
    Función principal de scraping con configuración personalizada
    
    Args:
        url: URL del sitio web
        config: Diccionario con configuración {
            'records_per_page': 50,
            'max_pages': 10,
            'headless': True,
            'wait_time': 3
        }
    
    Returns:
        DataFrame de Polars con los datos extraídos
    """
    # Configuración por defecto
    default_config = {
        'records_per_page': 50,
        'max_pages': 10,
        'headless': True,
        'wait_time': 3
    }
    
    if config:
        default_config.update(config)
    
    logger.info(f"Iniciando scraping con configuración: {default_config}")
    
    # Usar la función de múltiples páginas
    return extract_all_pages(
        url=url,
        records_per_page=default_config['records_per_page'],
        max_pages=default_config['max_pages']
    )


def print_data_summary(df: pl.DataFrame):
    """
    Imprime un resumen de los datos extraídos
    
    Args:
        df: DataFrame de Polars
    """
    if df.is_empty():
        print("No hay datos para mostrar")
        return
    
    print("\n=== INFORMACIÓN DEL DATASET ===")
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")
    print(f"\nColumnas disponibles: {df.columns}")
    
    # Mostrar primeras filas
    print("\n=== PRIMERAS 5 FILAS ===")
    print(df.head())
    
    # Mostrar estadísticas de columnas numéricas
    numeric_columns = [col for col in df.columns 
                      if df[col].dtype in [pl.Float64, pl.Int64]]
    
    if numeric_columns:
        print(f"\n=== ESTADÍSTICAS DE COLUMNAS NUMÉRICAS ===")
        for col in numeric_columns:
            try:
                stats = df[col].describe()
                print(f"\n{col}:")
                print(stats)
            except Exception as e:
                logger.warning(f"No se pudieron calcular estadísticas para {col}: {e}")


# ------------------------------------ EJEMPLO DE USO ------------------

if __name__ == "__main__":
   
   
    # Opción 1: Extraer desde URL con múltiples páginas 
    url = "https://transparencia.css.gob.pa/planilla/grid_defensoria/"
    
    #Extraer de múltiples páginas con 50 registros por página
    logger.info("=== EXTRAYENDO DATOS DESDE URL - MÚLTIPLES PÁGINAS ===")
    all_employees_data = extract_all_pages(
        url=url, 
        records_per_page=10,  # Cambiar a 50 registros por página
        max_pages=10          # Extraer hasta 10 páginas
    )
    
    if not all_employees_data.is_empty():
        logger.info(f"Extracción exitosa desde URL - múltiples páginas")
        print_data_summary(all_employees_data)
        save_data(all_employees_data, "employees_data_all_pages")
    else:
        logger.error("No se pudieron extraer datos de la URL")
    
    