import hashlib

def text_hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def is_duplicate(new_hash: str, seen_hashes: set) -> bool:
    return new_hash in seen_hashes
