class ErrorRendimientoEstudiantil(Exception):
    """Clase base para todas las excepciones personalizadas del proyecto."""
    pass

class ErrorValidacionDatos(ErrorRendimientoEstudiantil):
    """Excepcion lanzada cuando la validacion de los datos de entrada falla."""
    pass

class ErrorModeloNoEntrenado(ErrorRendimientoEstudiantil):
    """Excepcion lanzada cuando se intenta predecir o evaluar un modelo sin haberlo entrenado."""
    pass

class ErrorConfiguracion(ErrorRendimientoEstudiantil):
    """Excepcion lanzada cuando ocurre un error en la configuracion del sistema."""
    pass
