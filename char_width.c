#include <stdio.h>
#include <stdint.h>

int is_fullwidth(uint32_t unicode);
unsigned int hex_to_char(char c1, char c2);

int main(int argc, char *argv[])
{
    char c1, c2, c;
    uint32_t unicode;
    while ((c1 = getchar()) != EOF) {
        c2 = getchar();
        c = hex_to_char(c1, c2);
        if ((c & 0x80) == 0) {
            /* 1-byte character (ASCII) */
            unicode = c;
        } else if (((c & 0xE0) == 0xC0)) {
            /* 2-byte character */
            unicode = c & 0x1F;
            c1 = getchar(); c2 = getchar();
            unicode = (unicode << 6) | (hex_to_char(c1, c2) & 0x3f);
        } else if ((c & 0xF0) == 0xE0) {
            /* 3-byte character */
            unicode = c & 0x0F;
            for (int i = 0 ; i < 2 ; i++) {
                c1 = getchar(); c2 = getchar();
                unicode = (unicode << 6) | (hex_to_char(c1, c2) & 0x3f);
            }
        } else if ((c & 0xF8) == 0xF0) {
            /* 4-byte character */
            unicode = c & 0x07;
            for (int i = 0 ; i < 3 ; i++) {
                c1 = getchar(); c2 = getchar();
                unicode = (unicode << 6) | (hex_to_char(c1, c2) & 0x3f);
            }
        }

        if (is_fullwidth(unicode)) {
            printf("2");
            return 0;
        }
        printf("1");
    }
    
    return 0;
}
