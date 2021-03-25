# Cvičenie 1 (multithreading)

## Zadanie

[Zadanie domácej úlohy](du1.md)

## Termín

**Úlohu treba odovzdať do 21. 3. 2021.**

## Testovač

[Testovač](tester)

Použitie:
1. Naklonujte si repozitár.
2. Umiestnite testované riešenie do adresára `du/du1/tester/src`.
3. V adresári `du/du1/tester` spusťte `./testall.sh`.

Testovač nie je úplne spoľahlivý: môže sa stať, že nedokáže váš program násilne ukončiť po presiahnutí časového limitu (napr. ak vyrobíte deadlock). Nebojte sa ho vylepšiť (spravte pull request so zmenami).

## Knižnica _pthreads_

V riešení domácej úlohy budeme využívať jazyk C a knižnicu _pthreads_ (POSIX threads). Stručný popis nájdete nižšie a podrobnejší v [tutoriáli](https://computing.llnl.gov/tutorials/pthreads/).

#### Ukážka využitia _pthreads_

Krátky kód, ktorý vytvorí dve súčasne bežiace vlákna a nechá ich vypisovať na štandardný výstup plusy a mínusy.

    #include <pthread.h>
    #include <stdlib.h>
    #include <stdio.h>
    #include <unistd.h>
     
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
     
    void *vlakno1(void *data) {
        while(1) {
            pthread_mutex_lock(&mutex);
            printf("--"); printf("---"); printf("\n");
            pthread_mutex_unlock(&mutex);
            sleep(1);
        }
    }
     
    void *vlakno2(void *data) {
        while(1) {
            pthread_mutex_lock(&mutex);
            printf("++"); printf("+++"); printf("\n");
            pthread_mutex_unlock(&mutex);
            sleep(1);
        }
    }
     
    int main (void) {
        pthread_t t1, t2;
        pthread_create(&t1, NULL, vlakno1,  NULL);
        pthread_create(&t2, NULL, vlakno2,  NULL);
        sleep(5);
        return 0;
    }

Na skompilovanie kódu použite príkaz:

    gcc -pthread example.c -o example

## Správa vlákien

Zopár užitočných funkcií pre prácu s vláknami:

  *  `int pthread_create(pthread_t *thread, const pthread_attr_t *attr, void *(*start_routine) (void *), void *arg)` sa používa na vytváranie vlákien: inicializuje obsah premennej `thread` informáciami o novo vytvorenom vlákne, nastaví vláknu atribúty podľa `attr` (alebo s NULL použije default hodnoty), vo vlákne skočí na funkciu `start_routine` s parametrom `arg`. (http://linux.die.net/man/3/pthread_create)
  * Od spustenia vlákno žije vlastným životom, hoci zdieľa dáta so svojím rodičom. Vlákno môže skončiť zavolaním funkcie `void pthread_exit(void *retval)` alebo návratom z funkcie, ktorou vlákno začínalo. (http://linux.die.net/man/3/pthread_exit)
  * Keď sa vlákno ukončuje, návratová hodnota ukladá a rodič ju môže prečítať zavolaním funkcie `int pthread_join(pthread_t thread, void **retval)`. Ak sa `pthread_join` zavolá na neukončená vlákno, volajúce vlákno sa zablokuje a čaká na jeho ukončenie. (http://linux.die.net/man/3/pthread_join)
  * Vlákno je možné v niektorých momentoch zrušiť pomocou `int pthread_cancel(pthread_t thread)`, avšak platia tu isté obmedzenia (http://linux.die.net/man/3/pthread_cancel).

#### Zámky/mutexy

Slúžia na zabezpečenie časti kódu, ktorú môže naraz vykonávať iba jeden proces (kritická sekcia). Pred vstupom do kritickej sekcie musí vlákno zamknúť mutex -- pokiaľ už bol zamknutý predtým, vlákno bude zablokované, kým sa neuvoľní. V opačnom prípade mutex zamkne a vojde do kritickej sekcie, a po skončení vykonávania mutex odomkne. 

Pthreads API, ktoré je dôležité pre nás, je nasledovné:

* `int pthread_mutex_init(pthread_mutex_t *mutex, const pthread_mutexattr_t *restrict attr)`
    - inicializuje nový mutex s prípadnými ďalšími atribútmi (môžu byť `NULL`)
* `int pthread_mutex_lock(pthread_mutex_t *mutex)`
    - zamkne mutex
* `int pthread_mutex_unlock(pthread_mutex_t *mutex)`
    - odomkne mutex
* `int pthread_mutex_destroy(pthread_mutex_t *mutex)`
    - zruší mutex, jeho ľubovoľné ďalšie použitie bude neplatné

Okrem funkcií sa statické mutexy (tie, o ktorých vieme už v čase kompilácie) dajú inicializovať aj pomocou statického inicializátora (`pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;`), ktorý spracuje už kompilátor a dá sa tak predísť zbytočným volaniam počas behu programu.

Detailnejšia dokumentácia:
* http://linux.die.net/man/7/pthreads
* http://linux.die.net/man/3/pthread_mutex_lock
* http://linux.die.net/man/3/pthread_create


#### Condition variable

Umožňuje vláknam čakať na splnenie podmienky v kritickej sekcii. Základné operácie sú `wait`/`await` a `signal`. Typický scenár použitia je nasledovný: 

Vlákno, ktoré vnútri kritickej sekcie čaká na splnenie nejakej podmienky, môže zaspať na condition variable. Pri zaspaní vnútri kritickej sekcie sa zároveň uvoľní mutex, ktorý pre ňu toto vlákno držalo. Vďaka tomuto môže nejaké iné vlákno vstúpiť do tej istej kritickej sekcie a vykonať nejaké zmeny. Zároveň, ak je šanca, že bola zmenená podmienka, pre ktorú prvé vlákno zaspalo, môže mu poslať `signal`/`wake`. Po zobudení začne vlákno čakať na získanie mutexu, overí, či bola splnená podmienka, na ktorú čakalo -- v prípade kladnej odpovede pokračuje vo vykonávaní, ináč opäť zaspí.

Dôležitá podmnožina Pthreads API je nasledovná:
* `int pthread_cond_init(pthread_cond_t *cond)`<br>
    - inicializuje condition variable
* `int pthread_cond_wait(pthread_cond_t *restrict cond, pthread_mutex_t *restrict mutex)`
    - zaspí na condition variable, pričom uvoľní mutex
* `int pthread_cond_signal(pthread_cond_t *restrict cond)`
    - zobudí vlákno čakajúce na condition variable
* `int pthread_cond_destroy(pthread_cond_t *cond)`
    - uvoľní condition variable

Tak isto, ako pri mutexoch, aj tu sa dá použiť statický inicializátor:

    pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

Viac informácií sa opäť dá nájsť napríklad na
* http://linux.die.net/man/3/pthread_cond_init
* http://linux.die.net/man/3/pthread_cond_wait
* http://linux.die.net/man/3/pthread_cond_signa

V oboch prípadoch je dôležité uvedomiť si, že spánok vlákna môže byť zobudený nielen signálom z iného vlákna, ale aj operačným systémom z iných dôvodov (ide najmä o prípade, keď na jednom mutexe čaká viac ako jedno vlákno). Preto treba vždy po zobudení skontrolovať, či bola potrebná podmienka skutočne splnená.

Aj keď je povolené zavolať `pthread_cond_signal()` mimo časti kódu so zamknutým mutexom, [v niektorých prípadoch je to nevhodné](https://stackoverflow.com/questions/4544234/calling-pthread-cond-signal-without-locking-mutex#:~:text=The%20pthread_cond_signal()%20routine%20is,pthread_cond_wait()%20routine%20to%20complete.).

