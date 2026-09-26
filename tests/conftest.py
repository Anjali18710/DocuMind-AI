"""
Shared test fixtures. Tests run offline: the real embedding model is replaced
by a deterministic fake one and the LLM by a scripted fake, so no API keys or
model downloads are needed.
"""

import sys
from pathlib import Path

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SEED = ROOT / "data" / "raw"
SAMPLES = ROOT / "data" / "samples"


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch):
    import rag.vectorstore

    fake = DeterministicFakeEmbedding(size=64)
    monkeypatch.setattr(rag.vectorstore, "get_embedding_model", lambda: fake)
    return fake


@pytest.fixture
def store(tmp_path):
    from rag.storage import LocalStore

    return LocalStore(str(tmp_path / "store"))


@pytest.fixture
def seeded_store(store):
    from rag.storage import seed_if_empty

    seed_if_empty(store, str(SEED))
    return store


@pytest.fixture
def retriever(seeded_store):
    from rag.knowledge_base import build_retriever

    return build_retriever(seeded_store, use_cache=False)


class FakeLLM:
    """Stands in for LLMRouter: returns a fixed reply and records the prompt."""

    def __init__(self, reply):
        self.reply = reply
        self.prompts = []

    def generate(self, prompt, json_mode=False):
        self.prompts.append(prompt)
        return self.reply, "Fake · test-model"


@pytest.fixture
def fake_llm_factory():
    return FakeLLM
