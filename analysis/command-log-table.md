# Příkazy a výsledky výbojů (GM#54761–54785, + GM#49921)

Zdroj: chat log `Plasma current stabilization strategy.md` (export 2026-11-07) a MCP data pro GM#54785 (`conductor/discharge.json`).

Legenda:
- **Bt/CD** = `t_Bt` / `t_cd` z `--infrastructure.bt_ecd` (µs)
- **Stab. konce** = koncové body stabilizačních waveforem (radiální / vertikální / proudová)
- **Plasma / Flattop** = hodnoty z logu (`t_plasma_duration` / `t_plasma_qs_duration`)
- **Flattop real** = výpočet modelu z `ql_I_p.csv` (80 % špičky proudu); u některých shotů nedostupné
- „?“ = v logu nebo MCP není ověřitelný údaj

Pozn.: Společné pro všechny výboje z řady 54761–54781 jsou `U_Bt=1100`, `U_cd=450`, `p_H=10`, `U_v=39`, `style='standard'`, `S_gas='H'`.

| Shot | Bt / CD (µs) | Stab. konce (radiální / vertikální / proud) | Plasma (ms) | Flattop (ms) | Flattop real (ms) | Změny oproti předchozímu | Komentář (kdo změnil co) |
|---|---|---|---|---|---|---|---|
| GM#54761 | 5000 / 6000 | 50000,16 / 50000,-16 / 55000,14 | 35.460 | 15.282 | 20.824 | — | Referenční sada, vzorový příkaz uživatele (54586) s časováním 5000/6000. Model navrhl pouze komentář `AI4tG`. |
| GM#54762 | 5000 / 6000 | ? | — (vakuum) | — | — | Bez změn | Výboj bez plazmatu. |
| GM#54763 | 5000 / 6000 | ? | 27.073 | 10.312 | 13.464 | Bez změn (podle modelu) | Model nic neměnil. |
| GM#54764 | 5000 / 6000 | ? | 36.126 | 15.891 | 21.399 | Bez změn (podle modelu) | Model nic neměnil. |
| GM#54765 | 5000 / 6000 | ? | 27.013 | 7.169 | 16.788 | Bez změn (podle modelu) | Model nic neměnil. |
| GM#54766 | 5000 / 6000 | 50000,16 / 50000,-16 / 55000,14 | 40.519 | 15.267 | 23.411 | Model navrhl prodloužení proudového plató 55→65 ms (pro další shot) | Poslední čísla 54761–54766 jsou referencí; navržená změna 55→65 ms není v logu potvrzena jako vystřelená. |
| GM#54767 | ? | ? | ? | ? | nedostupné | ? | Surová data nedostupná. |
| GM#54768 | ? | ? | ? | ? | nedostupné (raw) | ? | Surová data nedostupná. |
| GM#54769 | ? | ? | ? | ? | 19.463 | ? | — |
| GM#54770 | ? | ? | ? | ? | nedostupné (raw) | ? | — |
| GM#54771 | ? | ? | ? | ? | 21.805 | ? | — |
| GM#54772 | ? | ? | ? | ? | 2.735 | ? | Velmi krátký výboj; příkaz v logu není. |
| GM#54773 | ? | ? | ? | ? | 5.249 | ? | Krátký výboj; příkaz v logu není. |
| GM#54774 | **5000 / 6000** | 50000,16 / 50000,-16 / 55000,14 | 27.193 | 8.069 | 15.182 | Poslední shot s původním časováním | Uživatel ještě nezměnil časování; model následně navrhl 1000/1200 (uživatelem požadováno: „Try 1000 and 1200“). |
| GM#54775 | **1000 / 1200** | 50000,16 / 50000,-16 / 55000,14 | 40.718 | 19.864 | nedostupné (raw) | Časování 5000/6000 → 1000/1200 (uživatel požadoval; model zapsal) | Model změnil jen `t_Bt` a `t_cd` a komentář; stabilizace beze změny. |
| GM#54776 | 1000 / 1200 | 50000,16 / 50000,-16 / 55000,14 (?) | 45.636 | 23.708 | nedostupné (raw) | Bez dalších změn | Nejlepší výsledek; model jej označil za referenci. Příkaz s prodlouženými konci (60/65 ms) model navrhl, ale není jisté, zda byl vystřelen. |
| GM#54777 | 1000 / 1200 | 50000,16 / 50000,-16 / 55000,14 (?) | 40.436 | 18.833 | nedostupné (raw) | Bez změn | Model: 1000/1200 potvrzeno. |
| GM#54778 | 1000 / 1200 | nulové body (přesné hodnoty v logu nejsou jednoznačné) | 4.759 | 1.138 | 0.769 | **Přidány nulové koncové body** (model navrhl; uživatel zadal „End stabilisation in zero“) | Krátký výboj. Model původně přisoudil příčinu nulovým bodům, později to odvolal (příčina nezjištěna). |
| GM#54779 | 1000 / 1200 | 50000,16 / 50000,-16 / 55000,14 | 27.396 | 8.542 | 11.399 | **Uživatel vrátil původní příkaz** (řádek 540 logu, „previous command that worked“) — model jen zopakoval přesně | Horší výsledek se stejným příkazem → velká variabilita. |
| GM#54780 | 1000 / 1200 | ? | ? | ? | 13.239 | ? | Model později odmítl; plasma v logu chybí. |
| GM#54781 | 1000 / 1200 | 50000,16 / 50000,-16 / 55000,14 | 28.001 | 8.226 | 11.400 | Bez změn (model: „nearly identical“) | Stejný příkaz jako 54779. |
| GM#54782–54784 | ? | ? | ? | ? | ? | ? | V logu nejsou; přesný příkaz neznámý. |
| **GM#54785** | **1000 / 1200** | **radiální** `1000,0;4000,0;15000,0;40000,16;50000,16;65000,0`; **vertikální** `1000,0;8000,0;40000,-16;50000,-16;65000,0`; **proud** `1000,0;18000,0;20000,1;22000,3;24000,5;33000,14;55000,14;65000,0` | 50.913 | ? | ? | **Nulové body na 65 ms** u všech tří waveforem (oproti 54781: přidáno `65000,0`) | Zdroj změny: kombinace uživatelova požadavku „max 65000“ a modelového návrhu nulových bodů. Přesně co uživatel poslal, nelze z logu rozlišit. Napětí CD 450 V (MCP). Plasma podle logu, Ip_max 11.974 kA. |
| GM#49921 (referenční, jiná éra) | 0 / 250 | ? (`PositionStabilization/Default`, `CurrentStabilization/Default`) | 50.124 | ? | ? | Jiná infrastruktura (`Basic`), napětí Bt/CD 900/350 V, tlak 15 | Ip_max 11.107 kA; nelze přímo srovnávat s řadou 54761–54785. |

## Shrnutí změn

**Uživatel:**
- 54586 vzorový příkaz (`t_Bt=5000`, `t_cd=6000`, stabilizace 50/55 ms) → základ pro 54761–54766.
- Přechod na 1000/1200 µs od GM#54775 (uživatelem zadáno).
- Návrat k „previous command that worked“ od GM#54779 (uživatel vrátil model na osvědčený příkaz).
- Požadavek nulových koncových bodů a limit 65000 µs (ovlivnil GM#54778 a GM#54785).

**Model:**
- Komentáře `AI4tG plasma stabilisation - …` (všechny návrhy).
- Návrhy časování 1000/1200 µs (uživatelem požadováno).
- Návrhy prodloužení plató (60/65 ms) a nulových bodů; část se do provozu dostala (GM#54778, GM#54785).
- Odstranění a opětovné přidání `--infrastructure.triggering` na žádost uživatele.

**Nejisté:** přesné příkazy GM#54762–54773, 54780 a 54782–54784 nejsou v logu, takže jejich sloupce jsou prázdné nebo s „?“.
