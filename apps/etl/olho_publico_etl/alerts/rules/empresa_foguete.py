"""EMPRESA_FOGUETE: CNPJ aberto há <12 meses recebeu contrato > R$ 500k."""
from typing import Iterator

from olho_publico_etl.models import Alerta

from .base import RegraAlerta


class EmpresaFogueteRule(RegraAlerta):
    codigo = "EMPRESA_FOGUETE"
    versao_atual = "1.0.0"
    nome = "Empresa-foguete"
    descricao = (
        "Detecta empresas abertas há menos de 12 meses que receberam contratos "
        "públicos relevantes."
    )
    severidade_padrao = "forte"
    valor_minimo_brl = 500_000
    meses_maximos = 12

    def detectar(self, conn) -> Iterator[Alerta]:
        sql = """
        SELECT
            c.id AS contrato_id,
            c.cnpj_fornecedor,
            c.municipio_aplicacao_id,
            c.valor,
            c.data_assinatura,
            c.modalidade_licitacao,
            e.data_abertura
        FROM contratos c
        JOIN empresas e ON e.cnpj = c.cnpj_fornecedor
        WHERE e.data_abertura IS NOT NULL
          AND c.valor >= %s
          AND c.data_assinatura - e.data_abertura < INTERVAL '%s months';
        """
        with conn.cursor() as cur:
            cur.execute(sql, (self.valor_minimo_brl, self.meses_maximos))
            for row in cur:
                contrato_id, cnpj, municipio_id, valor, data_ass, modalidade, data_abertura = row
                yield Alerta(
                    tipo=self.codigo,
                    severidade=self.severidade_padrao,
                    municipio_id=municipio_id,
                    cnpj_envolvido=cnpj,
                    evidencia={
                        "contrato_id": contrato_id,
                        "valor": str(valor),
                        "data_assinatura": data_ass.isoformat(),
                        "data_abertura": data_abertura.isoformat(),
                        "modalidade": modalidade,
                    },
                    regra_versao=self.versao_atual,
                )
