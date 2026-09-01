# Contribuir a spellmoney (Python)

*[Read this in English](#contributing-to-spellmoney-python-english)*

Gracias por tu interés en mejorar `spellmoney`. Si el cambio es sobre la lógica de idiomas o el catálogo de monedas, tenlo en cuenta: existe un [puerto a JavaScript](https://github.com/brandriver-bit/spellmoney-js) que comparte los mismos datos y debe reflejar el mismo comportamiento, así que conviene aplicarlo en ambos para mantenerlos sincronizados.

## Antes de nada

El repositorio corre automáticamente las pruebas (`pytest`) en cada Pull Request, sobre Python 3.9 a 3.13. Si tu cambio hace fallar una prueba, o le faltan pruebas, te va a aparecer marcado en rojo antes de que se revise.

## Formas de ayudar

### 1. Reportar un error o pedir algo

Abre un [Issue](../../issues) describiendo qué esperabas que pasara y qué pasó en realidad.

### 2. Agregar o corregir el nombre de una moneda

Los nombres de moneda viven en `src/spellmoney/monedas.py`. Para agregar una moneda en un idioma que todavía no la tiene, agrega la entrada correspondiente ahí siguiendo el mismo formato (`singular`, `plural`, `genero`).

### 3. Agregar un idioma nuevo

Cada idioma en `src/spellmoney/__init__.py` sigue el mismo patrón: una función `numero_a_letras_xx(n)`, una entrada en `IDIOMAS`, y conectarlo en `_MOTOR`, `_PALABRA_CERO`, `_CONECTOR`, `_CENTAVOS_PALABRA` y, si aplica, `_ESCALA_QUE_PIDE_DE`. Solo se acepta si la gramática está verificada, no adivinada.

## Cómo enviar tu cambio

```bash
git clone https://github.com/TU-USUARIO/spellmoney.git
cd spellmoney
pip install -e ".[dev]"

git checkout -b agrega-moneda-XXX

# haz tu cambio, agrega tu prueba en tests/test_spellmoney.py
pytest

git add -A
git commit -m "Agrega AFN en portugués"
git push origin agrega-moneda-XXX
```

Y abre un Pull Request desde GitHub.

---

# Contributing to spellmoney (Python) (English)

*[Leer esto en español](#contribuir-a-spellmoney-python)*

Thanks for your interest in improving `spellmoney`. If the change is about language logic or the currency catalog, keep in mind there's a [JavaScript port](https://github.com/brandriver-bit/spellmoney-js) that shares the same data and must behave identically, so it's best to apply the change to both and keep them in sync.

## Before anything else

The repository automatically runs the test suite (`pytest`) on every Pull Request, across Python 3.9 through 3.13. If your change breaks a test, or is missing one, it'll show up red before review.

## Ways to help

### 1. Report a bug or request something

Open an [Issue](../../issues) describing what you expected versus what actually happened.

### 2. Add or fix a currency name

Currency names live in `src/spellmoney/monedas.py`. To add a currency for a language that doesn't have it yet, add the matching entry there following the same shape (`singular`, `plural`, `genero`).

### 3. Add a new language

Every language in `src/spellmoney/__init__.py` follows the same pattern: a `numero_a_letras_xx(n)` function, an entry in `IDIOMAS`, and wiring it into `_MOTOR`, `_PALABRA_CERO`, `_CONECTOR`, `_CENTAVOS_PALABRA`, and `_ESCALA_QUE_PIDE_DE` if it applies. Only accepted if the grammar is verified, not guessed.

## How to submit your change

```bash
git clone https://github.com/YOUR-USERNAME/spellmoney.git
cd spellmoney
pip install -e ".[dev]"

git checkout -b add-currency-XXX

# make your change, add your test in tests/test_spellmoney.py
pytest

git add -A
git commit -m "Add AFN in Portuguese"
git push origin add-currency-XXX
```

Then open a Pull Request on GitHub.
