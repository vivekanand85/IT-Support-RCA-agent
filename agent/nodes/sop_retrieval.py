import os
import math
from openai import OpenAI
from dotenv import load_dotenv
from agent.state import AgentState

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DOCS_PATH = os.path.join(os.path.dirname(__file__), "../../knowledge_base/docs")
EMBED_MODEL = "text-embedding-3-small"

# ---------------------------------------------------------------
# WHY THIS REPLACES CHROMADB:
# ChromaDB depends on onnxruntime + numpy native binaries that are
# crashing on this machine (Windows/Anaconda DLL conflict).
# We do the same underlying mechanics ourselves - call OpenAI to
# get embeddings, then compare them with cosine similarity by hand.
# Same technique, just visible instead of hidden inside a library.
# ---------------------------------------------------------------

def get_embedding(text: str) -> list[float]:
    """Convert text into a list of numbers that capture its meaning."""
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    How close two vectors point in the same direction.
    1.0 = same meaning, 0 = unrelated. No numpy needed - just math.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product / (mag_a * mag_b)


# Built once, when this module is first imported - not on every request
_runbook_index = []  # list of (filename, content, embedding)

def _build_index():
    for filename in os.listdir(DOCS_PATH):
        if filename.endswith(".txt"):
            with open(os.path.join(DOCS_PATH, filename), "r") as f:
                content = f.read()
            embedding = get_embedding(content)
            _runbook_index.append((filename, content, embedding))
    print(f"[SOP_RETRIEVAL] Indexed {len(_runbook_index)} runbooks (in-memory)")

_build_index()


def sop_retrieval_node(state: AgentState) -> AgentState:
    query_embedding = get_embedding(state.raw_issue_text)

    best_score = -1.0
    best_content = ""

    for filename, content, embedding in _runbook_index:
        score = cosine_similarity(query_embedding, embedding)
        if score > best_score:
            best_score = score
            best_content = content

    if best_score > 0.2:
        state.sop_found = True
        state.sop_content = best_content
    else:
        state.sop_found = False
        state.sop_content = ""

    return state