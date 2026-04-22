"""DISPENSA_SUSPEITA: contrato sem licitação acima de R$ 1M."""
from typing import Iterator

from olho_publico_etl.models import Alerta

from .base import RegraAlerta


class DispensaSuspeitaRule(RegraAlerta):
    codigo = "DISPENSA_SUSPEITA"
    versao_atual = "1.0.0"
    nome = "Dispensa de licitação relevante"
    descricao = "Detecta contratos sem licitação (modalidade DISPENSA) acima de limiar."
    severidade_padrao = "atencao"
    valor_minimo_brl = 1_000_000

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6 (engine completo)")
