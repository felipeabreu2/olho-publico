"""CONCENTRACAO: mesma empresa = >40% dos contratos de uma secretaria."""
from typing import Iterator

from olho_publico_etl.models import Alerta

from .base import RegraAlerta


class ConcentracaoRule(RegraAlerta):
    codigo = "CONCENTRACAO"
    versao_atual = "1.0.0"
    nome = "Concentração de fornecedor"
    descricao = "Detecta concentração excessiva de uma única empresa em um órgão."
    severidade_padrao = "info"
    percentual_minimo = 0.40

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
