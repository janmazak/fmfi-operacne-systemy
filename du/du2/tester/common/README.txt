   2. Domaca uloha z OS
   ====================


  Velmi strucne, vasou ulohou bude napisat si vlastny alokator pamate. Ulohou
alokatora je spravovat nejaky kus pamate a vykonavat nad nim operacie
alloc(velkost) a free(adresa); vo vasom pripade funkcie my_alloc a my_free. Ich
vyznam je rovnaky, ako malloc/free v Ccku; viac je popisane v druhej casti


  1. Praca s pamatou

  Vase moznosti prace s pamatou budu obmedzene -- nebudete k nej pristupovat ako
ku polu, ale pomocou nasledovnych funkcii:

  - msize() -- vrati celkovy pocet bajtov v pamati. Dostupne adresy v pamati su
    vzdy rozsahu 0 az msize().

  - mread(adresa) -- precita bajt z pamate na adrese 'adresa' a vrati jeho
    hodnotu

  - mwrite(adresa, data) -- zapise na adresu 'adresa' bajt 'data'.

  Navyse, nesmiete pouzivat ziadne globalne ani staticke premenne. Rozpisane
podrobnejsie:

  - v Cckovom programe nesmu byt ziadne premenne deklarovane mimo vasich
    funkcii,
  - v Jave aj v C nesmiete pouzivat klucove slovo 'static' okrem miest, kde uz
    pouzite je (resp. v Jave si ho mozete dovolit iba v kombinacii s klucovym
    slovom 'final' a v Ccku s 'const' :) ). 

  A samozrejme, ziadne triky s dynamickou alokaciou pamate a ukladanim si
pointrov cez 'mwrite'. Mozem sa rozhodnut, ze vas program kedykolvek ukoncim, a
spustim znova; jedina trocha 'trvacejsia' pamat je dostupna cez mread/mwrite. Ak
by nejaky pripad nebol jednoznacny, radsej sa ozvite.

  Ak si potrebujete pamatat lubovolne data dlhsie ako v ramci jedneho volania
my_alloc/my_free, musite si ich ulozit do 'pamate' pomocou mread/mwrite.
Typickym prikladom takychto dat su napriklad udaje o tom, ktora cast pamate je
obsadena a ktora volna.


  2. Co mate spravit

  V zadani je pre vas dolezity iba jeden subor -- alloc.c, alebo Alloc.java . V
tomto subore budete upravovat kod funkcii/metod, nemali by ste sa dotykat nicoho
ineho. Obzvlast nie obsahu suboru wrapper.c/Wrapper.java , pripadne wrapper.h
(tieto subory mi ani neposielajte; ako riesenie vasej ulohy mi bude stacit
alloc.c/Alloc.java).

  Vasou ulohou je (re-)implementovat 3 funkcie v alloc.c/Alloc.java

  - my_init() -- jeho kod sa vykona pri vytvarani noveho suboru s pamatou.
    Mozete predpokladat, ze pamat je na zaciatku nastavena na same 0; v tejto
    funkcii si mozete vytvorit potrebne pociatocne datove struktury.

  - my_alloc(velkost) -- alokuje v pamati oblast velkosti 'velkost' a vrati
    adresu prveho bajtu alokovaneho priestoru v pamati. Pokial sa poziadavka
    neda splnit, vrati FAIL .

  - my_free(adresa) -- uvolni pamat na adrese 'adresa', ktoru predtym alokoval.
    Ak 'adresa' nie je platny prvy bajt alokovanej pamate, vrati FAIL. Ak
    uvolnenie pamate uspesne prebehne, vrati OK.

  V zdrojakoch uz je implementovana jedna velmi trivialna verzia alokatora,
ktora ukazuje, ako by veci mali fungovat. Umoznuje vyrobit iba jedinu alokaciu,
ktora nezavisle od velkosti aj tak zaberie celu RAM bez jedneho bajtu. Ten jeden
bajt je pouzity na pamatanie si toho, ci pamat je alebo nie je alokovana.

  Do pamate, ktoru alokujete, sa moze realne zapisovat (a pri testovani sa aj
bude); preto si nemozete dovolit 'upratat' pamat tak, ze zmenite zaciatky
alokovanych miest v pamati.


  3. Ako to testovat?

  Na spustenie celej domacej ulohy ju najskor musite skompilovat (v
nasledujucich odstavcoch budem uvadzat vzdy varianty pre C aj Javu):

  gcc alloc.c wrapper.c -o wrapper
  javac Alloc.java Wrapper.java

  Pri spustani viete zadat velkost pamate, ktoru bude vas alokator pouzivat. Ak
sa uskromnite s pamatou o velkosti 47 bajtov (bez parametra sa inicializuje
pamat o velkosti 4096 bajtov), spustite a spravnom adresari (tam, kde su
zdrojaky):

  ./wrapper 47
  java -ea Wrapper 47

  NOTE: Javisti, vsimnite si -ea flag. Znamena to 'enable assertions' --
vyhodnocovanie niektorych kontrolnych podmienok (assert), ktore su v zdrojaku,
ale Java ich standardne vypina. Je prudko odporucane zapnut kontroly; ak program
bude padat, znamena to, ze cosi je zle. Malo by to byt mozne spravit v kazdom
IDE: 

 - eclipse: http://www.cis.upenn.edu/~matuszek/cit594-2004/Pages/eclipse-faq.html#assert
 - NetBeans: http://paulmcpd.blogspot.com/2009/12/netbeans-enabling-assertions.html

  Prve spustenie vyrobi subor memory.bin so zadanou velkostou. Ak budete chciet
velkost pamate zmenit, musite subor zmazat, aby sa mohol vyrobit novy.

  Po spusteni bude program cakat na data zo standardneho vstupu; rozpravat sa s
nim da pomocou zopar prikazov. Kazdy prikaz sa pise na novy riadok, parametre su
oddelene medzerami. Program zakazdym (az na prikaz 'end' vypise navratovu
hodnotu).

  1) alloc 47 -- zavola my_alloc(47) a vypise navratovu hodnotu
  2) free 47 -- zavola my_free(47) a vypise navratovu hodnotu
  3) write 0 47 -- zavola mwrite(0, 47) a vypise 0
  4) read 0 -- zavola mread(0) a vypise navratovu hodnotu
  5) end -- ukonci program


  Ak by ste chceli testovat vo vacsom, mozete si sadu prikazov dopredu pripravit
do textoveho suboru a potom spustit:

  ./wrapper 47 <prikazy.txt
  java -ea Wrapper 47 <prikazy.txt

  Pozor, takto sa neda testovat uplne vsetko -- prikazy su casto zavisle na
navratovych hodnotach predchadzajucich prikazov.


  4. Hodnotenie

  Vase riesenia by v prvom rade mali fungovat _spravne_ -- nemali by padat pre
lubovolny korektny vstup. Uprednostnujte jednoduchsi a funkcny kod pred
zlozitejsim a padajucim. 

  Ukazkove riesenie tuto podmienku splna az prilis, preto budem zaroven
pozadovat, aby s rastucou pamatou mohol rast aj pocet alokovanych oblasti v
pamati, a tiez celkova velkost pamate, ktoru je mozne alokovat.  Inymi slovami,
mali by ste s pamatou pracovat aspon trocha efektivne.

  Zaroven prichadza challenge -- ked mi odovzdate riesenia, budem ich testovat
na sade nejakych testov. Prve tri algoritmy, ktore budu vediet pamat vyuzivat
najlepsie (v priemere najmensi overhead na alokaciu, ... ), ziskaju opat 2
bonusove body.

