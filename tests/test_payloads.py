"""Testes para core.payloads."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.payloads import CRC16, PixPayload


def test_crc16_retorna_4_hex_chars():
    resultado = CRC16.calculate("0014BR.GOV.BCB.PIX")
    assert len(resultado) == 4
    assert all(c in "0123456789ABCDEF" for c in resultado)


def test_crc16_deterministico():
    a = CRC16.calculate("teste")
    b = CRC16.calculate("teste")
    assert a == b


def test_crc16_diferente_para_inputs_diferentes():
    a = CRC16.calculate("alpha")
    b = CRC16.calculate("beta")
    assert a != b


def test_pix_payload_normaliza_nome_para_25_chars():
    payload = PixPayload(
        key="teste@email.com",
        name="A" * 50,
        city="SP",
    )
    assert len(payload.name) == 25


def test_pix_payload_normaliza_cidade_para_15_chars():
    payload = PixPayload(
        key="teste@email.com",
        name="Nome",
        city="C" * 30,
    )
    assert len(payload.city) == 15


def test_pix_payload_generate_termina_com_crc_valido():
    payload = PixPayload(
        key="teste@email.com",
        name="FULANO",
        city="SAO PAULO",
    )
    resultado = payload.generate()
    assert "6304" in resultado
    sufixo = resultado[-4:]
    assert len(sufixo) == 4
    assert all(c in "0123456789ABCDEF" for c in sufixo)


def test_pix_payload_txid_default_e_asteriscos():
    payload = PixPayload(
        key="teste@email.com",
        name="FULANO",
        city="SP",
    )
    assert payload.txid == "***"
