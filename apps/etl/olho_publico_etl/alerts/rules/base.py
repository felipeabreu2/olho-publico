from abc import ABC, abstractmethod
from collections.abc import Iterator

from olho_publico_etl.models import Alerta


class RegraAlerta(ABC):
    """Base for alert detection rules.

    Each rule has a stable code, current semver version, and parameters.
    A rule reads from the database and yields Alerta records.
    """

    codigo: str
    versao_atual: str
    nome: str
    descricao: str
    severidade_padrao: str  # "info" | "atencao" | "forte"
    disclaimer: str = (
        "Este é um sinal automatizado baseado em dados públicos oficiais. "
        "Não constitui acusação ou conclusão investigativa."
    )

    @abstractmethod
    def detectar(self, conn) -> Iterator[Alerta]:
        """Run the rule against the database (psycopg connection) and yield alerts."""
