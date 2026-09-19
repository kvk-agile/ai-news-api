import re

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12",
}


def normalize_text(value: str) -> str:
    """Normalize punctuation, case, and whitespace for deterministic comparison."""

    return " ".join(re.sub(r"[^a-z0-9.%]+", " ", value.lower()).split())


def extract_numbers(value: str) -> list[str]:
    """Return every number in an answer, in order, including spelled-out ones."""

    cleaned = value.lower().replace(",", "")
    found = []
    for match in re.finditer(r"-?\d+(?:\.\d+)?|[a-z]+", cleaned):
        token = match.group(0)
        if token in NUMBER_WORDS:
            found.append(NUMBER_WORDS[token])
        elif token[0].isdigit() or token[0] == "-":
            found.append(token)
    return found


def extract_boolean(value: str) -> str | None:
    """Return a leading true/false or yes/no answer in canonical form."""

    match = re.match(r"\s*(true|false|yes|no)\b", value, flags=re.IGNORECASE)
    first_word = match.group(1).lower() if match else ""
    if first_word in {"true", "yes"}:
        return "true"
    if first_word in {"false", "no"}:
        return "false"
    return None


def answer_matches(case: dict, actual_answer: str) -> bool:
    """Score one answer according to the case's declared answer type."""

    expected = case["expected_answer"]
    answer_type = case["answer_type"]

    if answer_type == "number":
        expected_numbers = extract_numbers(expected)
        actual_numbers = extract_numbers(actual_answer)
        if not expected_numbers or not actual_numbers:
            return False
        return expected_numbers[0] in actual_numbers

    if answer_type == "boolean":
        return extract_boolean(actual_answer) == extract_boolean(expected)

    acceptable = [expected, *case.get("accepted_answers", [])]
    actual = normalize_text(actual_answer)
    return any(normalize_text(answer) in actual for answer in acceptable)