import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./rulees_test.sqlite"
os.environ.setdefault("SECRET_KEY", "test-secret")

# Testes precisam ser deterministicos e nao podem depender de credenciais reais
# configuradas no .env local do desenvolvedor (ex.: LLM_PROVIDER=gemini). Forca
# os providers para os valores locais/deterministicos independente do .env.
os.environ["LLM_PROVIDER"] = "heuristic"
os.environ["EMBEDDING_PROVIDER"] = "deterministic"
os.environ["STT_PROVIDER"] = "mock"

test_db = Path("rulees_test.sqlite")
if test_db.exists():
    test_db.unlink()
