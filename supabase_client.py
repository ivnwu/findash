from supabase import create_client
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from .env.onadev or .env if present; in CI, env vars are injected directly
env_file = Path(__file__).parent / ".env.onadev"
if not env_file.exists():
    env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or Key not set in environment")

supabase = create_client(url, key)
