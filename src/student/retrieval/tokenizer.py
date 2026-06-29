import re
from functools import lru_cache

import re
from functools import lru_cache

# Keep the exact simple pattern that gave you 0.920 recall
TOKEN_PATTERN = re.compile(r"\w+")


# Matches standard words
TOKEN_PATTERN = re.compile(r"\w+")
# Detects transitions in CamelCase (e.g., 'BaseModel' -> 'Base', 'Model')
CAMEL_SPLIT_PATTERN = re.compile(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])')

@lru_cache(maxsize=2048)
def tokenize(text: str) -> tuple[str, ...]:
    tokens = []
    
    # 1. Find all standard alphanumeric blocks
    raw_tokens = TOKEN_PATTERN.findall(text)
    # if file_type == "python":
    for token in raw_tokens:
        lower_token = token.lower()
        tokens.append(lower_token)
        
        # 2. If it contains underscores (snake_case), split it up
        if "_" in token:
            sub_tokens = lower_token.split("_")
            # Only add meaningful sub-words
            tokens.extend(t for t in sub_tokens if t)
            
        # 3. If it uses CamelCase, split it up
        camel_parts = CAMEL_SPLIT_PATTERN.split(token)
        if len(camel_parts) > 1:
            tokens.extend(p.lower() for p in camel_parts if p)
    
    # Returning a tuple ensures it remains hashable for lru_cache
    return tuple(tokens)



# TOKEN_PATTERN = re.compile(r"\w+")


# @lru_cache(maxsize=2048)
# def tokenize(
#     text: str,
# ) -> tuple[str, ...]:

#     return tuple(
#         token.lower()
#         for token in TOKEN_PATTERN.findall(text)
#     )
