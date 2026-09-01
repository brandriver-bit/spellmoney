import random
import re
from decimal import Decimal

import pytest

from spellmoney import (
    IDIOMAS,
    MONEDAS,
    SpellMoneyError,
    a_letras,
    numero_a_letras,
    numero_a_letras_en,
    numero_a_letras_fr,
    numero_a_letras_pt,
)

# =============================================================================
# numero_a_letras (español)
# =============================================================================

CASOS_ES = [
    (0, "cero"), (1, "uno"), (5, "cinco"), (10, "diez"), (11, "once"),
    (15, "quince"), (16, "dieciséis"), (19, "diecinueve"), (20, "veinte"),
    (21, "veintiuno"), (22, "veintidós"), (29, "veintinueve"), (30, "treinta"),
    (31, "treinta y uno"), (45, "cuarenta y cinco"), (99, "noventa y nueve"),
    (100, "cien"), (101, "ciento uno"), (115, "ciento quince"),
    (199, "ciento noventa y nueve"), (200, "doscientos"),
    (221, "doscientos veintiuno"), (500, "quinientos"),
    (999, "novecientos noventa y nueve"), (1000, "mil"), (1001, "mil uno"),
    (1100, "mil cien"), (2000, "dos mil"), (21000, "veintiún mil"),
    (100000, "cien mil"), (101000, "ciento un mil"),
    (999999, "novecientos noventa y nueve mil novecientos noventa y nueve"),
    (1000000, "un millón"), (2000000, "dos millones"),
    (1000001, "un millón uno"), (21000000, "veintiún millones"),
    (1000000000, "mil millones"), (2000000000, "dos mil millones"),
    (1000000000000, "un billón"), (2000000000000, "dos billones"),
]


@pytest.mark.parametrize("n, esperado", CASOS_ES)
def test_numero_a_letras(n, esperado):
    assert numero_a_letras(n) == esperado


def test_rechaza_negativos():
    with pytest.raises(SpellMoneyError):
        numero_a_letras(-5)


def test_rechaza_no_enteros():
    with pytest.raises(SpellMoneyError):
        numero_a_letras(5.5)


def test_rechaza_fuera_de_rango():
    with pytest.raises(SpellMoneyError):
        numero_a_letras(10 ** 15)


# =============================================================================
# numero_a_letras_en (inglés)
# =============================================================================

CASOS_EN = [
    (0, "zero"), (1, "one"), (15, "fifteen"), (21, "twenty-one"),
    (100, "one hundred"), (101, "one hundred one"),
    (999, "nine hundred ninety-nine"), (1000, "one thousand"),
    (1_000_000, "one million"), (1_000_000_000, "one billion"),
    (1_000_000_000_000, "one trillion"), (2_000_000_000, "two billion"),
]


@pytest.mark.parametrize("n, esperado", CASOS_EN)
def test_numero_a_letras_en(n, esperado):
    assert numero_a_letras_en(n) == esperado


# =============================================================================
# numero_a_letras_pt (portugués)
# =============================================================================

CASOS_PT = [
    (0, "m", "zero"), (1, "m", "um"), (1, "f", "uma"), (2, "m", "dois"),
    (2, "f", "duas"), (15, "m", "quinze"), (21, "m", "vinte e um"),
    (21, "f", "vinte e uma"), (100, "m", "cem"), (101, "m", "cento e um"),
    (200, "m", "duzentos"), (200, "f", "duzentas"), (1000, "m", "mil"),
    (1_000_000, "m", "um milhão"), (1_000_000_000, "m", "um bilhão"),
    (2_000_000_000, "m", "dois bilhões"),
]


@pytest.mark.parametrize("n, genero, esperado", CASOS_PT)
def test_numero_a_letras_pt(n, genero, esperado):
    assert numero_a_letras_pt(n, genero) == esperado


# =============================================================================
# numero_a_letras_fr (francés)
# =============================================================================

CASOS_FR = [
    (0, "zéro"), (1, "un"), (21, "vingt et un"), (71, "soixante et onze"),
    (80, "quatre-vingts"), (81, "quatre-vingt-un"), (90, "quatre-vingt-dix"),
    (99, "quatre-vingt-dix-neuf"), (100, "cent"), (125, "cent vingt-cinq"),
    (200, "deux cents"), (201, "deux cent un"), (1000, "mille"),
    (1_000_000, "un million"), (1_000_000_000, "un milliard"),
    (1_000_000_000_000, "un billion"),
]


@pytest.mark.parametrize("n, esperado", CASOS_FR)
def test_numero_a_letras_fr(n, esperado):
    assert numero_a_letras_fr(n) == esperado


# =============================================================================
# a_letras
# =============================================================================


def test_monto_basico_en_usd():
    assert a_letras(125.50) == "CIENTO VEINTICINCO DÓLARES CON 50/100"


def test_singular_de_moneda():
    assert a_letras(1, moneda="GTQ") == "UN QUETZAL CON 00/100"


def test_apocope_antes_de_moneda_masculina():
    assert a_letras(21, moneda="USD") == "VEINTIÚN DÓLARES CON 00/100"


def test_genero_femenino():
    assert a_letras(1, moneda="GBP") == "UNA LIBRA ESTERLINA CON 00/100"
    assert a_letras(21, moneda="GBP") == "VEINTIUNA LIBRAS ESTERLINAS CON 00/100"


def test_cero():
    assert a_letras(0) == "CERO DÓLARES CON 00/100"


def test_de_antes_de_millon():
    assert a_letras(1000000, moneda="EUR") == "UN MILLÓN DE EUROS CON 00/100"
    assert a_letras(21000000, moneda="EUR") == "VEINTIÚN MILLONES DE EUROS CON 00/100"


def test_sin_de_cuando_hay_unidades_menores():
    assert a_letras(1000100, moneda="USD") == "UN MILLÓN CIEN DÓLARES CON 00/100"


def test_sin_de_con_mil():
    assert a_letras(1000, moneda="USD") == "MIL DÓLARES CON 00/100"


def test_centavos_en_palabras():
    assert a_letras(10.50, centavos="palabras") == "DIEZ DÓLARES CON CINCUENTA CENTAVOS"
    assert a_letras(10.01, centavos="palabras") == "DIEZ DÓLARES CON UN CENTAVO"
    assert a_letras(10.00, centavos="palabras") == "DIEZ DÓLARES CON CERO CENTAVOS"


def test_minusculas():
    assert a_letras(2, moneda="GBP", mayusculas=False) == "dos libras esterlinas con 00/100"


def test_redondeo_flotante():
    assert a_letras(19.999999) == "VEINTE DÓLARES CON 00/100"


def test_moneda_invalida():
    with pytest.raises(SpellMoneyError):
        a_letras(10, moneda="XXX")


def test_monto_negativo():
    with pytest.raises(SpellMoneyError):
        a_letras(-10)


def test_idioma_invalido():
    with pytest.raises(SpellMoneyError):
        a_letras(10, idioma="de")


def test_las_154_monedas_iso_4217_funcionan_en_espanol():
    for codigo in MONEDAS:
        for monto in (0, 1, 21, 1000, 1000000, 1234.56):
            resultado = a_letras(monto, moneda=codigo)
            assert "CON" in resultado
            assert resultado.endswith("/100")
            assert " UNO " not in f" {resultado} "


def test_las_154_monedas_iso_4217_funcionan_en_ingles():
    for codigo in MONEDAS:
        for monto in (0, 1, 21, 1000, 1000000, 1234.56):
            resultado = a_letras(monto, moneda=codigo, idioma="en")
            assert "AND" in resultado
            assert resultado.endswith("/100")


def test_ejemplos_del_docstring():
    assert a_letras(125.50) == "CIENTO VEINTICINCO DÓLARES CON 50/100"
    assert a_letras(125.50, idioma="en") == "ONE HUNDRED TWENTY-FIVE DOLLARS AND 50/100"
    assert a_letras(125.50, idioma="pt", moneda="BRL") == "CENTO E VINTE E CINCO REAIS E 50/100"
    assert a_letras(125.50, idioma="fr", moneda="EUR") == "CENT VINGT-CINQ EUROS ET 50/100"


def test_idioma_en():
    assert a_letras(1, moneda="USD", idioma="en") == "ONE DOLLAR AND 00/100"
    assert a_letras(2, moneda="USD", idioma="en") == "TWO DOLLARS AND 00/100"
    assert a_letras(1_000_000, moneda="EUR", idioma="en") == "ONE MILLION EUROS AND 00/100"


def test_idioma_pt_y_genero():
    assert a_letras(1, moneda="BRL", idioma="pt") == "UM REAL E 00/100"
    assert a_letras(1, moneda="GBP", idioma="pt") == "UMA LIBRA ESTERLINA E 00/100"
    assert a_letras(2, moneda="GBP", idioma="pt") == "DUAS LIBRAS ESTERLINAS E 00/100"
    assert a_letras(1_000_000, moneda="BRL", idioma="pt") == "UM MILHÃO DE REAIS E 00/100"


def test_idioma_fr_de_y_elision():
    assert a_letras(1_000_000, moneda="USD", idioma="fr") == "UN MILLION DE DOLLARS AMÉRICAINS ET 00/100"
    assert a_letras(1_000_000, moneda="EUR", idioma="fr") == "UN MILLION D'EUROS ET 00/100"
    assert a_letras(1, moneda="EUR", idioma="fr") == "UN EURO ET 00/100"


def test_ayuda_buscada_moneda_sin_traduccion_a_un_idioma():
    with pytest.raises(SpellMoneyError):
        a_letras(10, moneda="AFN", idioma="pt")
    with pytest.raises(SpellMoneyError):
        a_letras(10, moneda="AFN", idioma="fr")


def test_idiomas_declarados():
    assert list(IDIOMAS) == ["es", "en", "pt", "fr"]


# =============================================================================
# Montos como cadena o Decimal: lectura decimal exacta
# =============================================================================


def test_cadena_equivale_al_numero_en_casos_normales():
    assert a_letras("125.50") == "CIENTO VEINTICINCO DÓLARES CON 50/100"
    assert a_letras("0") == "CERO DÓLARES CON 00/100"
    assert a_letras("1", moneda="GTQ") == "UN QUETZAL CON 00/100"
    assert a_letras("21") == "VEINTIÚN DÓLARES CON 00/100"


def test_cadena_acepta_decimales_incompletos():
    assert a_letras("10.5") == "DIEZ DÓLARES CON 50/100"
    assert a_letras("10.") == "DIEZ DÓLARES CON 00/100"
    assert a_letras("10.05") == "DIEZ DÓLARES CON 05/100"


def test_cadena_redondea_half_up_de_forma_exacta():
    # El float más cercano a 2.675 queda por debajo, así que el número da 67.
    assert a_letras(2.675) == "DOS DÓLARES CON 67/100"
    # La cadena conserva el decimal escrito, así que redondea a 68.
    assert a_letras("2.675") == "DOS DÓLARES CON 68/100"
    assert a_letras("1.005") == "UN DÓLAR CON 01/100"
    assert a_letras("0.005") == "CERO DÓLARES CON 01/100"
    assert a_letras("0.004") == "CERO DÓLARES CON 00/100"


def test_cadena_acarrea_al_entero():
    assert a_letras("19.999") == "VEINTE DÓLARES CON 00/100"
    assert a_letras("0.999") == "UN DÓLAR CON 00/100"


def test_acepta_decimal():
    assert a_letras(Decimal("125.50")) == "CIENTO VEINTICINCO DÓLARES CON 50/100"
    assert a_letras(Decimal("2.675")) == "DOS DÓLARES CON 68/100"


def test_cadena_admite_el_tope_del_rango():
    assert "99/100" in a_letras("999999999999999.99")


@pytest.mark.parametrize(
    "invalido", ["", "abc", "1,50", "-5", "1.2.3", "1e3", " ", "+5"]
)
def test_rechaza_cadenas_invalidas(invalido):
    with pytest.raises(SpellMoneyError):
        a_letras(invalido)


def test_rechaza_cadenas_fuera_de_rango():
    with pytest.raises(SpellMoneyError):
        a_letras("1000000000000000")


# =============================================================================
# Pruebas por propiedades: miles de valores generados, invariantes verificadas
# =============================================================================


def test_a_letras_cumple_sus_invariantes_sobre_valores_generados():
    azar = random.Random(20260901)  # semilla fija: un fallo siempre se reproduce
    codigos = list(MONEDAS)
    for _ in range(5000):
        idioma = azar.choice(IDIOMAS)
        codigo = azar.choice(codigos)
        if idioma not in MONEDAS[codigo]:
            continue
        monto = azar.randrange(10 ** 12) + azar.random()

        resultado = a_letras(monto, moneda=codigo, idioma=idioma)

        assert isinstance(resultado, str)
        assert resultado
        assert "None" not in resultado
        assert "  " not in resultado
        assert resultado.strip() == resultado
        assert resultado == resultado.upper()
        assert re.search(r"\d\d/100$", resultado)
        # El apócope nunca deja "uno" pegado al nombre de la moneda.
        if idioma == "es":
            assert " UNO " not in f" {resultado} "


def test_numero_y_cadena_coinciden_en_montos_de_dos_decimales():
    azar = random.Random(4217)
    for _ in range(5000):
        entero = azar.randrange(10 ** 9)
        centavos = azar.randrange(100)
        como_cadena = f"{entero}.{centavos:02d}"
        assert a_letras(float(como_cadena)) == a_letras(como_cadena)


def test_los_conversores_de_numero_nunca_producen_texto_malformado():
    azar = random.Random(1954)
    motores = [
        numero_a_letras,
        numero_a_letras_en,
        numero_a_letras_fr,
        lambda n: numero_a_letras_pt(n, "f"),
    ]
    for _ in range(5000):
        n = azar.randrange(10 ** 15)
        for motor in motores:
            texto = motor(n)
            assert texto
            assert "None" not in texto
            assert "  " not in texto
            assert texto.strip() == texto
