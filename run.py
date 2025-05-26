import sys


def main():
    try:
        from src.agent import run_agent

        run_agent()
        return 0

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
