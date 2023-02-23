#include "wrapper.h"

/* Kod funkcii my_alloc a my_free nahradte vlastnym. Nepouzivajte ziadne
 * globalne ani staticke premenne; jedina globalna pamat je dostupna pomocou
 * mread/mwrite/msize, ktorych popis najdete vo wrapper.h */

/* Ukazkovy kod zvladne naraz iba jedinu alokaciu. V 0-tom bajte pamate si
 * pamata, ci je pamat od 1 dalej volna alebo obsadena. 
 *
 * V pripade, ze je volna, volanie my_allloc skonci uspesne a vrati zaciatok
 * alokovanej RAM; my_free pri volnej mamati zlyha.
 *
 * Ak uz nejaka alokacia prebehla a v 0-tom bajte je nenulova hodnota. Nie je
 * mozne spravit dalsiu alokaciu, takze my_alloc musi zlyhat. my_free naopak
 * zbehnut moze a uvolni pamat.
 */


/**
 * Inicializacia pamate
 *
 * Zavola sa, v stave, ked sa zacina s prazdnou pamatou, ktora je inicializovana
 * na 0.
 */
void my_init(void) {
	return;
}

/**
 * Poziadavka na alokaciu 'size' pamate. 
 *
 * Ak sa pamat podari alokovat, navratova hodnota je adresou prveho bajtu
 * alokovaneho priestoru v RAM. Pokial pamat uz nie je mozne alokovat, funkcia
 * vracia FAIL.
 */
int my_alloc(unsigned int size) {

	/* Nemozeme alokovat viac pamate, ako je dostupne */
	if (size >= msize() - 1)
		return FAIL;

	/* Pamat uz bola alokovana */
	if (mread(0) == 1)
		return FAIL;

	/* Vsetko je OK, mozeme splnit poziadavku. Do 0teho bajtu si poznacime, ze
	 * pamat je obsadena a vratime adresu prveho bajtu novo alokovanej pamate
	 */
	mwrite(0, 1);
	return 1;
}

/**
 * Poziadavka na uvolnenie alokovanej pamate na adrese 'addr'.
 *
 * Ak bola pamat zacinajuca na adrese 'addr' alokovana, my_free ju uvolni a
 * vrati OK. Ak je adresa 'addr' chybna (nezacina na nej ziadna alokovana
 * pamat), my_free vracia FAIL.
 */

int my_free(unsigned int addr) {

	/* Adresa nie je platnym smernikom, ktory mohol vratit my_alloc */
	if (addr != 1)
		return FAIL;

	/* Nie je alokovana ziadna pamat, nemozeme ju teda uvolnit */
	if (mread(0) != 1)
		return FAIL;

	/* Vsetko je OK, mozeme uvolnit pamat */
	mwrite(0, 0);
	return OK;
}
