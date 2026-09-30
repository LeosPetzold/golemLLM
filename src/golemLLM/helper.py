def find_between(text: str, start_key: str, end_key: str) -> str:
    """
    Fast, memory-efficient extraction of text between two substrings.
    Returns None if either key is not found.
    """
    start_idx = text.find(start_key)
    if start_idx == -1:
        return None

    start_idx += len(start_key)
    end_idx = text.find(end_key, start_idx)
    if end_idx == -1:
        return None

    return text[start_idx:end_idx]
