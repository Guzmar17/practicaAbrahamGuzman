# Informe · ECB A1-P1

Nom i cognoms:
URL pública:

Cada resposta porta **el número** (copiat de `uv run python -m microbiology.pipeline` o d'un test) i
**una frase** que digui què vol dir o per què has decidit el que has decidit.

## R1 · Càrrega

- Files llegides de cada fitxer, i de cada hospital:
- Què fa `pl.concat` si les tres taules de mostres no tenen les mateixes columnes en el mateix ordre (el missatge):
- Per què `codi_pacient` i `codi_postal` no poden ser enters (un exemple de la teva sortida):

## R2 · Neteja

Per a cada correcció: què has trobat, quantes files, què has decidit.

| problema | files | decisió |
|---|---:|---|
| sexe amb espais, minúscules o escrit sencer | | |
| codi de pacient sense els zeros de l'esquerra (OLV) | | |
| un bacteri escrit de maneres diferents | | |
| S/I/R mal escrit, i `pendent` | | |
| CMI amb `<=`, `>` o coma decimal | | |
| diàmetre en centímetres (CSA) | | |

- Quin error dona `replace_strict` amb una grafia que no és al diccionari, i quina era:

## R3 · Validació

- Files rebutjades per fitxer i per motiu (una mostra amb dos motius, com surt):
- Un exemple de missatge de Patito quan valides sense `split`:

## R4 · Joins

- Mostres sense pacient, pacients sense mostra, proves sense mostra. D'on surt cada número:
- Quantes mostres sense pacient tindries sense el `zfill` d'R2, i per què:
- Què passa si fas el join amb `hospitals.csv` tal com és, i per què `validate="m:1"`:

## R5 · Agregacions

- L'hospital amb més proporció de cultius positius, i amb quina n:
- La setmana en què un hospital no va tenir cap cultiu positiu, i per què:
- Pacients amb E. coli repetit que han passat de sensibles a resistents a la ciprofloxacina. Per què
  `min`/`max` de `sir` donaria una altra resposta:

## R6 · Estadística

- Temps de resposta: n, mitjana, mediana, desviació, tanques. Quina citaries i per què:
- Les mostres per sobre de la tanca alta són errors? Com ho saps (mira `statistic.outliers`):
- r(diàmetre, log2 CMI) i la seva n. Per què el log2, i per què és negativa:

## R7 · Pseudonimització i anonimització

- Per què un SHA-256 del codi de pacient sense clau no protegeix ningú (quant trigaries a desfer-lo):
- Per què el pseudònim s'ha de calcular sobre el codi de 7 xifres:
- On és la clau a la teva màquina virtual, i què passa si es filtra:
- k-anonimitat segons l'amplada de la franja d'edat (zona de 4 xifres):

| franja | files publicades | persones suprimides | % |
|---:|---:|---:|---:|
| 10 | | | |
| 20 | | | |
| 30 | | | |

- La franja que has triat, i per què:
- La publicació és anònima o pseudonimitzada? Per què:

## R8–R9 · Servidor i pàgina

- Bytes de `/api/points` i de `/api/tat.svg` (`curl -s -o /dev/null -w '%{size_download}'`):
- Per què l'histograma es dibuixa al servidor i la dispersió al navegador:

## R10 · Desplegament

- Mida de la màquina, disc i oferta de la subscripció (`az account show`):
- Què has de fer quan s'acabi la correcció perquè no costi res:

## R11 · Antibiograma acumulat

- L'antibiograma acumulat d'E. coli (`resistance.cumulative`), copiat:
- Aïllaments d'E. coli amb i sense la regla del primer aïllament. Per què la regla:
- Quina taxa no es publica a K. pneumoniae, i per què 30:
- Quin antibiòtic triaries per a una infecció d'orina per E. coli a l'Olivar, segons la taula, i què
  no et diu la taula:

## R12 · Taxes publicades

- Què rebutja el model `Rate` (un exemple de missatge):
- Per què un hospital no té barra en algun antibiòtic del gràfic:
