from better_profanity import profanity


profanity.load_censor_words()

CRISIS_KEYWORDS = [
    'suicide', 'kill myself', 'end it all',
    'self harm', 'hurt myself', 'want to die',
    'no reason to live', 'cant go on', "can't go on",
]


FLAGGED_KEYWORDS = [
    'hate', 'kill', 'attack', 'threat',
]


def check_crisis(text: str) -> bool:
    """
    Returns True if the text contains crisis-level keywords.
    Used to show helpline banner on the submit page.
    """
    lower = text.lower()
    return any(word in lower for word in CRISIS_KEYWORDS)


def check_flagged(text: str) -> bool:
    """
    Returns True if post should go to moderation queue.
    """
    if profanity.contains_profanity(text):
        return True
    lower = text.lower()
    return any(word in lower for word in FLAGGED_KEYWORDS)


def should_auto_approve(text: str) -> bool:
    """
    Returns True if post is clean enough to auto-approve.
    """
    return not check_flagged(text)