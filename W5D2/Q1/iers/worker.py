import logging, base64, json
from .config import settings
from .vector_index import VectorIndex
from .gmail_client import GmailClient
from .chroma_store import ChromaStore
from .template_engine import TemplateRenderer
from .embeddings import embed
import redis
from openai import OpenAI
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

CACHE_PREFIX = "iers:policy:"  # cache key prefix

@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3))
def _generate_response(email_body: str, context: str) -> str:
    prompt = f"""You are an AI assistant. Use the provided policy context to reply.

Policy context:\n{context}\n\nEmail:\n{email_body}\n\nResponse:"""
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )
    return completion.choices[0].message.content.strip()

def _get_policy_context(query: str, index: VectorIndex):
    cache_key = CACHE_PREFIX + query.strip().lower()[:128]
    cached = redis_client.get(cache_key)
    if cached:
        return cached
    results = index.search(query, k=5)
    context = "\n\n".join(r[0] for r in results)
    redis_client.set(cache_key, context, ex=3600)  # 1-hour TTL
    return context

def process_batch():
    store = ChromaStore()
    gmail = GmailClient(settings.GOOGLE_CREDENTIALS_FILE)
    renderer = TemplateRenderer()
    messages = gmail.fetch_unread(settings.BATCH_SIZE)
    for msg in messages:
        msg_id = msg["id"]
        payload = msg["payload"]
        headers = payload["headers"]
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        body = ""
        if payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
# Determine department from email content
        def _infer_dept(text: str) -> str | None:
            lower = text.lower()
            for dept, keywords in settings.DEPT_KEYWORDS.items():
                if any(kw in lower for kw in keywords):
                    return dept
            return None

        dept = _infer_dept(subject + " " + body)
        filters = {"department": dept} if dept else None

        search_results = store.similarity_search(body, k=5, filters=filters)
        context = "\n\n".join(doc for doc, _dist, _meta in search_results)
        raw_reply = _generate_response(body, context)
        formatted_reply = renderer.render(body=raw_reply)
        gmail.send_message(sender, f"Re: {subject}", formatted_reply)
        gmail.mark_as_read(msg_id)
        logger.info("Replied to %s", msg_id) 