from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict

class SaldoService:
    @staticmethod
    def calcular(saldo_inicial: float, transacoes: List[Dict]) -> float:
        """
        Recebe o saldo inicial e uma lista de dicionários de transações.
        Subtrai os valores utilizando alta precisão matemática e retorna um float
        com exatas duas casas decimais.
        """
        # Converte o saldo inicial para Decimal, usando string para não perder precisão
        saldo = Decimal(str(saldo_inicial))
        
        for transacao in transacoes:
            # Pega o valor da transação (se não existir, usa 0.0)
            valor = transacao.get("valor", 0.0)
            # Subtrai usando a precisão do Decimal
            saldo -= Decimal(str(valor))
            
        # Arredonda de forma segura para duas casas decimais e devolve como float
        saldo_arredondado = saldo.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
        return float(saldo_arredondado)