#ifndef FILESYSTEM_H
#define FILESYSTEM_H

#include <stdint.h>
#include <stddef.h>

#define MAX_FILENAME 12 /* Maximalna dlzka nazvu suboru v znakoch */
#define MAX_PATH 64 	/* Maximalna dlzka cesty v znakoch */
#define SECTOR_SIZE 128	/* Velkost sektora na disku v bajtoch */

/* Oddelovac poloziek v adresarovej strukture */
#define PATHSEP '/'

#define OK  	0
#define FAIL	(-1)

/* Typy pre fs_stat_t.st_type */
enum {
	STAT_TYPE_FILE    = 0,
	STAT_TYPE_DIR     = 1,
	STAT_TYPE_SYMLINK = 2,
};

typedef struct fs_stat {
	uint32_t st_size;  /* file size */
	uint32_t st_nlink; /* number of hard links */
	uint32_t st_type;  /* type, e.g. STAT_TYPE_DIR */
} fs_stat_t;

/* File handle pre otvorenu polozku. Na kazdy otvoreny subor mate 16 bajtov, v
 * ktorych si mozete pamatat lubovolne informacie.
 * Na alokovanie pouzivajte fd_alloc().
 */
typedef struct {
	uint32_t info[4];
} file_t;

/* Level 1 */

void fs_format();

file_t *fs_creat(const char *path);
file_t *fs_open(const char *path);
int fs_close(file_t *fd);
int fs_unlink(const char *path);
int fs_rename(const char *oldpath, const char *newpath);

/* Level 2 */

int fs_read(file_t *fd, uint8_t *bytes, size_t size);
int fs_write(file_t *fd, const uint8_t *bytes, size_t size);
int fs_seek(file_t *fd, size_t pos);
size_t fs_tell(file_t *fd);
int fs_stat(const char *path, struct fs_stat *fs_stat);

/* Level 3 */

int fs_mkdir(const char *path);
int fs_rmdir(const char *path);
file_t *fs_opendir(const char *path);
int fs_readdir(file_t *dir, char *item);
int fs_closedir(file_t *dir);

/* Level 4 */

int fs_link(const char *path, const char *linkpath);
int fs_symlink(const char *path, const char *linkpath);

#endif
