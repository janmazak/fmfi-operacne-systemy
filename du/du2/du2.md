# Domáca úloha 2

Vasou ulohou bude napisat vlastny alokator pamate v jazyku C. Ulohou
alokatora je spravovat nejaky kus pamate a vykonavat nad nim operacie
alloc(velkost) a free(adresa); vo vasom pripade funkcie `my_alloc` a `my_free`. Ich
vyznam je rovnaky, ako malloc/free v C; viac je popisane v druhej casti.


## Praca s pamatou

Vase moznosti prace s pamatou budu obmedzene -- nebudete k nej pristupovat ako k polu, ale pomocou nasledovnych funkcii:

  - `msize()` -- vrati celkovy pocet bajtov v pamati. Dostupne adresy v pamati su
    vzdy rozsahu `0` az `msize() - 1`.

  - `mread(adresa)` -- precita bajt z pamate na adrese _adresa_ a vrati jeho
    hodnotu

  - `mwrite(adresa, data)` -- zapise na adresu _adresa_ bajt _data_.

Velkost pamati bude najviac 2^30, cize adresy sa zmestia do 4 bytov, resp. od typu `int` na beznom pocitaci.

Navyse, nesmiete pouzivat ziadne globalne ani staticke premenne, cize:
  - ziadne premenne nesmu byt deklarovane mimo funkcii,
  - nesmiete pouzivat klucove slovo `static` okrem miest, kde uz pouzite je (pri `const`). 

A samozrejme, ziadne triky s dynamickou alokaciou pamate a ukladanim si
ukazovatelov cez `mwrite`. Vas program moze byt kedykolvek ukonceny a spusteny znova;
jedina 'trvacna' pamat je dostupna cez `mread`/`mwrite`.
(Ak by nejaky pripad nebol jednoznacny, radsej sa opytajte.)

Ak si potrebujete pamatat lubovolne data dlhsie ako v ramci jedneho volania
`my_alloc`/`my_free`, musite si ich ulozit do 'pamate' pomocou `mread`/`mwrite`.
Typickym prikladom takychto dat su napriklad udaje o tom, ktora cast pamate je
obsadena a ktora volna.


## Co mate spravit

V zadani je pre vas dolezity iba jeden subor -- [alloc.c](src/alloc.c).
V tomto subore budete upravovat kod funkcii/metod, nemali by ste sa dotykat nicoho
ineho. Obzvlast nie obsahu suboru `wrapper.c` a `wrapper.h` (tieto subory ani neposielajte; ako riesenie ulohy staci `alloc.c`).

Vasou ulohou je (re-)implementovat nasledovne tri funkcie v `alloc.c`:

- `my_init()` -- vykona sa pri vytvarani noveho suboru s pamatou.
Mozete predpokladat, ze pamat je na zaciatku nastavena na same 0; v tejto
funkcii si mozete vytvorit potrebne pociatocne datove struktury.

- `my_alloc(velkost)` -- alokuje v pamati oblast velkosti 'velkost' a vrati
adresu prveho bajtu alokovaneho priestoru v pamati. Pokial sa poziadavka
neda splnit, vrati FAIL.

- `my_free(adresa)` -- uvolni pamat na adrese 'adresa', ktoru predtym alokoval.
Ak 'adresa' nie je platny prvy bajt alokovanej pamate, vrati FAIL. Ak
uvolnenie pamate uspesne prebehne, vrati OK.

V zdrojakoch uz je implementovana jedna velmi trivialna verzia alokatora,
ktora ukazuje, ako by veci mali fungovat. Umoznuje vyrobit iba jedinu alokaciu,
ktora nezavisle od velkosti aj tak zaberie celu RAM bez jedneho bajtu. Ten jeden
bajt je pouzity na pamatanie si toho, ci pamat je alebo nie je alokovana.

Do pamate, ktoru alokujete, sa moze realne zapisovat (a pri testovani sa aj
bude); preto si nemozete dovolit 'upratat' pamat tak, ze zmenite zaciatky
alokovanych miest v pamati -- ked ste raz niekomu nieco pridelili, spolieha sa na to.

Poznamka ku debugovaniu -- ak chcete pouzivat debugovacie vypisy, vypisujte
ich na `stderr`. Je to jednak pekna konvencia, jednak to nezmatie testovac,
ktory komunikuje pomocou `stdin` a `stdout`.

## Ako to testovat?

Na spustenie celej domacej ulohy ju najskor musite skompilovat:

    gcc alloc.c wrapper.c -o wrapper

Pri spustani viete zadat velkost pamate, ktoru bude vas alokator pouzivat. Ak
sa uskromnite s pamatou o velkosti 47 bajtov (bez parametra sa inicializuje
pamat o velkosti 4096 bajtov), spustite v spravnom adresari (tam, kde su
zdrojaky):

    ./wrapper 47

Prve spustenie vyrobi subor `memory.bin` so zadanou velkostou. Ak budete chciet
velkost pamate zmenit, musite subor zmazat, aby sa mohol vyrobit novy.

Po spusteni bude program cakat na data zo standardneho vstupu; rozpravat sa s
nim da pomocou zopar prikazov. Kazdy prikaz sa pise na novy riadok, parametre su
oddelene medzerami. Program zakazdym (az na prikaz 'end') vypise navratovu
hodnotu.

  * `alloc 47` -- zavola `my_alloc(47)` a vypise navratovu hodnotu
  * `free 47` -- zavola `my_free(47)` a vypise navratovu hodnotu
  * `write 0 47` -- zavola `mwrite(0, 47)` a vypise `0`
  * `read 0` -- zavola `mread(0)` a vypise navratovu hodnotu
  * `end` -- ukonci program


Ak by ste chceli testovat vo vacsom, mozete si sadu prikazov dopredu pripravit
do textoveho suboru a potom spustit:

    ./wrapper 47 < prikazy.txt

Na komplexnejsie testovanie odporucame vyuzit [testovac](tester) v jazyku Python.

## Hodnotenie

Vase riesenia by v prvom rade mali fungovat **spravne** -- nemali by padat pre
lubovolny korektny vstup. Uprednostnujte jednoduchsi a funkcny kod pred
zlozitejsim a padajucim.

Ukazkove riesenie tuto podmienku splna "az prilis", preto budem zaroven
pozadovat, aby s rastucou pamatou mohol rast aj pocet alokovanych oblasti v
pamati, a tiez celkova velkost pamate, ktoru je mozne alokovat. Inymi slovami,
mali by ste s pamatou pracovat aspon trocha efektivne.
Myslite tiez na to, ze alokacia pamate musi byt rychla (jednotlive volania funkcii alokatora by nemali trvat viac nez par milisekund), hoci optimalizovat rychlost `alloc`/`free` nie je hlavnym cielom spravy pamate, najma nie v tejto domacej ulohe.

Zaroven prichadza challenge: priblizne 5 algoritmov, ktore budu vediet pamat vyuzivat najlepsie (pre danu sadu testov; hodnoti sa v priemere najmensi overhead na alokaciu atd.), ziskaju opat 1 az 2 bonusove body.

## Odovzdavanie

Programy sa odovzdávajú e-mailom na adresu `mazak.fmfi@gmail.com` (predmet `OS-DU2`, súbor `alloc.c` priložte k e-mailu. Odovzdať je možné viackrát (najviac raz denne). Pre bonusovú úlohu môžete odovzdať iný úplne nezávislý program, pomenujte ho `priezvisko_bonus.c`. Azda ani jeden rok sa ešte nestalo, aby všetci tieto pokyny dodržali, nepodceňujte to. :)

Najneskorsi mozny termin odovzdania je **11. 4. 2021**. Nepodcenujte cas potrebny na tuto DU, za hodinku-dve to s velmi vysokou pravdepodobnostou nenapisete.

