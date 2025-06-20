from agno.agent.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.storage.sqlite import SqliteStorage
from agno.memory.agent import AgentMemory
from agno.tools.reasoning import ReasoningTools
from agno.tools.github import GithubTools
from agno.tools.exa import ExaTools

from .agent_settings import settings
from .agent_system_instructions import instructions
from .security.exa_domains import get_official_domains


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
from .tools.project_tools import (
    get_project_structure,
    detect_dependency_manager,
)


def create_coding_agent():
    storage = SqliteStorage(table_name="agent_sessions", db_file=settings.DATABASE_PATH)

    tools = [
        get_project_structure,
        detect_dependency_manager,
        ReasoningTools(add_few_shot=True, add_instructions=True),
        read_file,
        write_file,
        delete_file,
        list_files,
        search_files,
        replace_in_file,
        execute_command,
        get_current_directory,
        change_directory,
    ]

    if settings.GITHUB_ACCESS_TOKEN:
        tools.append(
            GithubTools(
                access_token=settings.GITHUB_ACCESS_TOKEN,
                get_repository=True,
                search_repositories=True,
                create_repository=True,
                get_pull_request=True,
                get_pull_request_changes=True,
                delete_repository=True,
                list_branches=True,
                get_file_content=True,
                get_directory_content=True,
                get_branch_content=True,
                create_branch=True,
                search_code=True,
                create_pull_request=True,
            )
        )
    if settings.EXA_API_KEY:
        tools.append(
            ExaTools(
                api_key=settings.EXA_API_KEY,
                search=True,
                get_contents=True,
                find_similar=True,
                answer=True,
                text=True,
                text_length_limit=2000,
                highlights=True,
                num_results=8,
                use_autoprompt=True,
                include_domains=get_official_domains(),
                show_results=False,
                model="exa-pro",
            )
        )

    agent = Agent(
        name="Coding Assistant",
        model=OpenRouter(
            id=settings.OPENROUTER_MODEL, api_key=settings.OPENROUTER_API_KEY
        ),
        description="I am an expert coding assistant that can help you with programming tasks, file management, and command execution. I should also assist with programming tasks by following best practices, clean code, good folder structure, dependency isolation, repository pattern, etc.",
        instructions=instructions,
        tools=tools,
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
        exit_on=["bye"],
    )
