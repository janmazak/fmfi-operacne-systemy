# Operačné systémy 1-INF-171/15

Cvičenia k predmetu _Operačné systémy_ pozostávajú zo samostatnej práce (programovanie, štúdium dokumentácie) a prípadných krátkych individuálnych konzultácií (dohadujú sa najmä e-mailom).

V prípade ľubovoľných otázok na tému domácich úloh (napr. chyba či nejasnosť v zadaní) sa, prosím, ozvite čím skôr. Napíšte mi aj v prípade, že si s nejakým problémom dlhšie neviete poradiť.

Body za cvičenia sa získavajú len za domáce úlohy:
* [DÚ1 --- synchronizácia vlákien](du1/du1.md) (10 b)
* [DÚ2 --- alokátor pamäte](du2/du2.md) (10&ndash;12 b)
* [DÚ3 --- súborový systém](du3/du3.md) (10&ndash;14 b)

Úlohy je možné odovzdať viackrát (najviac raz denne), ráta sa najlepšie zo získaných hodnotení.
Neskoré odovzdanie domácej úlohy vedie k strate 2 b za každý začatý deň omeškania.
V odôvodnených prípadoch môže cvičiaci rozhodnúť o zmene termínu odovzdania úlohy.

#### Korektnosť kódu

Programuje sa v C, čo je jazyk náchylný na vznik chýb. Naučte sa preto používať automatizované nástroje na ich odchytávanie.
* statická analýza: https://clang-analyzer.llvm.org/
* dynamická analýza: https://valgrind.org/

#### Čitateľnosť kódu

Aj keď vaše programy po ohodnotení domácich úloh už nebude potrebné čítať a udržiavať, skúste ich písať štruktúrovane a čitateľne. Kód netreba vyšperkovať, siahodlho komentovať, ani vyrovnať všetky záhyby, ale nemal by vyzerať odpudivo. Snažíte sa o opak tohto tu: [Obfuscated C Code Contest](https://www.ioccc.org/years.html#2020).

Mali by ste si v tomto smere vyvinúť automatický návyk, preto nepoľavujte ani pri domácich úlohách. Začnite použitím automatizovaného formátovača, napr. [`astyle`](https://iq.opengenus.org/astyle-c/).
