import re
from functools import lru_cache

TOKEN_PATTERN = re.compile(r"\w+")


@lru_cache(maxsize=2048)
def tokenize(
    text: str,
) -> tuple[str, ...]:

    return tuple(
        token.lower()
        for token in TOKEN_PATTERN.findall(text)
    )