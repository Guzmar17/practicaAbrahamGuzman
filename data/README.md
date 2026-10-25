# Les dades

**Inventades.** Cap persona d'aquests fitxers existeix, ni cap dels tres hospitals: els noms surten
de dues llistes a l'atzar i els números d'un generador amb llavor fixa. Tracta-les, però, com si
fossin reals: és l'exercici.

Mig any (5 de gener – 5 de juliol de 2026, 26 setmanes) de la Xarxa de microbiologia del Riubaix:
tres hospitals prenen mostres (orina, sang, ferides, esput), el laboratori de cada hospital les
cultiva, i quan hi creix un bacteri en fa l'**antibiograma**: quins antibiòtics el maten i quins no.
Cada hospital té el seu sistema, i cada sistema té els seus costums.

| fitxer | sistema | separador | files | què és una fila |
|---|---|---|---:|---|
| `patients.csv` | índex de pacients de la xarxa | `;` | 900 | un pacient |
| `samples_rbx.csv` | Hospital de Riubaix | `,` | 933 | una mostra |
| `samples_olv.csv` | Hospital de l'Olivar (el sistema antic) | `;` | 757 | una mostra |
| `samples_csa.csv` | Hospital de Castellsalat | `,` | 454 | una mostra |
| `antibiogram.csv` | el laboratori de la xarxa | `,` | 6 854 | un antibiòtic provat en una mostra |
| `hospitals.csv` | la xarxa | `,` | 4 | un hospital |

## `patients.csv` (en català)

| columna | significat |
|---|---|
| `codi_pacient` | 7 xifres. **Un codi**, no un número |
| `nom`, `cognoms` | identificadors directes |
| `data_naixement` | dd/mm/aaaa |
| `sexe` | `D` dona, `H` home, tal com el va teclejar el taulell |
| `codi_postal` | 5 xifres, tots comencen per `08` |

## `samples_rbx.csv`, `samples_csa.csv`

| columna | significat |
|---|---|
| `sample_id` | la mostra: `RBX26-00001`, `CSA26-00001` |
| `patient` | el codi del pacient |
| `specimen` | `orina`, `sang` (hemocultiu), `ferida`, `esput` |
| `collected_at` | quan es va prendre la mostra |
| `received_at` | quan va arribar al laboratori |
| `reported_at` | quan el laboratori en va donar el resultat; buit: encara hi és |
| `organism` | el bacteri que hi ha crescut; buit o `NEG`: no hi ha crescut res |

Riubaix escriu les dates `aaaa-mm-dd hh:mm` i el nom sencer del bacteri (*Escherichia coli*);
Castellsalat, `aaaa-mm-ddThh:mm:ss` i l'abreviatura en majúscules (`E.COLI`).

## `samples_olv.csv` (el sistema antic de l'Olivar, en català)

Les mateixes columnes amb un altre nom: `mostra`, `pacient`, `tipus_mostra`, `data_presa`,
`data_recepcio`, `data_informe`, `microorganisme`. Dates `dd/mm/aaaa hh:mm`, `n/a` si no hi ha
informe encara, `negatiu` si no hi ha crescut res, el bacteri abreujat (`E. coli`). El sistema
desa el pacient com a número.

## `antibiogram.csv`

| columna | significat |
|---|---|
| `sample_id` | la mostra |
| `lab` | el laboratori que l'ha llegit: `RBX`, `OLV`, `CSA` |
| `antibiotic` | codi: `AMP` ampicil·lina, `AMC` amoxicil·lina-clavulànic, `CTX` cefotaxima, `CIP` ciprofloxacina, `GEN` gentamicina, `SXT` cotrimoxazole, `MEM` meropenem, `CAZ` ceftazidima, `OXA` oxacil·lina, `ERY` eritromicina, `CLI` clindamicina, `VAN` vancomicina |
| `mic` | concentració mínima inhibitòria, mg/L: la dosi més petita que atura el bacteri. `<=0.03`: com a molt això; `>64`: més que la dilució més alta. L'Olivar escriu coma decimal. Buit, `NA` o `-`: no consta |
| `diameter` | diàmetre del halo al voltant del disc d'antibiòtic (com més gran, més sensible), només Riubaix i Castellsalat i només en gramnegatius |
| `sir` | la interpretació: `S` sensible, `I` sensible augmentant la dosi, `R` resistent, tal com la teclegen; `pendent` si encara no hi és |

## `hospitals.csv`

`code`, `name`, `town`, `beds`. La llista de la xarxa, tal com la mantenen.
