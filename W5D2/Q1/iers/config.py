import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost/iers")
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))

    # Branding / tone settings
    SIGNATURE: str = os.getenv("EMAIL_SIGNATURE", "Acme Corp Support Team")
    DISCLAIMER: str = os.getenv("EMAIL_DISCLAIMER", "This message and any attachments are confidential and intended solely for the addressee.")

    # Simple department keyword mapping for demo heuristic
    DEPT_KEYWORDS = {
        "hr": ["leave", "vacation", "payroll", "benefit", "hiring"],
        "it": ["password", "login", "email", "vpn", "laptop"],
        "finance": ["invoice", "payment", "expense", "budget"],
    }

settings = Settings() 