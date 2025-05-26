from agno.agent.agent import Agent
from agno.models.mistral import MistralChat
from agno.storage.sqlite import SqliteStorage
from agno.memory.agent import AgentMemory
import os

from src.tools.command_tools import (
    ejecutar_comando,
    obtener_directorio_actual,
    cambiar_directorio,
    obtener_info_sistema,
)
from src.tools.file_tools import (
    leer_archivo,
    escribir_archivo,
    eliminar_archivo,
    listar_archivos,
    buscar_archivos,
)


def crear_agente_codificador():
    """Crea y configura el agente asistente codificador."""

    db_file = "tmp/agent.db"

    os.makedirs("tmp", exist_ok=True)

    memory = AgentMemory()

    storage = SqliteStorage(table_name="agent_sessions", db_file=db_file)

    agente = Agent(
        name="AsistenteCodificador",
        model=MistralChat(id="devstral-small-2505"),
        description="Soy un asistente codificador experto que puede ayudarte con tareas de programación, manejo de archivos y ejecución de comandos.",
        instructions=[
            "Eres un asistente de programación experto y útil.",
            "Puedes leer, escribir y manipular archivos libremente.",
            "Puedes ejecutar comandos del sistema y código Python sin restricciones.",
            "Eres autónomo y puedes tomar decisiones técnicas por tu cuenta.",
            "Usa las herramientas disponibles para ayudar al usuario de manera eficiente.",
            "Responde siempre en español.",
            "Sé preciso, detallado y proactivo en tus acciones.",
            "Si necesitas crear directorios, archivos o ejecutar comandos, hazlo directamente.",
            "Cuando uses herramientas, explica brevemente qué estás haciendo.",
        ],
        tools=[
            leer_archivo,
            escribir_archivo,
            eliminar_archivo,
            listar_archivos,
            buscar_archivos,
            ejecutar_comando,
            obtener_directorio_actual,
            cambiar_directorio,
            obtener_info_sistema,
        ],
        storage=storage,
        add_history_to_messages=True,
        num_history_runs=3,
        show_tool_calls=True,
        markdown=True,
        memory=memory,
    )

    return agente


def ejecutar_agente():
    """Ejecuta el agente usando el CLI nativo de Agno."""
    print("🤖 Agente Asistente Codificador - Modo Autónomo")
    print("💡 Usa 'exit', 'quit' o 'bye' para salir")
    print("🚀 El agente puede ejecutar comandos libremente")
    print("📁 Historial de chat guardado automáticamente")
    print("=" * 50)

    agente = crear_agente_codificador()

    agente.new_session()

    # Mostrar información de sesión
    print(f"🔗 ID de sesión: {agente.session_id}")
    print()

    # Usar el CLI nativo de Agno con configuración en español
    agente.cli_app(
        user="Usuario",
        emoji="👤",
        stream=True,
        markdown=True,
        exit_on=["exit", "quit", "bye", "salir"],
    )

    print("\n👋 ¡Hasta luego!")
    print(f"💾 Historial guardado en sesión: {agente.session_id}")


if __name__ == "__main__":
    ejecutar_agente()
