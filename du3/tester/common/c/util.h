#ifndef WRAPPER_H
#define WRAPPER_H

#include "filesystem.h"

size_t hdd_size();
void hdd_read(size_t sector, void *buffer);
void hdd_write(size_t sector, void *buffer);

file_t *fd_alloc();
void fd_free(file_t *fd);

/* Nasledujuce API je pre wrapper, nepouzivajte ho */

void util_reset_counters();
size_t util_get_reads();
size_t util_get_writes();
	
int util_init(const char *disk_path, size_t my_size);
void util_end();

#endif
