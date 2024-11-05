#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    FILE *fp;
    char *line = NULL;
    size_t len = 0;
    ssize_t read;
    unsigned long ln = 0;
    unsigned long lnum = 0;
    unsigned long size = 0;
    int cnt = 0;
    unsigned long line_chunk_size = atoi(*(argv+2));

    fp = fopen(*(argv+1), "r");
    if (fp == NULL)
        exit(EXIT_FAILURE);

    while ((read = getline(&line, &len, fp)) != -1) {
        size += read;
        ln++;
        lnum++;
        if (ln == line_chunk_size) {
            /* printf("%lu | %s", lnum, line); */
            /* printf("%d * line_chunk_size -> %zu\n", cnt, size); */
            ln = 0;
            cnt++;
            printf("%zu\n", size);
        }
        /* printf("Retrieved line of length %zu:\n", read); */
        /* printf("%s", line); */
    }
    printf("%zu\n", size);

    fclose(fp);
    if (line)
        free(line);
    exit(EXIT_SUCCESS);
}

