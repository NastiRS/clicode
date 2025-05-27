import sys
import argparse
from .agent import run_agent


def main():
    """Main function that runs when the clicode command is called"""
    parser = argparse.ArgumentParser(
        description="Clicode - Coding assistant agent using Agno", prog="clicode"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat subcommand
    subparsers.add_parser("chat", help="Start chat session with the agent")

    # If no subcommand is provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()

    try:
        if args.command == "chat":
            print("🤖 Starting Clicode Assistant...")
            print("💡 Type 'exit', 'quit', 'bye' or 'salir' to terminate")
            print("-" * 50)
            run_agent()
            return 0
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n👋 See you later!")
        return 0
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
