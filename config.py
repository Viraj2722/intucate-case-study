from dotenv import load_dotenv
import os

# Load environment variables from a .env file located next to this module.
# When the app is started from a parent directory, relying on the current
# working directory can miss the project's .env; loading from this file's
# directory makes behavior consistent regardless of the working directory.
base_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)


def get_config():
    """Load and validate required configuration from environment.

    Raises:
        EnvironmentError: if a required variable is missing.

    Returns:
        dict: keys `GEMINI_API_KEY` and `MONGO_URI`.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    mongo_uri = os.getenv("MONGO_URI")

    missing = []
    if not mongo_uri:
        missing.append("MONGO_URI")

    if missing:
        # Fail fast with clear message so running processes know what's wrong.
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    return {"GEMINI_API_KEY": gemini_key, "MONGO_URI": mongo_uri}


# Provide module-level config for convenience when imported.
CONFIG = get_config()
