"""DOADOR_BENEFICIADO: empresa que doou para campanha do prefeito recebeu contrato após eleição."""
from collections.abc import Iterator

from olho_publico_etl.models import Alerta

from .base import RegraAlerta


class DoadorBeneficiadoRule(RegraAlerta):
    codigo = "DOADOR_BENEFICIADO"
    versao_atual = "1.0.0"
    nome = "Doador da campanha do prefeito"
    descricao = (
        "Detecta empresas doadoras da campanha vitoriosa para prefeito que receberam "
        "contratos após o início do mandato."
    )
    severidade_padrao = "atencao"

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
