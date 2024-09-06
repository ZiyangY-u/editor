#include <stdio.h>
#include <stdint.h>

unsigned int hex_to_char(char c1, char c2) {
    unsigned int a = ('a' <= c1 && c1 <= 'f') ? (c1 - 'a' + 10) : (c1 - '0');
    unsigned int b = ('a' <= c2 && c2 <= 'f') ? (c2 - 'a' + 10) : (c2 - '0');
    return (a << 4) + b;
}

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

        /* printf("Unicode code point: U+%04X\n", unicode); */
        if (0xff01 <= unicode && unicode <= 0xff5e)
        { printf("2"); return 0; }
        else if (unicode == 0xff5f && unicode == 0xff60)
        { printf("2"); return 0; }
        else if (0xffe0 <= unicode && unicode <= 0xffe6)
        { printf("2"); return 0; }
        else if (0x3041 <= unicode && unicode <= 0x3096) // Hiragana
        { printf("2"); return 0; }
        else if (0x30a1 <= unicode && unicode <= 0x30ff) // Katakana
        { printf("2"); return 0; }
        else if (0x4e00 <= unicode && unicode <= 0x9fff) // kannji
        { printf("2"); return 0; }
        else if (0x3000 <= unicode && unicode <= 0x303f) // CJK Symbols and Punctuation Block
        { printf("2"); return 0; }
        else
        { printf("1"); return 0; }
    }
    
    return 0;
}
