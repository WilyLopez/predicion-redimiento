import time
import functools
import logging
from src.excepciones import ErrorRendimientoEstudiantil

# Configurar el registro de logs basico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def medir_tiempo(funcion):
    """Decorador para medir el tiempo de ejecucion de una funcion."""
    @functools.wraps(funcion)
    def envoltura(*args, **kwargs):
        tiempo_inicio = time.time()
        resultado = funcion(*args, **kwargs)
        tiempo_fin = time.time()
        duracion = tiempo_fin - tiempo_inicio
        logging.info(f"Funcion {funcion.__name__} ejecutada en {duracion:.4f} segundos.")
        return resultado
    return envoltura

def capturar_errores(funcion):
    """Decorador para capturar errores, registrarlos en logs y relanzarlos de forma limpia."""
    @functools.wraps(funcion)
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except ErrorRendimientoEstudiantil as error_personalizado:
            logging.error(f"Error controlado en {funcion.__name__}: {str(error_personalizado)}")
            raise error_personalizado
        except Exception as error_inesperado:
            logging.error(f"Error inesperado en {funcion.__name__}: {str(error_inesperado)}")
            raise ErrorRendimientoEstudiantil(f"Fallo en {funcion.__name__}: {str(error_inesperado)}") from error_inesperado
    return envoltura
