#ifndef WRAPPER_H
#define WRAPPER_H

int hd_sector_size();
void* hd_read(int sector);
int hd_write(int sector, void *data);



#endif
