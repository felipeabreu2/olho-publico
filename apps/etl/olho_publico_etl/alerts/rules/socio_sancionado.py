"""SOCIO_SANCIONADO: empresa cujo sócio aparece em CEIS/CNEP."""
from typing import Iterator

from olho_publico_etl.models import Alerta

from .base import RegraAlerta


class SocioSancionadoRule(RegraAlerta):
    codigo = "SOCIO_SANCIONADO"
    versao_atual = "1.0.0"
    nome = "Sócio em lista de sanções"
    descricao = "Detecta contratos firmados com empresas cujo sócio aparece em CEIS/CNEP."
    severidade_padrao = "forte"

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
