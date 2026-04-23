"""CRESCIMENTO_ANOMALO: empresa cujo faturamento público cresceu >300% ano a ano."""
from collections.abc import Iterator

from olho_publico_etl.models import Alerta

from .base import RegraAlerta


class CrescimentoAnomaloRule(RegraAlerta):
    codigo = "CRESCIMENTO_ANOMALO"
    versao_atual = "1.0.0"
    nome = "Crescimento anômalo em receita pública"
    descricao = "Detecta empresas cuja receita pública cresceu mais de 300% ano a ano."
    severidade_padrao = "atencao"
    multiplicador_minimo = 4.0  # >300% = >=4x

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
