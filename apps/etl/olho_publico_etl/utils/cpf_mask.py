def mask_cpf(cpf: str | None) -> str | None:
    """Return CPF in masked format like '***.123.456-**'.

    Accepts CPF with or without punctuation. Returns None if input is empty or invalid.
    """
    if not cpf:
        return None
    digits = "".join(ch for ch in cpf if ch.isdigit())
    if len(digits) != 11:
        return None
    return f"***.{digits[3:6]}.{digits[6:9]}-**"
