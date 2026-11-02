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
| sexe amb espais, minúscules o escrit sencer | 38 | Quito espacios y normalizo mayúsculas/minúsculas; `Dona` → `D`, `Home` → `H`. El vacío sigue siendo null. |
| codi de pacient sense els zeros de l'esquerra (OLV) | 103 | Completo hasta 7 caracteres con ceros a la izquierda; el código sigue siendo texto. |
| un bacteri escrit de maneres diferents | 1.142 cultivos positivos (16 grafías) | Normalizo las grafías a los 5 códigos de bacteria; `NEG` y `negatiu` pasan a null porque no hay crecimiento. |
| S/I/R mal escrit, i `pendent` | 74 (14 `pendent`) | Quito espacios y normalizo mayúsculas y sinónimos (`sensible` → `S`, `resistent` → `R`); `pendent` pasa a null. |
| CMI amb `<=`, `>` o coma decimal | 1.383 filas únicas (814 con coma, 631 censuradas; 62 con las dos) | Convierto la coma decimal y quito el signo para obtener el valor numérico; `mic_censored` guarda si había `<=` o `>`. |
| diàmetre en centímetres (CSA) | 1.181 medidas | Multiplico por 10 solo los diámetros de CSA para expresarlos en milímetros. |

- `replace_strict` da `InvalidOperationError: incomplete mapping specified for replace_strict`; con el diccionario inicial, la primera grafía de los datos que no estaba cubierta era `staphylococcus aureus`.

## R3 · Validació

- Files rebutjades per fitxer i per motiu (una mostra amb dos motius, com surt):
  - `patients`: 4 por `data de naixement sentinella`.
  - `samples`: 2 por `data de presa fora del període; recepció abans de la presa` y 3 por `recepció abans de la presa`.
  - `antibiogram`: 2 por `diàmetre impossible`.
- Un exemple de missatge de Patito quan valides sense `split`:
  ```text
  1 validation error for Patient
  born
    4 rows does not match custom constraints. (type=value_error.rowvalue)
  ```

## R4 · Joins

- Mostres sense pacient, pacients sense mostra, proves sense mostra. D'on surt cada número:
  **17** muestras sin paciente (8 RBX, 5 OLV, 4 CSA), **0** pacientes sin muestra y **25** pruebas sin
  muestra (7 del laboratorio RBX, 18 de OLV). Salen de joins `how="anti"`. De las 17 muestras, 9
  tienen un código de paciente que no existe en `patients.csv` y 8 son de pacientes rechazados en R3
  (fecha de nacimiento centinela). Las 25 pruebas son todas de muestras que existen pero se
  rechazaron en R3: al quitar la muestra se quedan sin cultivo.
- Quantes mostres sense pacient tindries sense el `zfill` d'R2, i per què:
  **120** en lugar de 17. El sistema de OLV guardó el código de paciente como número y perdió los ceros
  de la izquierda (`0412345` → `412345`), y esos códigos ya no coinciden con los de `patients.csv`.
- Què passa si fas el join amb `hospitals.csv` tal com és, i per què `validate="m:1"`:
  OLV aparece dos veces (el nombre actual y el antiguo), así que cada muestra de OLV saldría
  duplicada, una con cada nombre. Con `validate="m:1"` Polars lanza un `ComputeError` en vez de
  multiplicar filas sin avisar; por eso antes me quedo con la primera fila de cada código
  (`unique_hospitals`).

## R5 · Agregacions

- L'hospital amb més proporció de cultius positius, i amb quina n:
  **RBX** (Hospital de Riubaix), con un **0,548** de positivos sobre n = 924 muestras (CSA 0,531 con
  n = 450; OLV 0,516 con n = 748).
- La setmana en què un hospital no va tenir cap cultiu positiu, i per què:
  **CSA, la semana del 16/02/2026**. Esa semana CSA no tiene ninguna muestra: el 0 sale porque no
  hubo cultivos, no porque todos fueran negativos. Sin la rejilla hospital × semana esa fila no
  aparecería.
- Pacients amb E. coli repetit que han passat de sensibles a resistents a la ciprofloxacina. Per què
  `min`/`max` de `sir` donaria una altra resposta:
  **12** de los 88 pacientes con dos o más resultados. `min`/`max` ordena S < I < R y no mira la
  fecha: un paciente que fue R y después S también daría min = S y max = R. Solo ordenando por
  `collected_at` se sabe cuál fue el primer resultado y cuál el último. En estos datos el número
  coincide (12), pero solo por casualidad.

## R6 · Estadística

- Temps de resposta: n = 2.104 muestras informadas (18 pendientes), media 45,56 h, mediana 38,6 h,
  desviación 29,28 h, Q1 26,6 h, Q3 53,8 h (IQR 27,2 h), vallas −14,2 h y 94,6 h, 145 valores fuera.
  Citaría la **mediana (38,6 h, con Q1–Q3 26,6–53,8 h)**: la distribución tiene una cola larga hacia
  la derecha (máximo 263,2 h) que sube la media unas 7 h, y a la mediana esa cola no la mueve.
- ¿Las muestras por encima de la valla alta son errores? **No.** De las 145, 141 son hemocultivos
  (`sang`) y 138 no han crecido: un hemocultivo negativo se incuba unos cinco días antes de darlo por
  negativo, por eso la mediana de `sang` es 109,3 h frente a 30 h de `orina`. Es el protocolo, no un
  error de datos. Las otras 4 (3 `ferida`, 1 `esput`) quedan justo por encima de la valla
  (97,8–101,6 h) y son tiempos posibles. La valla encuentra valores inusuales, no valores falsos.
- r(diámetro, log2 CMI) = −0,924 con n = 345 (E. coli y ciprofloxacino, pruebas con las dos
  medidas). El log2 porque la CMI se mide en diluciones dobles (0,25, 0,5, 1, 2…): en log2 cada paso
  vale 1 y la relación con el diámetro es lineal. Es negativa porque una bacteria más sensible hace un
  halo más grande y se detiene con menos antibiótico: diámetro grande, CMI pequeña.

## R7 · Pseudonimització i anonimització

- Per què un SHA-256 del codi de pacient sense clau no protegeix ningú (quant trigaries a desfer-lo):
  Solo hay 10⁷ códigos posibles (7 cifras). Cualquiera puede calcular el SHA-256 de todos y montar una
  tabla hash → código: en mi portátil 1 millón de hashes tarda 1,66 s, así que los 10 millones son
  **unos 17 segundos**. Con HMAC hace falta la clave para calcular un solo pseudónimo.
- Per què el pseudònim s'ha de calcular sobre el codi de 7 xifres:
  Porque OLV escribió algunos códigos sin los ceros de la izquierda (`412345` en vez de `0412345`).
  Si no se completan a 7 cifras, el mismo paciente tendría dos pseudónimos distintos y sus muestras ya
  no se podrían enlazar. Por eso `pseudonym` hace `zfill(7)` antes del HMAC.
- On és la clau a la teva màquina virtual, i què passa si es filtra:
  En `/etc/ecb-microbiology.env` (variable `ECB_MICROBIOLOGY_KEY`), generada en la máquina con
  `openssl rand -hex 32` por `cloud-init`, con permisos `640` (root y el grupo `ecb`), y systemd la
  pasa al servidor con `EnvironmentFile`. Nunca está en el código ni en el repositorio. Si se filtra,
  cualquiera puede calcular el HMAC de los 10⁷ códigos y deshacer todos los pseudónimos en segundos:
  habría que generar una clave nueva y volver a publicar.
- k-anonimitat segons l'amplada de la franja d'edat (zona de 4 xifres):

| franja | files publicades | persones suprimides | % |
|---:|---:|---:|---:|
| 10 | 1.297 | 348 | 38,8 |
| 20 | 1.696 | 172 | 19,2 |
| 30 | 1.756 | 151 | 16,9 |

  El % es sobre las 896 personas de `cultures`. En las tres franjas la k final es 5.
- La franja que has triat, i per què:
  **20 años**. Con 10 se suprime casi el 40 % de las personas, demasiado. Con 30 solo se salvan 21
  personas más, pero las franjas (0–29, 30–59, 60–89) mezclan niños con adultos jóvenes y adultos con
  ancianos, y la edad deja de ser útil para el análisis.
- La publicació és anònima o pseudonimitzada? Per què:
  **Seudonimizada.** El campo `patient` es un HMAC con clave: quien tenga la clave puede recalcular el
  pseudónimo de cada código y volver a la persona, y además enlaza todas las muestras de un mismo
  paciente. Mientras exista la clave siguen siendo datos personales. El k ≥ 5 reduce el riesgo, pero
  no lo convierte en anónimo.

## R8–R9 · Servidor i pàgina

- Bytes de `/api/points` i de `/api/tat.svg` (`curl -s -o /dev/null -w '%{size_download}'`):
  `/api/points` **14.596 bytes** (345 puntos, solo `mic_log2` y `diameter`) y `/api/tat.svg`
  **5.154 bytes** (19 barras de 12 h). Medido con el cliente de pruebas de `oxid_server`, sin
  compresión.
- Per què l'histograma es dibuixa al servidor i la dispersió al navegador:
  El histograma es una imagen fija: el servidor ya tiene los datos, lo dibuja una vez como SVG y la
  página solo pone un `<img>`, sin Python ni datos en el navegador. La dispersión es interactiva (el
  recuadro para seleccionar puntos y contar cuántas pruebas hay dentro): eso tiene que pasar en el
  navegador, así que se envían los puntos, y solo las dos columnas que dibuja.

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
