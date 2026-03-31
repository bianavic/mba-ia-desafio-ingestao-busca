import sys
import unicodedata

import pytest

sys.path.insert(0, "src")
from search import search_prompt

NO_CONTEXT_ANSWER = "Não tenho informações necessárias para responder sua pergunta."


def normalize(text):
    """Remove acentos e converte para minúsculas para comparação robusta."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


# ──────────────────────────────────────────────
# Perguntas dentro do contexto
# ──────────────────────────────────────────────


class TestExtrairAno:
    def test_ano_fundacao_supertechibrazil(self):
        resposta = search_prompt("qual o ano de fundação da empresa SuperTechIABrazil?")
        assert "2025" in resposta

    def test_ano_fundacao_delta_higiene(self):
        resposta = search_prompt("qual o ano de fundação da empresa Delta Higiene S.A.?")
        assert "2024" in resposta


class TestExtrairFaturamento:
    def test_faturamento_supertechibrazil(self):
        resposta = search_prompt("qual o faturamento da empresa SuperTechIABrazil?")
        assert "10.000.000" in resposta or "10000000" in resposta

    def test_faturamento_vanguarda_financeira(self):
        resposta = search_prompt(
            "qual o faturamento da empresa Vanguarda Financeira Serviços?"
        )
        assert "47.719.989" in resposta or "47719989" in resposta

    def test_faturamento_alfa_saude(self):
        resposta = search_prompt("qual o faturamento da empresa Alfa Saúde LTDA?")
        assert "131.151.997" in resposta or "131151997" in resposta


class TestListarEmpresas:
    def test_empresas_fundadas_2025(self):
        resposta = normalize(
            search_prompt("quais empresas foram fundadas em 2025?")
        )
        assert "supertechiabrazil" in resposta

    def test_empresas_fundadas_2024(self):
        resposta = normalize(
            search_prompt("quais empresas foram fundadas em 2024?")
        )
        empresas_esperadas = [
            "orbital Midia Servicos",
            "Delta Higiene",
            "Mirage Quimica",
            "Vanguarda Financeira",
            "Vanguarda Turismo",
            "Vale Esportes",
            "Esmeralda Hotelaria",
        ]
        for empresa in empresas_esperadas:
            assert normalize(empresa) in resposta, (
                f"Empresa '{empresa}' não encontrada na resposta"
            )


# ──────────────────────────────────────────────
# Perguntas fora do contexto
# ──────────────────────────────────────────────


class TestForaDoContexto:
    def test_capital_franca(self):
        resposta = search_prompt("Qual é a capital da França?")
        assert normalize(NO_CONTEXT_ANSWER) in normalize(resposta)

    def test_clientes_2024(self):
        resposta = search_prompt("Quantos clientes temos em 2024?")
        assert normalize(NO_CONTEXT_ANSWER) in normalize(resposta)

    def test_opiniao(self):
        resposta = search_prompt("Você acha isso bom ou ruim?")
        assert normalize(NO_CONTEXT_ANSWER) in normalize(resposta)
