from pymongo import MongoClient
from pymongo.errors import PyMongoError
import certifi
import config

# Connect to MongoDB using the URI from config. We pass an explicit CA bundle
# so Atlas TLS validation does not depend on OS cert store quirks.
# A shorter server selection timeout helps fail fast with clearer errors.
client = MongoClient(
    config.CONFIG["MONGO_URI"],
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000,
)
# Use a specific default database name when none is provided in the URI.
# This avoids ConfigurationError when the connection string lacks a database.
db = client.get_database("flask_ai_api_db")

# Trigger an early connection check so TLS/network issues are detected at startup.
try:
    client.admin.command("ping")
except PyMongoError as e:
    print(f"Warning: MongoDB connection check failed: {e}")

prompts_col = db.get_collection("prompts")
history_col = db.get_collection("history")


def seed_prompts():
    """Ensure the Education_Prompt exists in the `prompts` collection.

    We seed at startup so deployments have a sensible default prompt.
    The check is idempotent to avoid duplicate inserts across restarts.
    """
    try:
        existing = prompts_col.find_one({"_id": "Education_Prompt"})
        if not existing:
            prompts_col.insert_one({
                "_id": "Education_Prompt",
                "template": "You are an expert in education domain. Answer the following: {{userInput}}",
            })
    except PyMongoError as e:
        # If seeding fails (e.g., no Mongo available), log a warning and
        # continue. This avoids crashing the entire app at startup while
        # still attempting the seed as required.
        print(f"Warning: failed to seed prompts collection: {e}")


# Seed on import so the collection is ready for requests.
seed_prompts()
