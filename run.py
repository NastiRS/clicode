import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv


def main():
    """Función principal."""
    # Cargar variables de entorno
    load_dotenv()

    # Verificar API key de Mistral
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: Variable de entorno MISTRAL_API_KEY no encontrada")
        print("💡 Crea un archivo .env con tu API key de Mistral:")
        print("   MISTRAL_API_KEY=tu_api_key_aqui")
        return 1

    try:
        from src.agent import ejecutar_agente

        ejecutar_agente()
        return 0

    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
        return 0
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
