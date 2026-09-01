# spellmoney

**Convierte montos numéricos a letras, con el formato exacto que exigen los documentos legales y financieros** — cheques, facturas, recibos y contratos: `CIENTO VEINTICINCO DÓLARES CON 50/100`.

[![PyPI](https://img.shields.io/pypi/v/spellmoney?logo=pypi&logoColor=white&color=3775A9&label=pypi)](https://pypi.org/project/spellmoney/)
![Python](https://img.shields.io/badge/Python-%3E%3D3.9-3776AB?logo=python&logoColor=white)
![Tests](https://github.com/brandriver-bit/spellmoney/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencias-cero-brightgreen)
![Idiomas](https://img.shields.io/badge/idiomas-es%20%7C%20en%20%7C%20pt%20%7C%20fr-blue)

Existe también el [puerto a TypeScript/JavaScript](https://github.com/brandriver-bit/spellmoney-js) — misma lógica, mismos datos de moneda, mismo resultado exacto — para quien trabaja en Node.

## Instalación

```bash
pip install spellmoney
```

## Uso

```python
from spellmoney import a_letras

a_letras(125.50)
# 'CIENTO VEINTICINCO DÓLARES CON 50/100'

a_letras(1, moneda="GTQ")
# 'UN QUETZAL CON 00/100'

a_letras(21000000, moneda="EUR")
# 'VEINTIÚN MILLONES DE EUROS CON 00/100'

a_letras(2, moneda="GBP", mayusculas=False)
# 'dos libras esterlinas con 00/100'

a_letras(10.50, centavos="palabras")
# 'DIEZ DÓLARES CON CINCUENTA CENTAVOS'

a_letras("125.50")
# 'CIENTO VEINTICINCO DÓLARES CON 50/100'  (lectura decimal exacta)
```

### Otros idiomas

```python
a_letras(125.50, idioma="en")
# 'ONE HUNDRED TWENTY-FIVE DOLLARS AND 50/100'

a_letras(125.50, idioma="pt", moneda="BRL")
# 'CENTO E VINTE E CINCO REAIS E 50/100'

a_letras(125.50, idioma="fr", moneda="EUR")
# 'CENT VINGT-CINQ EUROS ET 50/100'
```

### Solo el número, sin moneda

```python
from spellmoney import (
    numero_a_letras,
    numero_a_letras_en,
    numero_a_letras_pt,
    numero_a_letras_fr,
)

numero_a_letras(1000000)        # 'un millón'
numero_a_letras(1000000000)     # 'mil millones'   (¡no "un billón"!)
numero_a_letras(1000000000000)  # 'un billón'

numero_a_letras_en(1000000000)  # 'one billion'    (escala corta del inglés)

numero_a_letras_pt(21, "f")     # 'vinte e uma'    (concordancia de género)

numero_a_letras_fr(71)          # 'soixante et onze'  (base vigesimal del francés)
```

## Monedas soportadas

**Las 154 divisas activas del estándar ISO 4217.** La cobertura varía según el idioma:

| Idioma | Divisas cubiertas |
|---|---|
| `es` (español) | 154 — todas |
| `en` (inglés) | 154 — todas |
| `pt` (portugués, Brasil) | 46 — países lusófonos + las divisas más usadas del mundo |
| `fr` (francés) | 45 — países francófonos + las divisas más usadas del mundo |

Si se pide una combinación de moneda e idioma que aún no existe, `a_letras` lanza `SpellMoneyError` con un mensaje explicando exactamente qué falta, en vez de fallar en silencio.

### 🙋 Ayuda buscada

Portugués y francés todavía tienen huecos en divisas regionales. Los pasos exactos para contribuir (fork, rama, pruebas, Pull Request) están en [`CONTRIBUTING.md`](CONTRIBUTING.md) — en español e inglés.

## API

| Función | Descripción |
|---|---|
| `a_letras(monto, moneda="USD", idioma="es", centavos="fraccion", mayusculas=True)` | Convierte un monto con nombre de moneda. `monto` puede ser `int`, `float`, `Decimal` o cadena decimal. |
| `numero_a_letras(n)` | Solo el número, en español. |
| `numero_a_letras_en(n)` | Solo el número, en inglés. |
| `numero_a_letras_pt(n, genero="m")` | Solo el número, en portugués. |
| `numero_a_letras_fr(n)` | Solo el número, en francés. |
| `MONEDAS` | Catálogo de las 154 divisas ISO 4217. |
| `IDIOMAS` | `("es", "en", "pt", "fr")`. |
| `SpellMoneyError` | Error lanzado ante un monto, moneda o idioma inválidos. |

Parámetros de `a_letras`:

- `monto` — `int`, `float`, `Decimal` o cadena decimal (`"125.50"`).
- `moneda` — código ISO 4217. Por defecto `"USD"`.
- `idioma` — `"es"`, `"en"`, `"pt"` o `"fr"`. Por defecto `"es"`.
- `centavos` — `"fraccion"` escribe `50/100`; `"palabras"` escribe `CINCUENTA CENTAVOS`.
- `mayusculas` — `True` devuelve el resultado en mayúsculas; `False`, en minúsculas.

## Rango soportado

Enteros de `0` a `999,999,999,999,999`. Un monto fuera de ese rango lanza `SpellMoneyError`, igual que un monto negativo, una moneda no reconocida o un idioma no soportado.

## Redondeo y precisión

Un monto se puede pasar como `float`, como `Decimal` o como cadena decimal, y la diferencia importa:

- **Cadena o `Decimal`** — `a_letras("125.50")`, `a_letras(Decimal("125.50"))`: los dígitos se leen tal como fueron escritos, sin pasar por punto flotante. El redondeo del tercer decimal en adelante es half-up exacto, así que `"2.675"` da `68/100`. Es la vía recomendada cuando el monto viene de una base de datos, un formulario o un archivo.
- **`float`** — `a_letras(125.50)`: los montos de **dos decimales** se convierten de forma exacta. Verificado sobre el millón de montos de `0.00` a `9999.99`: ninguna diferencia frente a aritmética decimal exacta. Con **tres o más decimales**, el empate exacto se resuelve según el valor binario que el `float` almacena realmente, que puede quedar apenas por debajo del decimal escrito: `2.675` da `67/100`. Es una propiedad del tipo `float`, no de esta librería.

## Desarrollo

```bash
git clone https://github.com/brandriver-bit/spellmoney.git
cd spellmoney
pip install -e ".[dev]"
pytest
```

## Licencia

MIT — ver [`LICENSE`](LICENSE).
