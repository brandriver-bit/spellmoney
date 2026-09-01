"""
spellmoney
==========

Convierte cantidades numéricas a su representación en letras, para documentos
legales y financieros: cheques, facturas, recibos y contratos (por ejemplo:
"CIENTO VEINTICINCO DÓLARES CON 50/100").

Soporta cuatro idiomas — español, inglés, portugués (variante de Brasil) y
francés — y las 154 divisas activas del estándar ISO 4217. La cobertura de
nombres de moneda es completa en español e inglés; en portugués y francés
cubre los países que hablan esos idiomas más las monedas más usadas del
mundo — el resto está marcado como "ayuda buscada": se aceptan pull requests
de quien domine ese idioma y esa moneda.

Uso básico::

    from spellmoney import a_letras

    a_letras(125.50)                                  # "CIENTO VEINTICINCO DÓLARES CON 50/100"
    a_letras(125.50, idioma="en")                     # "ONE HUNDRED TWENTY-FIVE DOLLARS AND 50/100"
    a_letras(125.50, idioma="pt", moneda="BRL")       # "CENTO E VINTE E CINCO REAIS E 50/100"
    a_letras(125.50, idioma="fr", moneda="EUR")       # "CENT VINGT-CINQ EUROS ET 50/100"
"""

import math
from typing import Callable, Dict, List, Literal, Tuple

from .monedas import MONEDAS, FormaMoneda

__all__ = [
    "a_letras",
    "numero_a_letras",
    "numero_a_letras_en",
    "numero_a_letras_pt",
    "numero_a_letras_fr",
    "MONEDAS",
    "FormaMoneda",
    "IDIOMAS",
    "SpellMoneyError",
]

__version__ = "1.0.0"

IDIOMAS: Tuple[str, ...] = ("es", "en", "pt", "fr")

Idioma = Literal["es", "en", "pt", "fr"]
Genero = Literal["m", "f"]

_MAXIMO = 10 ** 15


class SpellMoneyError(ValueError):
    """Error de uso: monto, moneda o idioma inválidos."""


# =============================================================================
# ESPAÑOL
# =============================================================================

_UNIDADES_ES = ["", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]

_ESPECIALES_ES: Dict[int, str] = {
    10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce",
    15: "quince", 16: "dieciséis", 17: "diecisiete", 18: "dieciocho",
    19: "diecinueve", 20: "veinte", 21: "veintiuno", 22: "veintidós",
    23: "veintitrés", 24: "veinticuatro", 25: "veinticinco",
    26: "veintiséis", 27: "veintisiete", 28: "veintiocho", 29: "veintinueve",
}

_DECENAS_ES: Dict[int, str] = {
    30: "treinta", 40: "cuarenta", 50: "cincuenta",
    60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa",
}

_CENTENAS_ES: Dict[int, str] = {
    100: "cien", 200: "doscientos", 300: "trescientos", 400: "cuatrocientos",
    500: "quinientos", 600: "seiscientos", 700: "setecientos",
    800: "ochocientos", 900: "novecientos",
}


def _grupo_es(n: int) -> str:
    if n == 0:
        return ""
    if n < 10:
        return _UNIDADES_ES[n]
    if n < 30:
        return _ESPECIALES_ES[n]
    if n < 100:
        decena = n // 10 * 10
        unidad = n % 10
        palabra = _DECENAS_ES[decena]
        return f"{palabra} y {_UNIDADES_ES[unidad]}" if unidad else palabra
    if n == 100:
        return "cien"
    centena = n // 100 * 100
    resto = n % 100
    prefijo = "ciento" if centena == 100 else _CENTENAS_ES[centena]
    return f"{prefijo} {_grupo_es(resto)}" if resto else prefijo


def _apocopar_es(palabra: str, genero: str) -> str:
    if not palabra.endswith("uno"):
        return palabra
    if genero == "f":
        return palabra[:-1] + "a"
    if palabra.endswith("veintiuno"):
        return palabra[:-3] + "ún"
    return palabra[:-1]


def numero_a_letras(n: int) -> str:
    """Convierte un entero no negativo a palabras en español (minúsculas, sin
    nombre de moneda). Soporta hasta 999.999.999.999.999.

    Usa la escala larga real del español: 10**9 es "mil millones" y 10**12 es
    "billón" — no el falso amigo de "billion" en inglés.
    """
    n = _validar_entero(n)
    if n == 0:
        return "cero"

    billones, resto = divmod(n, 10 ** 12)
    mil_millones, resto = divmod(resto, 10 ** 9)
    millones, resto = divmod(resto, 10 ** 6)
    miles, unidades = divmod(resto, 1000)

    partes: List[str] = []
    if billones:
        palabra = _apocopar_es(_grupo_es(billones), "m")
        partes.append(f"{palabra} billón" if billones == 1 else f"{palabra} billones")
    if mil_millones:
        palabra = "mil" if mil_millones == 1 else f"{_apocopar_es(_grupo_es(mil_millones), 'm')} mil"
        partes.append(f"{palabra} millones")
    if millones:
        palabra = _apocopar_es(_grupo_es(millones), "m")
        partes.append(f"{palabra} millón" if millones == 1 else f"{palabra} millones")
    if miles:
        partes.append("mil" if miles == 1 else f"{_apocopar_es(_grupo_es(miles), 'm')} mil")
    if unidades:
        partes.append(_grupo_es(unidades))
    return " ".join(partes)


# =============================================================================
# INGLÉS (sin género, escala corta: billion = 10**9)
# =============================================================================

_UNITS_EN = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

_TEENS_EN: Dict[int, str] = {
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
}

_TENS_EN: Dict[int, str] = {
    20: "twenty", 30: "thirty", 40: "forty", 50: "fifty",
    60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety",
}


def _grupo_en(n: int) -> str:
    if n == 0:
        return ""
    if n < 10:
        return _UNITS_EN[n]
    if n < 20:
        return _TEENS_EN[n]
    if n < 100:
        tens = n // 10 * 10
        unit = n % 10
        palabra = _TENS_EN[tens]
        return f"{palabra}-{_UNITS_EN[unit]}" if unit else palabra
    hundred, rest = divmod(n, 100)
    palabra = f"{_UNITS_EN[hundred]} hundred"
    return f"{palabra} {_grupo_en(rest)}" if rest else palabra


def numero_a_letras_en(n: int) -> str:
    """Converts a non-negative integer to English words. Supports up to
    999,999,999,999,999. Uses the short scale (billion = 10**9)."""
    n = _validar_entero(n)
    if n == 0:
        return "zero"

    trillions, resto = divmod(n, 10 ** 12)
    billions, resto = divmod(resto, 10 ** 9)
    millions, resto = divmod(resto, 10 ** 6)
    thousands, units = divmod(resto, 1000)

    partes: List[str] = []
    if trillions:
        partes.append(f"{_grupo_en(trillions)} trillion")
    if billions:
        partes.append(f"{_grupo_en(billions)} billion")
    if millions:
        partes.append(f"{_grupo_en(millions)} million")
    if thousands:
        partes.append(f"{_grupo_en(thousands)} thousand")
    if units:
        partes.append(_grupo_en(units))
    return " ".join(partes)


# =============================================================================
# PORTUGUÉS (Brasil; escala corta: bilhão = 10**9). "um/dois" y las centenas
# (duzentos...) tienen forma femenina.
# =============================================================================

_UNIDADES_PT_M = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]
_UNIDADES_PT_F = ["", "uma", "duas", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]

_ESPECIALES_PT: Dict[int, str] = {
    10: "dez", 11: "onze", 12: "doze", 13: "treze", 14: "catorze",
    15: "quinze", 16: "dezesseis", 17: "dezessete", 18: "dezoito",
    19: "dezenove", 20: "vinte",
}

_DEZENAS_PT: Dict[int, str] = {
    20: "vinte", 30: "trinta", 40: "quarenta", 50: "cinquenta",
    60: "sessenta", 70: "setenta", 80: "oitenta", 90: "noventa",
}

_CENTENAS_PT_M: Dict[int, str] = {
    200: "duzentos", 300: "trezentos", 400: "quatrocentos",
    500: "quinhentos", 600: "seiscentos", 700: "setecentos",
    800: "oitocentos", 900: "novecentos",
}
_CENTENAS_PT_F: Dict[int, str] = {
    200: "duzentas", 300: "trezentas", 400: "quatrocentas",
    500: "quinhentas", 600: "seiscentas", 700: "setecentas",
    800: "oitocentas", 900: "novecentas",
}


def _grupo_pt(n: int, genero: str) -> str:
    unidades = _UNIDADES_PT_F if genero == "f" else _UNIDADES_PT_M
    if n == 0:
        return ""
    if n < 10:
        return unidades[n]
    if n <= 20:
        return _ESPECIALES_PT[n]
    if n < 100:
        dezena = n // 10 * 10
        unidade = n % 10
        palavra = _DEZENAS_PT[dezena]
        return f"{palavra} e {unidades[unidade]}" if unidade else palavra
    if n == 100:
        return "cem"
    centena = n // 100 * 100
    resto = n % 100
    prefixo = "cento" if centena == 100 else (_CENTENAS_PT_F if genero == "f" else _CENTENAS_PT_M)[centena]
    return f"{prefixo} e {_grupo_pt(resto, genero)}" if resto else prefixo


def numero_a_letras_pt(n: int, genero: str = "m") -> str:
    """Converte um número inteiro não negativo em palavras, em português do
    Brasil. Suporta até 999.999.999.999.999. Usa a escala curta (bilhão =
    10**9), padrão no Brasil.

    ``genero`` afeta apenas o dígito final (um/uma, dois/duas, e as centenas):
    os multiplicadores de milhão/bilhão/trilhão são sempre tratados como
    masculinos, porque concordam com "milhão" e não com o substantivo que vem
    depois.
    """
    n = _validar_entero(n)
    if n == 0:
        return "zero"

    trilhoes, resto = divmod(n, 10 ** 12)
    bilhoes, resto = divmod(resto, 10 ** 9)
    milhoes, resto = divmod(resto, 10 ** 6)
    milhares, unidades = divmod(resto, 1000)

    partes: List[str] = []
    if trilhoes:
        palavra = _grupo_pt(trilhoes, "m")
        partes.append(f"{palavra} trilhão" if trilhoes == 1 else f"{palavra} trilhões")
    if bilhoes:
        palavra = _grupo_pt(bilhoes, "m")
        partes.append(f"{palavra} bilhão" if bilhoes == 1 else f"{palavra} bilhões")
    if milhoes:
        palavra = _grupo_pt(milhoes, "m")
        partes.append(f"{palavra} milhão" if milhoes == 1 else f"{palavra} milhões")
    if milhares:
        partes.append("mil" if milhares == 1 else f"{_grupo_pt(milhares, 'm')} mil")
    if unidades:
        partes.append(_grupo_pt(unidades, genero))
    return " ".join(partes)


# =============================================================================
# FRANCÉS (escala larga: milliard = 10**9, billion = 10**12). Solo "un" tiene
# forma femenina ("une"); se aplica al final, sobre el grupo de unidades que
# queda pegado directamente al sustantivo.
# =============================================================================

_0_99_FR: Dict[int, str] = {
    0: "", 1: "un", 2: "deux", 3: "trois", 4: "quatre", 5: "cinq", 6: "six",
    7: "sept", 8: "huit", 9: "neuf", 10: "dix", 11: "onze", 12: "douze",
    13: "treize", 14: "quatorze", 15: "quinze", 16: "seize",
    17: "dix-sept", 18: "dix-huit", 19: "dix-neuf", 20: "vingt",
    21: "vingt et un", 22: "vingt-deux", 23: "vingt-trois", 24: "vingt-quatre",
    25: "vingt-cinq", 26: "vingt-six", 27: "vingt-sept", 28: "vingt-huit",
    29: "vingt-neuf", 30: "trente", 31: "trente et un", 32: "trente-deux",
    33: "trente-trois", 34: "trente-quatre", 35: "trente-cinq", 36: "trente-six",
    37: "trente-sept", 38: "trente-huit", 39: "trente-neuf", 40: "quarante",
    41: "quarante et un", 42: "quarante-deux", 43: "quarante-trois",
    44: "quarante-quatre", 45: "quarante-cinq", 46: "quarante-six",
    47: "quarante-sept", 48: "quarante-huit", 49: "quarante-neuf",
    50: "cinquante", 51: "cinquante et un", 52: "cinquante-deux",
    53: "cinquante-trois", 54: "cinquante-quatre", 55: "cinquante-cinq",
    56: "cinquante-six", 57: "cinquante-sept", 58: "cinquante-huit",
    59: "cinquante-neuf", 60: "soixante", 61: "soixante et un",
    62: "soixante-deux", 63: "soixante-trois", 64: "soixante-quatre",
    65: "soixante-cinq", 66: "soixante-six", 67: "soixante-sept",
    68: "soixante-huit", 69: "soixante-neuf", 70: "soixante-dix",
    71: "soixante et onze", 72: "soixante-douze", 73: "soixante-treize",
    74: "soixante-quatorze", 75: "soixante-quinze", 76: "soixante-seize",
    77: "soixante-dix-sept", 78: "soixante-dix-huit", 79: "soixante-dix-neuf",
    80: "quatre-vingts", 81: "quatre-vingt-un", 82: "quatre-vingt-deux",
    83: "quatre-vingt-trois", 84: "quatre-vingt-quatre", 85: "quatre-vingt-cinq",
    86: "quatre-vingt-six", 87: "quatre-vingt-sept", 88: "quatre-vingt-huit",
    89: "quatre-vingt-neuf", 90: "quatre-vingt-dix", 91: "quatre-vingt-onze",
    92: "quatre-vingt-douze", 93: "quatre-vingt-treize", 94: "quatre-vingt-quatorze",
    95: "quatre-vingt-quinze", 96: "quatre-vingt-seize", 97: "quatre-vingt-dix-sept",
    98: "quatre-vingt-dix-huit", 99: "quatre-vingt-dix-neuf",
}


def _grupo_fr(n: int) -> str:
    if n < 100:
        return _0_99_FR[n]
    centaine, resto = divmod(n, 100)
    if centaine == 1:
        mot = "cent"
    else:
        mot = f"{_0_99_FR[centaine]} cent"
        if resto == 0:
            mot += "s"
    return f"{mot} {_0_99_FR[resto]}" if resto else mot


def _feminiser_fr(mot: str) -> str:
    return mot[:-2] + "une" if mot.endswith("un") else mot


def numero_a_letras_fr(n: int) -> str:
    """Convertit un entier non négatif en mots français. Prend en charge
    jusqu'à 999 999 999 999 999. Utilise l'échelle longue réelle du français :
    10**9 est "milliard" et 10**12 est "billion"."""
    n = _validar_entero(n)
    if n == 0:
        return "zéro"

    billions, resto = divmod(n, 10 ** 12)
    milliards, resto = divmod(resto, 10 ** 9)
    millions, resto = divmod(resto, 10 ** 6)
    milliers, unites = divmod(resto, 1000)

    partes: List[str] = []
    if billions:
        mot = _grupo_fr(billions)
        partes.append(f"{mot} billion" if billions == 1 else f"{mot} billions")
    if milliards:
        mot = _grupo_fr(milliards)
        partes.append(f"{mot} milliard" if milliards == 1 else f"{mot} milliards")
    if millions:
        mot = _grupo_fr(millions)
        partes.append(f"{mot} million" if millions == 1 else f"{mot} millions")
    if milliers:
        partes.append("mille" if milliers == 1 else f"{_grupo_fr(milliers)} mille")
    if unites:
        partes.append(_grupo_fr(unites))
    return " ".join(partes)


def _validar_entero(n) -> int:
    """Acepta un entero no negativo dentro de rango y lo devuelve como ``int``.

    Un ``float`` con parte decimal cero (``5.0``) se acepta y se convierte;
    cualquier otro valor decimal se rechaza.
    """
    if isinstance(n, bool) or not isinstance(n, (int, float)):
        raise SpellMoneyError("se esperaba un entero no negativo")
    if isinstance(n, float):
        if not n.is_integer():
            raise SpellMoneyError("se esperaba un entero no negativo")
        n = int(n)
    if n < 0:
        raise SpellMoneyError("no se admiten números negativos")
    if n >= _MAXIMO:
        raise SpellMoneyError("el número excede el rango soportado (máximo 999,999,999,999,999)")
    return n


_MOTOR: Dict[str, Callable[[int, str], str]] = {
    "es": lambda n, genero: numero_a_letras(n),
    "en": lambda n, genero: numero_a_letras_en(n),
    "pt": lambda n, genero: numero_a_letras_pt(n, genero),
    "fr": lambda n, genero: numero_a_letras_fr(n),
}

_PALABRA_CERO: Dict[str, str] = {"es": "cero", "en": "zero", "pt": "zero", "fr": "zéro"}
_CONECTOR: Dict[str, str] = {"es": "CON", "en": "AND", "pt": "E", "fr": "ET"}
_CENTAVOS_PALABRA: Dict[str, Tuple[str, str]] = {
    "es": ("centavo", "centavos"),
    "en": ("cent", "cents"),
    "pt": ("centavo", "centavos"),
    "fr": ("centime", "centimes"),
}
_ESCALA_QUE_PIDE_DE: Dict[str, Tuple[str, ...]] = {
    "es": ("millón", "millones", "billón", "billones"),
    "pt": ("milhão", "milhões", "bilhão", "bilhões", "trilhão", "trilhões"),
    "fr": ("million", "millions", "milliard", "milliards", "billion", "billions"),
}
_VOCALES_FR = set("aeiouàâäéèêëïîôöùûüh")
_UNO_CENTAVO: Dict[str, str] = {"es": "un", "en": "one", "pt": "um", "fr": "un"}


def _de_fr(nombre: str) -> str:
    return f"d'{nombre}" if nombre[:1].lower() in _VOCALES_FR else f"de {nombre}"


def _apocopar_uno(idioma: str, cantidad: str, genero: str) -> str:
    if idioma == "es":
        return _apocopar_es(cantidad, genero)
    if idioma == "fr" and genero == "f":
        return _feminiser_fr(cantidad)
    return cantidad  # en: sin género; pt: ya viene con el género correcto


def a_letras(
    monto: float,
    moneda: str = "USD",
    idioma: str = "es",
    centavos: str = "fraccion",
    mayusculas: bool = True,
) -> str:
    """Convierte un monto a su representación en letras para documentos legales
    y financieros.

    :param monto: Cantidad a convertir. Debe ser >= 0.
    :param moneda: Código ISO 4217 de la moneda (por defecto ``"USD"``).
    :param idioma: ``"es"`` (por defecto), ``"en"``, ``"pt"`` o ``"fr"``. Si la
        moneda elegida todavía no tiene traducción a ese idioma, se lanza
        ``SpellMoneyError`` invitando a contribuir la traducción.
    :param centavos: ``"fraccion"`` (por defecto) escribe los centavos como
        fracción (50/100). ``"palabras"`` los escribe en letras.
    :param mayusculas: Si es ``True`` (por defecto) devuelve el resultado en
        mayúsculas.
    """
    if idioma not in IDIOMAS:
        raise SpellMoneyError(f"idioma '{idioma}' no soportado. Disponibles: {', '.join(IDIOMAS)}")
    if moneda not in MONEDAS:
        disponibles = ", ".join(sorted(MONEDAS))
        raise SpellMoneyError(f"moneda '{moneda}' no reconocida. Disponibles: {disponibles}")
    entrada_moneda = MONEDAS[moneda]
    if idioma not in entrada_moneda:
        raise SpellMoneyError(
            f"la moneda '{moneda}' todavía no tiene nombre en idioma '{idioma}'. "
            f"¡Ayuda buscada! Se acepta un pull request agregando "
            f"MONEDAS['{moneda}']['{idioma}'] en src/spellmoney/monedas.py."
        )
    if centavos not in ("fraccion", "palabras"):
        raise SpellMoneyError("centavos debe ser 'fraccion' o 'palabras'")
    if isinstance(monto, bool) or not isinstance(monto, (int, float)):
        raise SpellMoneyError("se esperaba un monto numérico")
    if monto < 0:
        raise SpellMoneyError("no se admiten montos negativos")

    entero = int(monto)
    parte_centavos = math.floor((monto - entero) * 100 + 0.5)
    if parte_centavos == 100:
        entero += 1
        parte_centavos = 0

    info = entrada_moneda[idioma]
    genero = info["genero"]
    motor = _MOTOR[idioma]

    if entero == 1:
        nombre_moneda = info["singular"]
        if idioma == "es":
            cantidad_en_letras = _apocopar_es("uno", genero)
        elif idioma == "en":
            cantidad_en_letras = "one"
        elif idioma == "pt":
            cantidad_en_letras = "uma" if genero == "f" else "um"
        else:
            cantidad_en_letras = "une" if genero == "f" else "un"
    else:
        nombre_moneda = info["plural"]
        cantidad_en_letras = _PALABRA_CERO[idioma] if entero == 0 else motor(entero, genero)
        cantidad_en_letras = _apocopar_uno(idioma, cantidad_en_letras, genero)
        escala = _ESCALA_QUE_PIDE_DE.get(idioma)
        ultima_palabra = cantidad_en_letras.split(" ")[-1]
        if escala and ultima_palabra in escala:
            nombre_moneda = _de_fr(nombre_moneda) if idioma == "fr" else f"de {nombre_moneda}"

    sing_centavos, plur_centavos = _CENTAVOS_PALABRA[idioma]
    conector = _CONECTOR[idioma]

    if centavos == "fraccion":
        sufijo_centavos = f"{conector} {parte_centavos:02d}/100"
    elif parte_centavos == 0:
        sufijo_centavos = f"{conector} {_PALABRA_CERO[idioma].upper()} {plur_centavos.upper()}"
    elif parte_centavos == 1:
        sufijo_centavos = f"{conector} {_UNO_CENTAVO[idioma].upper()} {sing_centavos.upper()}"
    else:
        texto = _apocopar_uno(idioma, motor(parte_centavos, "m"), "m")
        sufijo_centavos = f"{conector} {texto.upper()} {plur_centavos.upper()}"

    resultado = f"{cantidad_en_letras} {nombre_moneda} {sufijo_centavos}"
    return resultado.upper() if mayusculas else resultado.lower()
