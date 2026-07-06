import os
import urllib.request
import zipfile
import pandas as pd

def descargar_y_validar_datos():
    directorio_datos = "datos"
    os.makedirs(directorio_datos, exist_ok=True)
    ruta_salida = os.path.join(directorio_datos, "datos_estudiantes.csv")
    
    # URL alternativa de GitHub (ya descomprimido) y URL oficial de UCI (zip)
    url_github = "https://raw.githubusercontent.com/ranga4all1/student-dropout-and-success-prediction/main/data/dataset.csv"
    url_uci = "https://archive.ics.uci.edu/static/public/697/predict+students+dropout+and+academic+success.zip"
    
    print("Intentando descargar desde GitHub...")
    try:
        urllib.request.urlretrieve(url_github, ruta_salida)
        print("Descargado con éxito de GitHub.")
    except Exception as error_github:
        print(f"Error al descargar de GitHub: {error_github}")
        print("Intentando descargar desde UCI Repository...")
        ruta_zip = os.path.join(directorio_datos, "temporal.zip")
        try:
            urllib.request.urlretrieve(url_uci, ruta_zip)
            with zipfile.ZipFile(ruta_zip, 'r') as referencia_zip:
                # El archivo dentro del zip se llama dataset.csv
                referencia_zip.extractall(directorio_datos)
            
            # Renombrar dataset.csv a datos_estudiantes.csv si es necesario
            ruta_extraida = os.path.join(directorio_datos, "dataset.csv")
            if os.path.exists(ruta_extraida):
                if os.path.exists(ruta_salida):
                    os.remove(ruta_salida)
                os.rename(ruta_extraida, ruta_salida)
            
            # Limpiar zip temporal
            os.remove(ruta_zip)
            print("Descargado y descomprimido con éxito desde UCI.")
        except Exception as error_uci:
            print(f"Error crítico al descargar desde UCI: {error_uci}")
            raise error_uci

    # Validar la lectura de los datos
    if os.path.exists(ruta_salida):
        # Intentar leer con delimitador ';' (UCI estándar) o ','
        try:
            datos = pd.read_csv(ruta_salida, sep=';')
            if len(datos.columns) <= 1:
                datos = pd.read_csv(ruta_salida, sep=',')
            
            print(f"Datos cargados exitosamente.")
            print(f"Número de registros: {datos.shape[0]}")
            print(f"Número de columnas: {datos.shape[1]}")
            print("Columnas encontradas:")
            print(list(datos.columns))
            
            # Asegurarse de que el archivo final tenga delimitador ';' para consistencia
            datos.to_csv(ruta_salida, sep=';', index=False)
            print("Datos validados y guardados con delimitador ';'.")
        except Exception as error_lectura:
            print(f"Error al leer y validar el archivo CSV: {error_lectura}")
            raise error_lectura
    else:
        raise FileNotFoundError("No se encontró el archivo de datos final.")

if __name__ == "__main__":
    descargar_y_validar_datos()
