# Domáca úloha 2

Vašou úlohou bude napísať vlastný alokator pamäte v jazyku C. Úlohou
alokatora je spravovať nejaký kus pamäte a vykonávať nad ním operácie
alloc(veľkosť) a free(adresa); vo vašom prípade funkcie `my_alloc` a `my_free`. 
Ich význam je rovnaký, ako malloc/free v C; viac je popísané v druhej časti.


## Práca s pamäťou

Vaše možnosti práce s pamäťou budú obmedzené -- nebudete k nej pristupovať ako k poľu, ale pomocou nasledovných funkcií:

  - `msize()` -- vráti celkový počet bajtov v pamäti. Dostupné adresy v pamäti sú
    vždy rozsahu `0` až `msize() - 1`.

  - `mread(adresa)` -- prečíta bajt z pamäte na adrese _adresa_ a vráti jeho
    hodnotu

  - `mwrite(adresa, dáta)` -- zapíše na adresu _adresa_ bajt _dáta_.

Veľkosť pamäte bude najviac 2^30, čiže adresy sa zmestia do 4 bytov, resp. od typu `int` na bežnom počítači.
Veľkosť pamäte sa počas činnosti vášho alokátora nemení, `msize()` vráti stále rovnakú hodnotu (takú, ako v `my_init()`, viď nižšie).

Navyše, nesmiete používať žiadne globálne ani statické premenné, čiže:
  - žiadne premenné nesmú byť deklarované mimo funkcií,
  - nesmiete používať kľúčové slovo `static` okrem miest, kde už použité je (pri `const`).
(Je však možné do globálneho priestoru umiestniť konštanty, napr. ak máte predpočítanú veľkú tabuľku.)

A samozrejme, žiadne triky s dynamickou alokáciou pamäte a ukladaním si
ukazovateľov cez `mwrite`. Váš program môže byť kedykoľvek ukončený a spustený znova;
jediná 'trvácna' pamäť je dostupná cez `mread`/`mwrite`.
(Ak by nejaký prípad nebol jednoznačný, radšej sa opýtajte.)

Ak si potrebujete pamätať ľubovoľné dáta dlhšie ako v rámci jedného volania
`my_alloc`/`my_free`, musíte si ich uložiť do 'pamäte' pomocou `mread`/`mwrite`.
Typickým príkladom takýchto dát sú napríklad údaje o tom, ktorá časť pamäte je
obsadená a ktorá voľná.

V tejto domácej úlohe sa nerieši bezpečnosť. V reálnom systéme majú jednotlivé procesy oddelený pamäťový priestor, a samozrejme alokačné dáta si nemôže užívateľský program prepisovať len tak. (Na druhej strane, mnohé OS dovoľujú procesu skorumpovať vlastnú pamäť, napr. ak si program prepíše hodnoty v call stacku, rozsype sa to nepredvídateľným spôsobom.)

Váš alokátor má fungovať za predpokladu, že užívatelia prepisujú len im pridelenú pamäť.


## Čo máte spraviť

V zadaní je pre vás dôležitý iba jeden súbor -- [alloc.c](src/alloc.c).
V tomto súbore budete upravovať kód funkcií, nemali by ste sa dotýkať ničoho
iného. Obzvlášť nie obsahu súboru `wrapper.c` a `wrapper.h` (tieto súbory ani neposielajte; ako riešenie úlohy stačí `alloc.c`).

Vašou úlohou je (re-)implementovať nasledovné tri funkcie v `alloc.c`:

- `my_init()` -- vykoná sa pri vytváraní nového súboru s pamäťou.
Môžete predpokladať, že pamäť je na začiatku nastavená na samé 0; v tejto
funkcii si môžete vytvoriť potrebné počiatočné dátové štruktúry.

- `my_alloc(veľkosť)` -- alokuje v pamäti oblasť veľkosti 'veľkosť' a vráti
adresu prvého bajtu alokovaného priestoru v pamäti. Pokiaľ sa požiadavka
nedá splniť, vráti FAIL.

- `my_free(adresa)` -- uvoľní pamäť na adrese 'adresa', ktorú predtým alokoval.
Ak 'adresa' nie je platný prvý bajt alokovanej pamäte, vráti FAIL. Ak
uvoľnenie pamäte úspešne prebehne, vráti OK.

V zdrojákoch už je implementovaná jedna veľmi triviálna verzia alokatora,
ktorá ukazuje, ako by veci mali fungovať. Umožňuje vyrobiť iba jedinú alokáciu,
ktorá nezávisle od veľkosti aj tak zaberie celú RAM bez jedného bajtu. Ten jeden
bajt je použitý na pamätanie si toho, či pamäť je alebo nie je alokovaná.

Do pamäte, ktorú alokujete, sa môže reálne zapisovať (a pri testovaní sa aj
bude); preto si nemôžete dovoliť 'upratať' pamäť tak, že zmeníte začiatky
alokovaných miest v pamäti -- keď ste raz niekomu niečo pridelili, spolieha sa na to.

Poznámka ku debugovaniu -- ak chcete používať debugovacie výpisy, vypisujte
ich na `stderr`. Je to jednak pekná konvencia, jednak to nezmätie testovac,
ktorý komunikuje pomocou `stdin` a `stdout`.


## Ako to testovať?

Na spustenie celej domácej úlohy ju najskôr musíte skompilovať:

    gcc alloc.c wrapper.c -o wrapper

Pri spúšťaní viete zadať veľkosť pamäte, ktorú bude váš alokator používať. Ak
sa uskromníte s pamäťou o veľkosti 47 bajtov (bez parametra sa inicializuje
pamäť o veľkosti 4096 bajtov), spustite v správnom adresári (tam, kde sú
zdrojáky):

    ./wrapper 47

Prvé spustenie vyrobí súbor `memory.bin` so zadanou veľkosťou. Ak budete chcieť
veľkosť pamäte zmeniť, musíte súbor zmazať, aby sa mohol vyrobiť nový.

Po spustení bude program čakať na dáta zo štandardného vstupu; rozprávať sa s
ním dá pomocou zopár príkazov. Každý príkaz sa píše na nový riadok, parametre sú
oddelené medzerami. Program zakaždým (až na príkaz 'end') vypíše návratovú
hodnotu.

  * `alloc 47` -- zavolá `my_alloc(47)` a vypíše návratovú hodnotu
  * `free 47` -- zavolá `my_free(47)` a vypíše návratovú hodnotu
  * `write 0 47` -- zavolá `mwrite(0, 47)` a vypíše `0`
  * `read 0` -- zavolá `mread(0)` a vypíše návratovú hodnotu
  * `end` -- ukončí program


Ak by ste chceli testovať vo väčšom, môžete si sadu príkazov dopredu pripraviť
do textového súboru a potom spustiť:

    ./wrapper 47 < príkazy.txt

Na komplexnejšie testovanie odporúčame využiť [testovac](tester) v jazyku Python.


## Hodnotenie

Vaše riešenia by v prvom rade mali fungovať **správne** -- nemali by padať pre
ľubovoľný korektný vstup. Uprednostňujte jednoduchší a funkčný kód pred
zložitejším a padajúcim.

Ukážkové riešenie túto podmienku spĺňa "až príliš", preto budem zároveň
požadovať, aby s rastúcou pamäťou mohol rásť aj počet alokovaných oblastí v
pamäti, a tiež celková veľkosť pamäte, ktorú je možné alokovať. Inými slovami,
mali by ste s pamäťou pracovať aspoň trocha efektívne.
Myslite tiež na to, že alokácia pamäte musí byť rýchla (jednotlivé volania funkcií alokatora by nemali trvať viac než pár milisekúnd), hoci optimalizovať rýchlosť `alloc`/`free` nie je hlavným cieľom správy pamäte, najmä nie v tejto domácej úlohe.

Zároveň prichádza challenge: približne 5 algoritmov, ktoré budú vedieť pamäť využívať najlepšie (pre danú sadu testov; hodnotí sa v priemere najmenší overhead na alokáciu atď.), získajú opäť 1 až 2 bonusové body.


## Odovzdávanie

Programy sa odovzdávajú e-mailom na adresu `mazak.fmfi@gmail.com`, predmet `OS-DU2`, súbor `alloc.c` priložte k e-mailu. Odovzdať je možné viackrát (najviac raz denne).

Najneskorší možný termín odovzdania je **25. 4. 2022**. Nepodceňujte čas potrebný na túto DU, za hodinku-dve to s vysokou pravdepodobnosťou nenapíšete, najmä ak cielite na efektívnejšie riešenie, ktoré má šancu získať bonus.

