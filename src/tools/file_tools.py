import os
import shutil
from pathlib import Path
from typing import Optional

from agno.tools import tool


@tool()
def leer_archivo(ruta: str) -> str:
    """Lee el contenido completo de un archivo.

    Args:
        ruta: Ruta del archivo a leer

    Returns:
        Contenido del archivo como string
    """
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: El archivo '{ruta}' no existe."
    except Exception as e:
        return f"Error al leer el archivo: {str(e)}"


@tool()
def escribir_archivo(ruta: str, contenido: str, sobrescribir: bool = True) -> str:
    """Crea o edita un archivo con el contenido especificado.

    Args:
        ruta: Ruta del archivo a crear/editar
        contenido: Contenido a escribir en el archivo
        sobrescribir: Si True, sobrescribe el archivo existente

    Returns:
        Mensaje de confirmación
    """
    try:
        # Crear directorios padre si no existen
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)

        if not sobrescribir and os.path.exists(ruta):
            return (
                f"Error: El archivo '{ruta}' ya existe y sobrescribir está desactivado."
            )

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Archivo '{ruta}' {'creado' if not os.path.exists(ruta) else 'actualizado'} exitosamente."
    except Exception as e:
        return f"Error al escribir el archivo: {str(e)}"


@tool()
def eliminar_archivo(ruta: str) -> str:
    """Elimina un archivo o directorio.

    Args:
        ruta: Ruta del archivo o directorio a eliminar

    Returns:
        Mensaje de confirmación
    """
    try:
        if os.path.isfile(ruta):
            os.remove(ruta)
            return f"Archivo '{ruta}' eliminado exitosamente."
        elif os.path.isdir(ruta):
            shutil.rmtree(ruta)
            return f"Directorio '{ruta}' eliminado exitosamente."
        else:
            return f"Error: '{ruta}' no existe."
    except Exception as e:
        return f"Error al eliminar: {str(e)}"


@tool()
def listar_archivos(
    directorio: str = ".", patron: Optional[str] = None, recursivo: bool = False
) -> str:
    """Lista archivos en un directorio con opciones de filtrado.

    Args:
        directorio: Directorio a explorar (por defecto el actual)
        patron: Patrón de búsqueda (ej: "*.py", "test*")
        recursivo: Si True, busca recursivamente en subdirectorios

    Returns:
        Lista de archivos encontrados
    """
    try:
        path = Path(directorio)
        if not path.exists():
            return f"Error: El directorio '{directorio}' no existe."

        if recursivo:
            if patron:
                archivos = list(path.rglob(patron))
            else:
                archivos = list(path.rglob("*"))
        else:
            if patron:
                archivos = list(path.glob(patron))
            else:
                archivos = list(path.iterdir())

        # Separar archivos y directorios
        dirs = [f for f in archivos if f.is_dir()]
        files = [f for f in archivos if f.is_file()]

        resultado = f"Contenido de '{directorio}':\n\n"

        if dirs:
            resultado += "Directorios:\n"
            for d in sorted(dirs):
                resultado += f"  📁 {d.name}/\n"
            resultado += "\n"

        if files:
            resultado += "Archivos:\n"
            for f in sorted(files):
                size = f.stat().st_size
                resultado += f"  📄 {f.name} ({size} bytes)\n"

        if not dirs and not files:
            resultado += "No se encontraron archivos o directorios."

        return resultado
    except Exception as e:
        return f"Error al listar archivos: {str(e)}"


@tool()
def buscar_archivos(nombre: str, directorio: str = ".", recursivo: bool = True) -> str:
    """Busca archivos por nombre de forma inteligente.

    Args:
        nombre: Nombre o patrón del archivo a buscar
        directorio: Directorio donde buscar
        recursivo: Si True, busca en subdirectorios

    Returns:
        Lista de archivos encontrados con sus rutas
    """
    try:
        path = Path(directorio)
        if not path.exists():
            return f"Error: El directorio '{directorio}' no existe."

        # Buscar con diferentes patrones
        patrones = [
            f"*{nombre}*",  # Contiene el nombre
            f"{nombre}*",  # Empieza con el nombre
            f"*{nombre}",  # Termina con el nombre
            nombre,  # Nombre exacto
        ]

        archivos_encontrados = set()

        for patron in patrones:
            if recursivo:
                matches = path.rglob(patron)
            else:
                matches = path.glob(patron)

            for match in matches:
                if match.is_file():
                    archivos_encontrados.add(match)

        if not archivos_encontrados:
            return f"No se encontraron archivos que coincidan con '{nombre}' en '{directorio}'."

        resultado = f"Archivos encontrados para '{nombre}':\n\n"
        for archivo in sorted(archivos_encontrados):
            size = archivo.stat().st_size
            resultado += f"📄 {archivo} ({size} bytes)\n"

        return resultado
    except Exception as e:
        return f"Error al buscar archivos: {str(e)}"
