import os
import platform
import subprocess
from pathlib import Path

from agno.tools import tool


@tool()
def ejecutar_comando(comando: str) -> str:
    """Ejecuta un comando del sistema.

    Args:
        comando: El comando a ejecutar

    Returns:
        La salida del comando o mensaje de error
    """
    try:
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = f"Comando: {comando}\n"
        output += f"Código de salida: {result.returncode}\n"

        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        return output

    except subprocess.TimeoutExpired:
        return f"⏰ El comando '{comando}' excedió el tiempo límite de 2 minutos"
    except Exception as e:
        return f"❌ Error al ejecutar '{comando}': {str(e)}"


@tool()
def obtener_directorio_actual() -> str:
    """Obtiene el directorio de trabajo actual.

    Returns:
        La ruta del directorio actual
    """
    try:
        directorio = os.getcwd()
        return f"📁 Directorio actual: {directorio}"
    except Exception as e:
        return f"❌ Error al obtener directorio: {str(e)}"


@tool()
def cambiar_directorio(ruta: str) -> str:
    """Cambia el directorio de trabajo.

    Args:
        ruta: La ruta del nuevo directorio

    Returns:
        Confirmación del cambio o mensaje de error
    """
    try:
        ruta_path = Path(ruta)
        if not ruta_path.exists():
            return f"❌ La ruta no existe: {ruta}"

        if not ruta_path.is_dir():
            return f"❌ La ruta no es un directorio: {ruta}"

        os.chdir(ruta)
        nuevo_directorio = os.getcwd()
        return f"✅ Directorio cambiado a: {nuevo_directorio}"

    except Exception as e:
        return f"❌ Error al cambiar directorio: {str(e)}"


@tool()
def obtener_info_sistema() -> str:
    """Obtiene información del sistema.

    Returns:
        Información detallada del sistema
    """
    try:
        info = {
            "Sistema": platform.system(),
            "Versión": platform.version(),
            "Arquitectura": platform.architecture()[0],
            "Procesador": platform.processor(),
            "Nombre del equipo": platform.node(),
            "Usuario": os.getenv("USERNAME") or os.getenv("USER", "Desconocido"),
            "Python": platform.python_version(),
            "Directorio actual": os.getcwd(),
        }

        resultado = "🖥️ Información del sistema:\n"
        for clave, valor in info.items():
            resultado += f"  • {clave}: {valor}\n"

        return resultado

    except Exception as e:
        return f"❌ Error al obtener información del sistema: {str(e)}"
