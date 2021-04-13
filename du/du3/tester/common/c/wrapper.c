#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "util.h"
#include "filesystem.h"

#define MAX_LINE 512

int hex2bin(char c) { assert ((('0' <= c) && (c <= '9')) || (('a' <=c) && (c <= 'f'))); return c - ((c<='9')?'0':('a'-10)); }
char bin2hex(uint8_t i) { assert(i < 16); return (i<10)?('0'+i):('a'+i-10);}

uint8_t *hex_to_array(const char *array)
{
	static uint8_t ret[MAX_LINE];
	size_t len = strlen(array);

	assert(len < MAX_LINE/2);

	for (size_t i = 0; i < len-1; i += 2)
		ret[i/2] = (hex2bin(array[i])<<4) + hex2bin(array[i+1]);
	return ret;
}

char *array_to_hex(const uint8_t *array, int len)
{
	int i;
	static char ret[MAX_LINE];
	assert (len*2 < MAX_LINE);

	for (i = 0; i < len; i++) {
		ret[2*i] = bin2hex(array[i]>>4);
		ret[2*i+1] = bin2hex(array[i]&0xf);
	}
	ret[2*i] = 0;

	return ret;
}

int main(int argc, char *argv[])
{
	int quit = 0;

	if (argc == 3)
		util_init(argv[1], atoi(argv[2]));
	else
		util_init("disk.bin", 65536);

	while (!quit) {
		char buffer[MAX_LINE];
		uint8_t data[MAX_LINE];
		char path[MAX_PATH] = { 0 }, path2[MAX_PATH] = { 0 };
		char command[16];
		int ret = 0;
		size_t pos = 0, len = 0;
		file_t *fd = NULL;

		fflush(stdout);
		util_reset_counters();
		fgets(buffer, MAX_LINE, stdin);
		sscanf(buffer, "%15s", command);

		/* Level 1 */
		if (0) {
		} else if (!strcmp(command, "creat")) {
			sscanf(buffer, "%*s %s\n", path);
			file_t* fret = fs_creat(path);
			printf("%ld # %lu %lu\n", (long)fret, util_get_reads(), util_get_writes());
			continue;
		} else if (!strcmp(command, "open")) {
			sscanf(buffer, "%*s %s\n", path);
			file_t* fret = fs_open(path);
			printf("%ld # %lu %lu\n", (long)fret, util_get_reads(), util_get_writes());
			continue;
		} else if (!strcmp(command, "close")) {
			sscanf(buffer, "%*s %ld\n", (long *)&fd);
			ret = fs_close(fd);
		} else if (!strcmp(command, "unlink")) {
			sscanf(buffer, "%*s %s\n", path);
			ret = fs_unlink(path);
		} else if (!strcmp(command, "rename")) {
			sscanf(buffer, "%*s %s %s\n", path, path2);
			ret = fs_rename(path, path2);
		} else if (!strcmp(command, "rename")) {
			sscanf(buffer, "%*s %s %s\n", path, path2);
			ret = fs_rename(path, path2);
		/* Level 2 */
		} else if (!strcmp(command, "read")) {
			sscanf(buffer, "%*s %ld %lu\n", (long *)&fd, &len);
			ret = fs_read(fd, data, len);
			if (ret >= 0) {
				printf("%d %s # %lu %lu\n", ret, array_to_hex(data, ret), util_get_reads(), util_get_writes());
				continue;
			};
		} else if (!strcmp(command, "write")) {
			char dataToWrite[MAX_LINE];
			sscanf(buffer, "%*s %ld %s %lu\n", (long *)&fd, dataToWrite, &len);
			ret = fs_write(fd, hex_to_array(dataToWrite), len);
		} else if (!strcmp(command, "seek")) {
			sscanf(buffer, "%*s %ld %lu\n", (long *)&fd, &pos);
			ret = fs_seek(fd, pos);
		} else if (!strcmp(command, "tell")) {
			sscanf(buffer, "%*s %ld\n", (long *)&fd);
			ret = fs_tell(fd);
		} else if (!strcmp(command, "stat")) {
			sscanf(buffer, "%*s %s\n", path);
			fs_stat_t stat;
			ret = fs_stat(path, &stat);
			if (ret>=0) {
				printf("%d %s # %lu %lu\n", ret, array_to_hex((uint8_t*) &stat, sizeof(stat)), util_get_reads(), util_get_writes());
				continue;
			}
		/* Level 3 */
		} else if (!strcmp(command, "mkdir")) {
			sscanf(buffer, "%*s %s\n", path);
			ret = fs_mkdir(path);
		} else if (!strcmp(command, "rmdir")) {
			sscanf(buffer, "%*s %s\n", path);
			ret = fs_rmdir(path);
		} else if (!strcmp(command, "opendir")) {
			sscanf(buffer, "%*s %s\n", path);
			file_t* fret = fs_opendir(path);
			printf("%ld # %lu %lu\n", (long)fret, util_get_reads(), util_get_writes());
			continue;
		} else if (!strcmp(command, "readdir")) {
			sscanf(buffer, "%*s %ld\n", (long *)&fd);
			ret = fs_readdir(fd, (char*)buffer);
			if (ret >= 0) {
				printf("%d %s # %lu %lu\n", ret, buffer, util_get_reads(), util_get_writes());
				continue;
			}
		} else if (!strcmp(command, "closedir")) {
			sscanf(buffer, "%*s %ld\n", (long *)&fd);
			ret = fs_closedir(fd);
		
		/* Level 4 */
		} else if (!strcmp(command, "link")) {
			sscanf(buffer, "%*s %s %s\n", path, path2);
			ret = fs_link(path, path2);
		} else if (!strcmp(command, "symlink")) {
			sscanf(buffer, "%*s %s %s\n", path, path2);
			ret = fs_symlink(path, path2);
		} else if (!strcmp(command, "end")) {
			util_end();
			ret = 0;
			quit = 1;
		} else 
			ret = -1;
		

		printf("%d # %lu %lu\n", ret, util_get_reads(), util_get_writes());
	}
}
