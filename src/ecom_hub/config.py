
import os
from dotenv import load_dotenv


load_dotenv()

def _load_from_infisical() -> bool:
    """
    Attempts to pull all secrets from Infisical into os.environ.
    Returns True if successful, False if anything goes wrong.

   
    """
    client_id = os.getenv("INFISICAL_CLIENT_ID")
    client_secret = os.getenv("INFISICAL_CLIENT_SECRET")
    project_id = os.getenv("INFISICAL_PROJECT_ID")

    # If  credentials aren't present, skip Infisical silently
    if not all([client_id, client_secret, project_id]):
        print("[config] Infisical credentials not found — using .env only")
        return False

    try:
        from infisical_client import InfisicalClient, ClientSettings, AuthenticationOptions, UniversalAuthMethod, ListSecretsOptions

        client = InfisicalClient(ClientSettings(
            auth=AuthenticationOptions(
                universal_auth=UniversalAuthMethod(
                    client_id=client_id,
                    client_secret=client_secret,
                )
            )
        ))

        # Determine environment based on APP_ENV
        env = os.getenv("APP_ENV", "development")
        infisical_env = {
            "development": "dev",
            "staging": "staging",
            "production": "prod",
        }.get(env, "dev")

        # Fetch all secrets for this environment
        secrets = client.listSecrets(ListSecretsOptions(
            project_id=project_id,
            environment=infisical_env,
            path="/",
        ))

        # Inject each secret into os.environ
        # This means existing .env values are OVERRIDDEN by Infisical
        # Infisical is the source of truth
        injected = 0
        for secret in secrets:
            os.environ[secret.secret_key] = secret.secret_value
            injected += 1

        print(f"[config] Loaded {injected} secrets from Infisical ({infisical_env})")
        return True

    except Exception as e:
        print(f"[config] Infisical failed: {e}")
        print("[config] Falling back to .env")
        return False


# This runs once when config.py is first imported
_loaded_from_infisical = _load_from_infisical()

# ── Now read from os.environ (works regardless of source) ──────────────────

# Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# App
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Infisical bootstrap (these stay in .env, never in Infisical itself)
INFISICAL_CLIENT_ID = os.getenv("INFISICAL_CLIENT_ID")
INFISICAL_CLIENT_SECRET = os.getenv("INFISICAL_CLIENT_SECRET")
INFISICAL_PROJECT_ID = os.getenv("INFISICAL_PROJECT_ID")


def validate_required_secrets():
    """
    Call this at app startup.
    Fails loudly if any critical secret is missing.
    Better to crash at boot than fail mysteriously mid-request.
    """
    required = {
        "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
        "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
        "AZURE_OPENAI_API_VERSION": AZURE_OPENAI_API_VERSION,
        "AZURE_OPENAI_DEPLOYMENT_NAME": AZURE_OPENAI_DEPLOYMENT_NAME,
    }

    missing = [k for k, v in required.items() if not v]

    if missing:
        raise RuntimeError(
            f"Missing required secrets: {', '.join(missing)}\n"
            f"Source: {'Infisical' if _loaded_from_infisical else '.env file'}"
        )

    print(f"[config] All required secrets present ✅")
    print(f"[config] Source: {'Infisical' if _loaded_from_infisical else '.env file'}")