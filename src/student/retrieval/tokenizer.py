import re


TOKEN_PATTERN = re.compile(r"\w+")


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_PATTERN.findall(text)
    ]