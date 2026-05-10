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
    """Seed multiple CA-focused prompts into the `prompts` collection.

    We seed at startup so deployments have multiple specialized templates.
    The check is idempotent to avoid duplicate inserts across restarts.
    """
    ca_prompts = [
        {
            "_id": "Education_Prompt",
            "template": "You are an expert in CA Final education. Answer the following question concisely and accurately: {{userInput}}",
            "keywords": ["general", "default"],
        },
        {
            "_id": "CA_Scoring_Prompt",
            "template": "You are a CA Final scoring expert. Focus on pass criteria, marks, and scoring rules. Answer: {{userInput}}",
            "keywords": ["score", "pass", "marks", "criteria", "aggregate", "percentage"],
        },
        {
            "_id": "CA_Syllabus_Prompt",
            "template": "You are a CA Final syllabus expert. Focus on subjects, groups, topics, and course structure. Answer: {{userInput}}",
            "keywords": ["subject", "group", "syllabus", "topics", "chapter", "paper", "group 1", "group 2"],
        },
        {
            "_id": "CA_Exam_Strategy_Prompt",
            "template": "You are a CA Final exam strategy expert. Focus on attempt strategies, preparation tips, and time management. Answer: {{userInput}}",
            "keywords": ["attempt", "strategy", "prepare", "tips", "study", "revision", "time management", "exam"],
        },
        {
            "_id": "CA_Exemption_Prompt",
            "template": "You are a CA Final exemption expert. Focus on subject exemptions, validity, and re-examination rules. Answer: {{userInput}}",
            "keywords": ["exemption", "exempt", "validity", "re-exam", "re-attempt"],
        },
    ]
    
    try:
        for prompt_doc in ca_prompts:
            existing = prompts_col.find_one({"_id": prompt_doc["_id"]})
            if not existing:
                prompts_col.insert_one(prompt_doc)
    except PyMongoError as e:
        # If seeding fails (e.g., no Mongo available), log a warning and
        # continue. This avoids crashing the entire app at startup while
        # still attempting the seed as required.
        print(f"Warning: failed to seed prompts collection: {e}")


# Seed on import so the collection is ready for requests.
seed_prompts()
