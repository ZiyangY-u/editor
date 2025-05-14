#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 1st param: file path
// 2nd param: offset
// 3rd param: start line number
// 4th param: end line number
// 5th param: offset line
int main(int argc, char *argv[])
{
    FILE *fp;
    /* printf("%s\n", *(argv+1)); */
    fp = fopen(*(argv+1), "r");
    fseek(fp, atoi(*(argv+2)), SEEK_SET);
    char *line = NULL;
    size_t len = 0;
    ssize_t read;
    unsigned long start = atoi(*(argv+3));
    unsigned long end = atoi(*(argv+4));
    unsigned long offset_ln = atoi(*(argv+5));
    unsigned long ln = offset_ln+1;
    /* printf("%lu %lu %lu %lu\n", start, end, offset_ln, ln); */

    while ((read = getline(&line, &len, fp)) != -1) {
        /* printf("%s", line); */
        if (start <= ln && ln <= end) {
            size_t llen = strcspn(line, "\r\n"); // Find the index of \r or \n
            line[llen] = '\0';                   // Replace it with null terminator
            printf("%4lu |%s\n", ln , line);
        }
        if (ln > end)
            exit(0);
        ln++;
    }
    
    return 0;
}

