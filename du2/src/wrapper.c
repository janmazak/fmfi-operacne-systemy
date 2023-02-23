#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include "wrapper.h"

int MEMORY_SIZE = 4096;
static FILE *mem = NULL;

int minit(void) {
	assert(mem == NULL);

	mem = fopen("memory.bin", "rb+");
	if (mem == NULL) {
		/* Set up size of the file, if it does not exist */
		unsigned char c=0;
		int i;
		mem = fopen("memory.bin", "wb+");
		fseek(mem, 0, SEEK_SET);
		for (i = 0; i < MEMORY_SIZE; i++)
			fwrite(&c, 1, 1, mem);

		my_init();
	} else {
		fseek(mem, 0 , SEEK_END);
		int file_size = ftell(mem);
		assert(file_size == MEMORY_SIZE);
	}

	if (!mem) {
		perror("fopen");
		return -1;
	}
	
	return 0;
}

int mdone(void) {
	assert(mem != NULL);

	fclose(mem);
	mem = NULL;
}

uint8_t mread(unsigned int addr) {
	uint8_t data = 0;
	assert(mem != NULL);
	assert((0 <= addr) && (addr < MEMORY_SIZE));

	int seek_ret = fseek(mem, addr, SEEK_SET);
	assert(seek_ret == 0);
	int fread_ret = fread(&data, 1, 1, mem);
	assert(fread_ret == 1);

	return data;
}

void mwrite(unsigned int addr, uint8_t val) {
	uint8_t data = 0;
	assert(mem != NULL);
	assert((0 <= addr) && (addr < MEMORY_SIZE));

	int fseek_ret = fseek(mem, addr, SEEK_SET);
	assert(fseek_ret == 0);
	int fwrite_ret = fwrite(&val, 1, 1, mem);
	assert(fwrite_ret == 1);
	int fflush_ret = fflush(mem);
	assert(fflush_ret == 0);
}

unsigned int msize(void) {
	return MEMORY_SIZE;
}

#define MAX_LINE_LENGTH 256

int main(int argc, char *argv[]) {
	char line[MAX_LINE_LENGTH];
	char command[16];
	int data, data2;
	int params;

	if (argc >1)
		MEMORY_SIZE = atoi(argv[1]);
	else
		MEMORY_SIZE = 4096;

	assert (MEMORY_SIZE > 0);

	minit();

	while (!feof(stdin)) {
		fgets(line, MAX_LINE_LENGTH, stdin);
		params = sscanf(line, "%15s %d %d\n", command, &data, &data2);

		if (0) {}
		else if (!strcmp(command, "alloc") && params == 2)
			fprintf(stdout, "%d\n", my_alloc(data)); 
		else if (!strcmp(command, "free") && params == 2)
			fprintf(stdout, "%d\n", my_free(data));
		else if (!strcmp(command, "read") && params == 2)
			fprintf(stdout, "%d\n", mread(data));
		else if (!strcmp(command, "write") && params == 3) {
			mwrite(data, data2);
			fprintf(stdout, "%d\n", 0);
		} else if (!strcmp(command, "end") && params == 1)
			break;
		else
			fprintf(stderr, "Unknown command line '%s'\n", line);
		fflush(stdout);
	}

	mdone();

	return 0;
}


