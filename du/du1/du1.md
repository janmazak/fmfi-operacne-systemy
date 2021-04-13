# Domáca úloha 1

Vašou úlohou je naprogramovať síce zjednodušenú, ale viacvláknovú verziu UNIXového programu `cat`. Účelom programu je všetky dáta, ktoré dostane na štandardný vstup (a žiadne iné), vypísať na štandardný výstup v presne tom istom poradí. Keď sa vstup skončí, program má korektne dovypisovať všetky zostávajúce dáta na štandardný výstup a skončiť.

### Požiadavky na program

Odovzdaný program musí používať multithreading s aspoň 2 vláknami (môže ich byť viac) -- minimálne jedno vlákno obsluhuje načítavanie zo vstupu a druhé výpis na štandardný výstup. Tieto vlákna si nejakým spôsobom koordinovane a efektívne odovzdávajú dáta. _Efektívne_ znamená, že akékoľvek formy činného čakania sú vylúčené. Všetky dáta, ktoré prišli na štandardný vstup programu, sa musia v (primeranom) konečnom čase a nezmenené dostať na štandardný výstup.

### Ako to má vyzerať?

Vlastný program má byť napísaný v jazyku C a používať iba štandardnú knižnicu jazyka C (https://en.wikipedia.org/wiki/C_standard_library, využívajte veci zahrnuté v štandarde POSIX a nie rôzne neprenositeľné doplnky, ktoré vaša konkrétna implementácia možno ponúka) a _pthread_. Kompilácia vášho programu by mala prebehnúť bez chýb pomocou príkazu

    gcc -std=c99 -Werror=implicit-function-declaration -pthread priezvisko.c -o priezvisko

Odporúčam tiež zapnúť prepínače `-W`, `-Wall`; často pomôžu odhaliť nenápadnú závažnú chybu. **Zvážte tiež použitie nástroja [valgrind](https://valgrind.org/) (odhalí o.i. chybnú prácu s pamäťou)**.

Na synchronizáciu je prudko odporúčané používať primitíva z tejto knižnice (`pthread_mutex_lock`, `pthread_mutex_unlock`, `pthread_cond_wait`, `pthread_cond_signal`). Viac o nich nájdete [tuto](cvicenie1.md).

Ak nemáte dostupný Linux, môžete použiť študentský server Davinci (davinci.fmph.uniba.sk), na ktorý sa viete pripojiť napr. pomocou PuTTy, alebo [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about). (Dôrazne však odporúčame Linux si nainštalovať, keď pre nič iné, tak aspoň pre tú skúsenosť.)

Na čítanie je vhodné použiť systémové volania [`read`](http://man7.org/linux/man-pages/man2/read.2.html) a [`write`](http://man7.org/linux/man-pages/man2/write.2.html), funkcie vyššej úrovne typu `getc` sú podstatne pomalšie.

### Ako to vyskúšať?

Ak chcete otestovať funkčnosť programu z príkazového riadka, najjednoduchší spôsob je vytvoriť si súbor s testovacími dátami (napr. `test.in`) a spustiť:

    ./priezvisko < test.in > test.out

Tento príkaz dá na štandardný vstup vášho programu obsah súboru `test.in` a vytvorí nový subor `test.out`, do ktorého je zachytený celý štandardný výstup. Môžete ich porovnať pomocou `diff`.

Môžete tiež využiť [testovač](tester).

### Odovzdávanie a hodnotenie

Programy sa odovzdávajú e-mailom na adresu `mazak.fmfi@gmail.com`, predmet `OS-DU1`, súbor priložte k e-mailu a pomenujte `priezvisko.c`, kde _priezvisko_ je vaše priezvisko. Odovzdať je možné viackrát (najviac raz denne). Pre bonusovú úlohu môžete odovzdať iný úplne nezávislý program, pomenujte ho `priezvisko_bonus.c`. Azda ani jeden rok sa ešte nestalo, aby všetci tieto pokyny dodržali, nepodceňujte to. :)

Plný počet bodov dostane program, ktorý za každých podmienok zvládne splniť zadanie úlohy; 0 bodov program, ktorý nie je možné donútiť, aby aspoň v nejakom prípade dostatočne spĺňal zadanie. Body medzi sa škálujú podľa rozsahu (ne-)funkčnosti. Zároveň **je možné získať 2 bonusové body** -- získa ich každý, komu sa podarí implementovať cat (aj keď nie nutne multithreadový), ktorý bude aspoň občas v 2 z 3 behov v reálnom čase (prvé číslo vo výstupe programu `time`) rýchlejší ako skutočný `cat`.

Očakáva sa, že program vie spracovať aj vstup veľkosti 1 GB do 10 sekúnd. ("Time limit exceeded" na menších vstupoch zvyčajne znamená chybne implementovanú komunikáciu medzi vláknami.) Stĺpec Testcase udáva veľkosť vstupu. Červené záznamy zodpovedajú chybnému správaniu programu a znamenajú stratu bodov, konkrétne bodové hodnotenie je však prideľované až na konci, keď si odovzdané programy prečítam a pochopím, či sú chyby zásadné alebo len marginálne. (Ak je program napísaný nezrozumiteľne, nemá to okamžitý vplyv na hodnotenie, ale v prípade chýb pravdepodobne bude hodnotený menším počtom bodov, pretože sa mi nepodarí zistiť, čo je v ňom správne a čo nie.)

Oficiálny výstup z testovača bude zverejnený po odovzdaní všetkých domácich úloh na http://dcs.fmph.uniba.sk/~mazak/vyucba/os/results1.html. 

V prípade ľubovoľných otázok na tému domácich úloh (napr. chyba či nejasnosť v zadaní) sa, prosím, ozvite čím skôr.

Napíšte mi aj v prípade, že si s nejakým problémom dlhšie neviete poradiť.

