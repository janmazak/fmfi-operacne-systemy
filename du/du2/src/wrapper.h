#ifndef WRAPPER_H
#define WRAPPER_H

#include <stdint.h>

/**
 * Precita z permanentnej pamate bajt na adrese 'addr'.
 *
 * V pripade nespravnej adresy zhodi program :).
 */
uint8_t mread(unsigned int addr);

/**
 * Zapise do permanentnej pamate na adresu 'addr' bajt 'val'.
 *
 * V pripade zlych vstupnych parametrov zhodi program :).
 */
void mwrite(unsigned int addr, uint8_t val);

/** 
 * Vrati velkost dostupnej pamate v bajtoch.
 *
 * Ostatne funkcie je mozne volat s parametrom 'addr' od 0 po 'msize()-1'. Tato
 * funkcia nema parametre, ktore by mohli sposobit pad programu :( .
 */
unsigned int msize(void);

/**
 * Navratova hodnota pre pripad, ze alloc nemoze alokovat pamat alebo free
 * dostalo neplatnu adresu.
 */

#define FAIL	(-1)
#define OK  	(0)

/* Nasledujuce funkcie musite implementovat v subore alloc.c */

void my_init(void);
int my_alloc(unsigned int size);
int my_free(unsigned int addr);

#endif
