#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "filesystem.h"
#include "util.h"


/* file_t info items */
#define FILE_T_OFFSET 0

typedef struct {
	char name[MAX_FILENAME];
	uint32_t size;
} zero_sector_t;


/**
 * Naformatovanie disku.
 *
 * Zavola sa vzdy, ked sa vytvara novy obraz disku.
 */
void fs_format()
{
	uint8_t buffer[256] = { 0 };
	hdd_write(0, buffer);
}

/**
 * Vytvorenie suboru.
 *
 * Volanie vytvori v suborovom systeme na zadanej ceste novy subor a vrati
 * handle nan. Ak subor uz existoval, bude skrateny na prazdny. Pozicia v subore bude
 * nastavena na 0ty byte. Ak adresar, v ktorom subor ma byt ulozeny, neexistuje,
 * vrati FAIL (sam nevytvara adresarovu strukturu, moze vytvarat iba subory).
 */

file_t *fs_creat(const char *path)
{
	/* Nepodporujeme adresare */
	if (strrchr(path, PATHSEP) != path)
		return NULL;

	uint8_t buffer[SECTOR_SIZE] = { 0 };

	/* Skontrolujeme, ci uz nahodou na disku nie je subor */
	hdd_read(0, buffer);

	if (buffer[0] != 0 ) {
		/* Nemozeme vytvorit dalsi subor, ak nema rovnake meno, ako uz existujuci
		 */
		if (strncmp(path, (char*)buffer, MAX_FILENAME))
			return NULL;

		/* Skratime subor na 0 bajtov */
		((zero_sector_t*)buffer)->name[0] = 0;
		hdd_write(0, buffer);
	}

	/* Vsetko ok, pripravime informacie pre zapis do nulteho sektora */

	/* Meno suboru je na zaciatku*/
	strcpy((char*)buffer, path);

	/* Za castou vyhradenou pre meno je ulozena velkost suboru */
	*((uint32_t*)(buffer + MAX_FILENAME)) = 0;

	/* Zapiseme informacie o novovytvorenom subore na disk */
	hdd_write(0, buffer);

	return fs_open(path);
}


/**
 * Otvorenie existujuceho suboru.
 *
 * Ak zadany subor existuje, funkcia ho otvori a vrati handle nan. Pozicia v
 * subore bude nastavena na 0-ty bajt. Ak subor neexistuje, vrati FAIL.
 */
file_t *fs_open(const char *path)
{
	uint8_t buffer[SECTOR_SIZE];

	hdd_read(0, &buffer);

	/* Skontrolujeme, ci v prvom sektore je ulozene meno nasho suboru */
	if (memcmp(buffer, path, strnlen(path,12)))
			return NULL;

	/* Subor existuje, alokujeme pren deskriptor */
	file_t *fd = fd_alloc();

	/* mame iba jeden jediny subor, deskriptor vyplnime samymi nulami */
	fd->info[FILE_T_OFFSET] = 0;
	fd->info[1] = 0;
	fd->info[2] = 0;
	fd->info[3] = 0;

	return fd;
}

/**
 * Zatvori otvoreny file handle.
 *
 * Funkcia zatvori handle, ktory bol vytvoreny pomocou volania 'open' alebo
 * 'creat' a uvolni prostriedky, ktore su s nim spojene. V pripade akehokolvek
 * zlyhania vrati FAIL.
 */
int fs_close(file_t *fd)
{
	/* Uvolnime filedescriptor, aby sme neleakovali pamat */
	fd_free(fd);
	return OK;
}

/**
 * Odstrani subor na ceste 'path'.
 *
 * Ak zadana cesta existuje a je to subor, odstrani subor z disku; nemeni
 * adresarovu strukturu. V pripade chyby vracia FAIL.
 */
int fs_unlink(const char *path)
{
	return FAIL;
}

/**
 * Premenuje/presunie polozku v suborovom systeme z 'oldpath' na 'newpath'.
 *
 * Po uspesnom vykonani tejto funkcie bude subor, ktory doteraz existoval na
 * 'oldpath' dostupny cez 'newpath' a 'oldpath' prestane existovat. Opat,
 * funkcia nemanipuluje s adresarovou strukturou (nevytvara nove adresare
 * z cesty newpath, okrem posledneho v pripade premenovania adresara).
 * V pripade zlyhania vracia FAIL.
 */
int fs_rename(const char *oldpath, const char *newpath)
{
	return FAIL;
}

/**
 * Nacita z aktualnej pozicie vo 'fd' do bufferu 'bytes' najviac 'size' bajtov.
 *
 * Z aktualnej pozicie v subore precita funkcia najviac 'size' bajtov; na konci
 * suboru funkcia vracia 0. Po nacitani dat zodpovedajuco upravi poziciu v
 * subore. Vrati pocet precitanych bajtov z 'bytes', alebo FAIL v pripade
 * zlyhania. Existujuci subor prepise.
 */
int fs_read(file_t *fd, uint8_t *bytes, size_t size)
{
	/* Podporujeme iba subory s maximalnou velkostou SECTOR_SIZE */
	uint8_t buffer[SECTOR_SIZE] = { 0 };
	/* Vo filedescriptore je ulozena nasa aktualna pozicia v subore */
	int offset = fd->info[FILE_T_OFFSET];

	/* Nacitame celkovu velkost suboru na disku */
	hdd_read(0, buffer);
	size_t file_size = ((zero_sector_t*)buffer)->size;

	hdd_read(1, buffer);
	size_t i;
	for (i = 0; (i < size) && ((i + offset) < file_size); i++) {
		bytes[i] = buffer[offset + i];
	}

	/* Aktualizujeme offset, na ktorom sme teraz */
	fd->info[FILE_T_OFFSET] += i;

	/* Vratime pocet precitanych bajtov */
	return i;
}

/**
 * Zapise do 'fd' na aktualnu poziciu 'size' bajtov z 'bytes'.
 *
 * Na aktualnu poziciu v subore zapise 'size' bajtov z 'bytes'. Ak zapis
 * presahuje hranice suboru, subor sa zvacsi; ak to nie je mozne, zapise sa
 * maximalny mozny pocet bajtov. Po zapise korektne upravi aktualnu poziciu v
 * subore a vracia pocet zapisanych bajtov z 'bytes'.
 * 
 * Write existujuci obsah suboru prepisuje, nevklada dovnutra nove data.
 * Write pre poziciu tesne za koncom existujucich dat zvacsi velkost suboru.
 */
int fs_write(file_t *fd, const uint8_t *bytes, size_t size)
{
	uint8_t buffer[SECTOR_SIZE] = { 0 };
	/* Vo filedescriptore je ulozena nasa aktualna pozicia v subore */
	int offset = fd->info[FILE_T_OFFSET];

	/* Nacitame celkovu velkost suboru na disku */
	hdd_read(0, buffer);
	size_t file_size = ((zero_sector_t*)buffer)->size;

	/* Nacitame stare data do buffera a prepiseme ich novymi */
	hdd_read(1, buffer);
	size_t i;
	for (i = 0; (i < size) && ((i + offset) < SECTOR_SIZE); i++) {
		buffer[offset + i] = bytes[i];
	}
	hdd_write(1, buffer);

	/* Ak subor narastol, aktualizujeme velkost */

	if (file_size < offset + i) {
		hdd_read(0, buffer);
		((zero_sector_t*)buffer)->size = offset + i;
		hdd_write(0, buffer);
	}

	/* Aktualizujeme offset, na ktorom sme */
	fd->info[FILE_T_OFFSET] += i;

	/* Vratime pocet zapisanych bajtov */
	return i;
}

/**
 * Zmeni aktualnu poziciu v subore na 'pos'-ty byte.
 *
 * Upravi aktualnu poziciu; ak je 'pos' mimo hranic suboru, vrati FAIL a pozicia
 * sa nezmeni, inac vracia OK.
 */
int fs_seek(file_t *fd, size_t pos)
{
	uint8_t buffer[SECTOR_SIZE] = { 0 };

	/* Nacitaj velkost suboru z disku */
	hdd_read(0, buffer);
	size_t file_size = ((zero_sector_t*)buffer)->size;

	/* Nemozeme seekovat za velkost suboru */
	if (pos > file_size) {
		fprintf(stderr, "Can not seek: %lu > %lu\n", pos, file_size);
		return FAIL;
	}

	fd->info[FILE_T_OFFSET] = pos;

	return OK;
}


/**
 * Vrati aktualnu poziciu v subore.
 */

size_t fs_tell(file_t *fd) {
	return fd->info[FILE_T_OFFSET];
}


/**
 * Vrati informacie o 'path'.
 *
 * Funkcia vrati FAIL ak cesta neexistuje, alebo vyplni v strukture 'fs_stat'
 * polozky a vrati OK:
 *  - st_size: velkost suboru v byte-och
 *  - st_nlink: pocet hardlinkov na subor (ak neimplementujete hardlinky, tak 1)
 *  - st_type: hodnota podla makier v hlavickovom subore: STAT_TYPE_FILE,
 *  STAT_TYPE_DIR, STAT_TYPE_SYMLINK
 *
 */

int fs_stat(const char *path, struct fs_stat *fs_stat) { 
	uint8_t buffer[SECTOR_SIZE] = { 0 };
	
	/* Nacitaj velkost suboru z disku */
	hdd_read(0, buffer);

	/* Ak subor neexistuje, FAIL */
	if (buffer[0] == 0)
		return FAIL;

	size_t file_size = ((zero_sector_t*)buffer)->size;
	fs_stat->st_size = file_size;
	fs_stat->st_nlink = 1;
	fs_stat->st_type = STAT_TYPE_FILE;

	return OK;
}

/* Level 3 */
/**
 * Vytvori adresar 'path'.
 *
 * Ak cesta, v ktorej adresar ma byt, neexistuje, vrati FAIL (vytvara najviac
 * jeden adresar), pri korektnom vytvoreni OK.
 */
int fs_mkdir(const char *path) { return FAIL; }

/**
 * Odstrani adresar 'path'.
 *
 * Odstrani prazdny adresar, na ktory ukazuje 'path'; ak obsahuje subory, neexistuje alebo nie je
 * adresar, vrati FAIL; po uspesnom dokonceni vrati OK.
 */
int fs_rmdir(const char *path) { return FAIL; }

/**
 * Otvori adresar 'path' (na citanie poloziek)
 *
 * Vrati handle na otvoreny adresar s poziciou nastavenou na 0; alebo FAIL v
 * pripade zlyhania.
 */
file_t *fs_opendir(const char *path) { return (file_t*)FAIL; }

/**
 * Nacita nazov dalsej polozky z adresara.
 *
 * Do dodaneho buffera ulozi nazov polozky v adresari, posunie aktualnu
 * poziciu na dalsiu polozku a vrati OK.
 * V pripade problemu, alebo ak nasledujuca polozka neexistuje, vracia FAIL.
 * (V pripade jedneho suboru v adresari vracia FAIL az pri druhom volani.)
 */
int fs_readdir(file_t *dir, char *item) {return FAIL; }

/**
 * Zatvori otvoreny adresar.
 */
int fs_closedir(file_t *dir) { return FAIL; }

/* Level 4 */
/**
 * Vytvori hardlink zo suboru 'path' na 'linkpath'.
 */
int fs_link(const char *path, const char *linkpath) { return FAIL; }

/**
 * Vytvori symlink z 'path' na 'linkpath'.
 */
int fs_symlink(const char *path, const char *linkpath) { return FAIL; }

