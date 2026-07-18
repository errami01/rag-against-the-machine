import re
from functools import lru_cache


# Matches standard words
TOKEN_PATTERN = re.compile(r"\w+")
# Detects transitions in CamelCase (e.g., 'BaseModel' -> 'Base', 'Model')
CAMEL_SPLIT_PATTERN = re.compile(
    r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])'
    )
DEFAULT_STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "in", "on", "at", "to", "from", "by", "for", "with",
    "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "of", "it", "its", "they", "them", "their",
    "this", "that", "these", "those", "which", "who", "whom", "what", "as",
    "if", "when", "where", "how", "why", "can", "will", "should", "would",
    "you"
}


@lru_cache(maxsize=2048)
def tokenize(text: str, dataset_name: str = "docs") -> tuple[str, ...]:
    """Tokenizes a string into normalized, code-aware textual sub-components.

    Extracts alphanumeric text blocks and applies language-specific parsing
    rules to break down compound variable names. It splits strings matching
    snake_case and CamelCase naming conventions to ensure granular matching
    for code-heavy RAG documents.

    Args:
        text: The raw source text or code string to process.

    Returns:
        An immutable, ordered tuple of lowercase string tokens. The tuple
        format guarantees that the function output can be safely cached by
        lru_cache.
    """
    if "docs" in dataset_name.lower():
        # For general documentation, we can use a simpler tokenization
        return tuple(
            token.lower()
            for token in TOKEN_PATTERN.findall(text)
            if token not in DEFAULT_STOP_WORDS
        )
    tokens = []

    # 1. Find all standard alphanumeric blocks
    raw_tokens = TOKEN_PATTERN.findall(text)
    # if file_type == "python":
    for token in raw_tokens:
        lower_token = token.lower()
        if lower_token not in DEFAULT_STOP_WORDS:
            tokens.append(lower_token)

        # 2. If it contains underscores (snake_case), split it up
        # if "_" in token:
        #     sub_tokens = lower_token.split("_")
        #     # Only add meaningful sub-words
        #     tokens.extend(t for t in sub_tokens if t)

        # 3. If it uses CamelCase, split it up
        camel_parts = CAMEL_SPLIT_PATTERN.split(token)
        if len(camel_parts) > 1:
            tokens.extend(
                p.lower() for p in camel_parts if p not in DEFAULT_STOP_WORDS)

    # Returning a tuple ensures it remains hashable for lru_cache
    return tuple(tokens)


# TOKEN_PATTERN = re.compile(r"\w+")
# @lru_cache(maxsize=2048)
# def tokenize_prompt(
#     text: str,
# ) -> tuple[str, ...]:

#     return tuple(
#         token.lower()
#         for token in TOKEN_PATTERN.findall(text)
#     )
