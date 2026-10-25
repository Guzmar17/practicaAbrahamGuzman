# ecb-microbiology

**ECB · A1-P1.** Mig any d'una xarxa de microbiologia inventada, tres hospitals i un laboratori:
carregar-ho, netejar-ho, validar-ho, ajuntar-ho, resumir-ho, calcular-ne l'antibiograma acumulat,
pseudonimitzar-ho i publicar-ne només el que es pot publicar, en una pàgina Oxid servida per
oxid-server en una màquina virtual gratuïta d'Azure.

L'enunciat (requisits, punts i criteris) és al Moodle. Aquest repositori és la bastida: l'estructura,
les signatures, les proves i el desplegament ja hi són. Tu escrius el cos de cada funció que diu
`raise NotImplementedError("Rn")` i cada `TODO Rn`.

## Engegar

```sh
uv sync                                       # Python 3.14, oxid, polars, patito, pytest
uv run pytest                                 # les proves d'acceptació, una per requisit
uv run pytest tests/test_r1_load.py           # només les d'un requisit
uv run python -m microbiology.pipeline        # els números que demana INFORME.md
```

La pàgina i el servidor, mentre treballes (cal una clau, mira R7):

```sh
export ECB_MICROBIOLOGY_KEY=$(uv run python -c "import secrets; print(secrets.token_hex(32))")
OXID_SERVER_RUNTIME=cpython uv run oxid serve app --server server.py --port 8600
```

`http://127.0.0.1:8600`. El servidor executa tota l'anàlisi en arrencar: fins que R1–R7 i R11 no
funcionin, no arrenca, i l'error que veus és el primer `NotImplementedError` que troba.

## On és cada requisit

| | fitxer | prova |
|---|---|---|
| R1 càrrega | `microbiology/load.py` | `tests/test_r1_load.py` |
| R2 neteja | `microbiology/clean.py` | `tests/test_r2_clean.py` |
| R3 validació | `microbiology/model.py` | `tests/test_r3_model.py` |
| R4 joins | `microbiology/combine.py` | `tests/test_r4_combine.py` |
| R5 agregacions | `microbiology/summary.py` | `tests/test_r5_summary.py` |
| R6 estadística | `microbiology/statistic.py` | `tests/test_r6_statistic.py` |
| R7 privacitat | `microbiology/privacy.py` | `tests/test_r7_privacy.py` |
| R8 servidor | `server.py` | `tests/test_r8_server.py` |
| R9 pàgina | `app/app.py` | `tests/test_r9_page.py` |
| R10 desplegament | `deploy/` | la URL pública |
| R11 antibiograma acumulat | `microbiology/resistance.py` | `tests/test_r11_resistance.py` |
| R12 taxes publicades | `microbiology/resistance.py` (`Rate`), `server.py`, `app/app.py` | `tests/test_r12_rate.py` |

`microbiology/pipeline.py` els encadena en ordre i ja està fet: llegeix-lo primer. Les dades i què
vol dir cada columna: `data/README.md`. No canviïs els fitxers de `data/` ni les proves.

## Desplegar a Azure (R10)

Cal [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) i una subscripció
**Azure for Students** (`az login`). Des de la carpeta del repositori, en un terminal bash
(macOS, Linux, WSL o Git Bash):

```sh
deploy/azure.sh ecb-<nom>-<cognom>            # la màquina: B1s, disc P6 de 64 GiB, ports 80 i 443
ssh azureuser@ecb-<nom>-<cognom>.francecentral.cloudapp.azure.com cloud-init status --wait
deploy/push.sh ecb-<nom>-<cognom>.francecentral.cloudapp.azure.com
```

`push.sh` envia l'últim commit (no el que no has confirmat), i a la màquina `install.sh` crea
l'entorn amb `uv sync --frozen`, construeix la pàgina, reinicia el servei i posa Caddy davant amb
HTTPS. Cada canvi posterior: commit i `deploy/push.sh <host>` una altra vegada.

La clau de pseudonimització es crea **a la màquina** en el primer arrencada
(`/etc/ecb-microbiology.env`) i no surt mai d'allà ni entra al repositori.

Si encara tens la màquina de la pràctica `ecb-emergency`, esborra-la abans
(`az group delete -n rg-ecb --yes`): només una màquina és gratuïta.

Què costa: la màquina i el disc entren en les 750 hores gratuïtes del primer any si són
**exactament** aquests; l'adreça IP pública es paga des de la primera hora (uns 3 € al mes).
Quan la pràctica estigui corregida:

```sh
az group delete -n rg-ecb --yes
```

## Ús de la IA

L'enunciat ho explica: primer tu, després que revisi. Has de poder explicar i reescriure sense
ajuda tot el que lliuris.
