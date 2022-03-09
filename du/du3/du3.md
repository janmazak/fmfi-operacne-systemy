# Domáca úloha 3

Úlohou je implementovať vlastný súborový systém. Táto úloha je o dosť rozsiahlejšia ako predchádzajúca,
preto na získanie plného počtu bodov nebude treba spraviť implementáciu celého API.

## Práca s diskom

Čítanie/zápis na disk prebieha po sektoroch (ktoré sú nastavené na `SECTOR_SIZE`
bajtov, čiže 128). Adresa sa uvádza v násobkoch sektorov a naraz je potrebné na
disk zapísať vždy jeden sektor (a číta sa tiež jeden sektor). Veľkosť disku je
tiež celočíselný násobok veľkosti sektora. API je teda nasledovné:

  - `hdd_size()` -- vráti veľkosť harddisku v bajtoch (_nie v sektoroch_)
  - `hdd_read(sector, buffer)` -- do premennej `buffer` načíta dáta zo sektora
    `sector` (čísluje sa od 0)
  - `hdd_write(sector, buffer)` -- na disk zápise z premennej `buffer` jeden
    sektor na adrese `sector`

Váš súborový systém bude vedieť otvárať a zatvárať súbory. Na pamätanie otvorených súborov
budeme používať handle (file descriptor) otvoreného súboru. Informácie o otvorených súboroch jednoznačne nepatria na disk.
(Pri vypnutí počítača zanikne aj informácia o tom, ktoré súbory boli otvorené; neplatia obmedzenia z predošlej DU.)

Handle sa skladá zo štyroch 4-bajtových integerov (dokopy 16 B),
ktoré môžete použiť, ako uznáte za vhodné. Handle reprezentuje typ
```
typedef struct {
    uint32_t info[4];
} file_t;
```
Funkcie, ktoré budú pracovať so súbormi, budú dostávať handle ako parameter;
uložte si doň informácie, ktoré potrebujete na určenie súboru na disku, pozície v ňom atď.
Na vytváranie a uvoľňovanie handles používajte výlučne nasledovné funkcie:

  - `fd_alloc()` -- allocates a new handle and returns a pointer to it
  - `fd_free(handle)` -- free an allocated handle

Prácu s handle odporúčame si jednotlivé byty v ňom pomenovať, alebo ešte lepšie, vytvoriť funkcie,
ktoré pre handle ako argument vypočítajú požadovanú informáciu (napr. pozíciu v otvorenom súbore).

#### Príklad

Vo [filesystem.c](src/filesystem.c) je už implementovaný jednoduchý a hlúpy súborový systém,
ktorý si v sektore 0 na disku drží názov a veľkosť jediného súboru, ktorý
môže existovať, a v sektore 1 si drží jeho dáta (nevie byť teda väčší ako
`SECTOR_SIZE`).

sektor 0
```
|-----12B------|----4B----|-----112B-----|
| meno súboru  | veľkosť  | nevyužité    |
```

sektor 1
```
|--------------128B----------------|
| dáta zo súboru                   |
```

Všimnite si použitie pomenovanej položky `FILE_T_OFFSET`; ostatné tri bajty v handle sú nevyužité.

## Čo máte spraviť?

Pozrite si súbor [filesystem.c](src/filesystem.c), nájdete v ňom ukážkovú čiastočnú implementáciu
filesystemu (veľa funkcií obsahuje len `return FAIL`). Tieto funkcie upravte/doplňte tak, aby sa správali podľa komentárov.

Vo všeobecnosti by mal byť súborový systém limitovaný iba množstvom dostupného miesta na disku,
v praxi je však rozumné zaviesť [niektoré obmedzenia](https://en.wikipedia.org/wiki/Comparison_of_file_systems#Limits),
čo umožní zvýšiť rýchlosť práce so súbormi a uľahčí implementáciu.
Nepridávajte však obmedzenia príliš reštriktívne alebo zbytočné (ako napr. limit na 1 súbor v ukážkovej implementácii).
Váš súborový systém by mal podporovať toto:
  - maximálna dĺžka jednej položky v ceste 12 B
  - celková dĺžka cesty max. 64 B
  - povolené znaky v názvoch súborov a adresárov: `a-zA-Z0-9.-_`; názvy sú citlivé na veľkosť písmen
  - maximálna veľkosť súboru 2^30 B (1 GiB)
  - maximálna veľkosť disku 2^31 B (2 GiB)
  - maximálny počet položiek v adresári 2^16
  - max. 16 otvorených súborov naraz

Môžete navyše predpokladať:
  - súbor bude otvorený najviac raz (pri otváraní nezisťujete, či už súbor nebol otvorený)
  - otvorené súbory sa nebudú mazať ani premenúvať (pri mazaní neskúmate, či je súbor otvorený alebo nie)
  - v prípade hardlinkov je otvorený naraz najviac jeden z nich
  - hardlinky sa vytvárajú len pre obyčajné súbory

Všetky cesty, ktoré dostávate ako argumenty, budú začínať lomítkom (koreňovým
adresárom `/`) ako v UNIXoch a budú absolútne -- nie je v nich adresár `.` ani `..`.
Pre jednoznačnosť cesty nikdy nekončia lomítkom (okrem cesty `/`).

Pomenovanie funkcií, ktoré máte implementovať, vychádza zo
[zaužívaných názvov týchto funkcií](http://linasm.sourceforge.net/docs/syscalls/filesystem.php).
Odporúčame tiež prečítať si dokumentáciu k aspoň niektorým z funkcií, ktoré idete implementovať
(o.i. získate lepšiu predstavu o mnohých detailoch, ktoré presahujú rámec tejto DU).

Symbolické linky sa môžu vytvárať aj na adresáre a neexistujúce položky. Ak cieľ symlinku neexistuje, symlink sa nedá otvoriť.

## Ako to testovať?

* Kompilácia: spustenie príkazu `make` v adresári so súbormi.
* Spustenie programu: `./wrapper`, prípadne `./test` pre testovanie.

Všetky potrebné súbory nájdete v adresári [`src`](src). Pre make
je tam [`Makefile`](src/Makefile), pomocou ktorého vytvoríte spustiteľný súbor `wrapper`, čo je váš
filesystem obalený wrapperom, ktorý čaká na príkazy. Viete si taktiež
skompilovať test, do ktorého môžete priamo písať príkazy, ktoré má váš
filesystem vykonávať. Momentálne je v ňom jednoduchá ukážka.

Váš program bude čítať príkazy zo štandardného vstupu a
vypisovať výsledky na štandardný výstup. Väčšinou platí konvencia, že meno
funkcie bez `fs_` na začiatku na štandardnom vstupe spôsobí zavolanie tej
funkcie. Riadky označené ako I: znamenajú zadaný vstup, O: je výstup od programu.
Za # je komentár.
```
I: creat /test.txt            # Požiadavka na vytvorenie nového súboru test.txt
O: 47423                      # Všetko je OK, dostali sme file handle
I: write 47423 38656c6c6f 5   # Zápise do súboru 5 bajtov, zakódované v hexastringu
O: 5                          # bolo zapísaných 5 bajtov
I: tell 47423                 # Na akej pozícii v súbore momentálne sme?
O: 5                          # na 5-tom bajte
I: close 47423                # Zavri file handle
O: 0                          # OK
```

Dáta pre funkcie read a write sú kódované do hexa reťazcov -- čo dvojica
znakov, to jeden bajt v hexadecimálnom zápise. Funkcia read tiež vracia načítaný
buffer v tomto formáte.

Ďalšia možnosť na testovanie je súbor [`test.c`](src/test.c), v ktorom máte ukážku volania
zopár funkcií filesystému, alebo použitie [testovaca](tester).

Dobre si overte, že vás program korektne pracuje s pamäťou ([valgrind](https://valgrind.org/docs/manual/quick-start.html)).

## Hodnotenie

Funkcie pre prácu so súborovým systémom sú rozdelené do 4 úrovni (pozri [filesystem.h](src/filesystem.h)).
Tieto úrovne sú medzi sebou previazané --- implementácia funkcií L1 napríklad závisí od toho, či máte ambíciu podporovať prácu s adresármi, a testovač využíva aj funkcie z nižších úrovni.
Premyslite si preto už na začiatku, aké máte ciele.

  - korektná implementácia po úroveň L1 -- 5 bodov
  - korektná implementácia po úroveň L2 -- 10 bodov
  - korektná implementácia po úroveň L3 -- 12 bodov
  - korektná implementácia po úroveň L4 -- 14 bodov

Korektná implementácia L3 znamená, že _všetko_ bude zvládať korektne pracovať
s adresármi, nie iba funkcie, ktoré sú v L3 navyše.


## Odovzdávanie

Programy sa odovzdávajú e-mailom na adresu `mazak.fmfi@gmail.com`, predmet `OS-DU3`, súbor `filesystem.c` priložte k e-mailu. Odovzdať je možné viackrát (najviac raz denne).

Najneskorší možný termín odovzdania je **9. 5. 2022**. Nepodceňujte čas potrebný na túto DU, za pol dňa to asi nenapíšete.
