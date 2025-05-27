from agno.agent.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.memory.agent import AgentMemory
from agno.tools.reasoning import ReasoningTools
from .agent_settings import settings
from .agent_system_instructions_optimized import instructions


from .tools.command_tools import (
    execute_command,
    get_current_directory,
    change_directory,
)
from .tools.file_tools import (
    read_file,
    write_file,
    delete_file,
    list_files,
    search_files,
    replace_in_file,
)


def create_coding_agent():
    storage = SqliteStorage(table_name="agent_sessions", db_file=settings.DATABASE_PATH)

    agent = Agent(
        name="Coding Assistant",
        model=OpenAIChat(id=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY),
        description="I am an expert coding assistant that can help you with programming tasks, file management and command execution.",
        instructions=instructions,
        tools=[
            read_file,
            write_file,
            delete_file,
            list_files,
            search_files,
            execute_command,
            get_current_directory,
            change_directory,
            replace_in_file,
            ReasoningTools(add_few_shot=True, add_instructions=True),
        ],
        storage=storage,
        add_history_to_messages=True,
        num_history_runs=3,
        show_tool_calls=True,
        markdown=True,
        memory=AgentMemory(),
    )

    return agent


def run_agent():
    agent = create_coding_agent()

    agent.new_session()
    agent.cli_app(
        user="User",
        emoji="👤",
        stream=True,
        markdown=True,
        exit_on=["exit", "quit", "bye", "salir"],
    )
