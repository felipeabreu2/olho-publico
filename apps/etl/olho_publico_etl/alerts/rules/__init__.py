from .concentracao import ConcentracaoRule
from .crescimento_anomalo import CrescimentoAnomaloRule
from .dispensa_suspeita import DispensaSuspeitaRule
from .doador_beneficiado import DoadorBeneficiadoRule
from .empresa_foguete import EmpresaFogueteRule
from .socio_sancionado import SocioSancionadoRule

ALL_RULES = [
    EmpresaFogueteRule(),
    DispensaSuspeitaRule(),
    SocioSancionadoRule(),
    CrescimentoAnomaloRule(),
    ConcentracaoRule(),
    DoadorBeneficiadoRule(),
]

__all__ = [
    "EmpresaFogueteRule",
    "DispensaSuspeitaRule",
    "SocioSancionadoRule",
    "CrescimentoAnomaloRule",
    "ConcentracaoRule",
    "DoadorBeneficiadoRule",
    "ALL_RULES",
]
