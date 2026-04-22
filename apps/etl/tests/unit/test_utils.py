from olho_publico_etl.utils.cpf_mask import mask_cpf
from olho_publico_etl.utils.slug import slugify


def test_mask_cpf_with_punctuation():
    assert mask_cpf("123.456.789-09") == "***.456.789-**"


def test_mask_cpf_bare_digits():
    assert mask_cpf("12345678909") == "***.456.789-**"


def test_mask_cpf_invalid_returns_none():
    assert mask_cpf("123") is None
    assert mask_cpf("") is None
    assert mask_cpf(None) is None


def test_slugify_accents():
    assert slugify("São Paulo") == "sao-paulo"


def test_slugify_complex():
    assert slugify("Itabaiana - SE") == "itabaiana-se"
