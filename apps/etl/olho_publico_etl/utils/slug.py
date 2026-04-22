import re
import unicodedata


def slugify(value: str) -> str:
    """Lowercased, accent-free, dashed slug."""
    nfkd = unicodedata.normalize("NFD", value)
    no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", no_accents).strip("-").lower()
    return cleaned
