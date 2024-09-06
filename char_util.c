#include <stdint.h>
#include <stdbool.h>

int is_fullwidth(uint32_t unicode)
{

    /* printf("Unicode code point: U+%04X\n", unicode); */
    if (0xff01 <= unicode && unicode <= 0xff5e)
        return true;
    else if (unicode == 0xff5f && unicode == 0xff60)
        return true;
    else if (0xffe0 <= unicode && unicode <= 0xffe6)
        return true;
    else if (0x3041 <= unicode && unicode <= 0x3096) // Hiragana
        return true;
    else if (0x30a1 <= unicode && unicode <= 0x30ff) // Katakana
        return true;
    else if (0x4e00 <= unicode && unicode <= 0x9fff) // kannji
        return true;
    else if (0x3000 <= unicode && unicode <= 0x303f) // CJK Symbols and Punctuation Block
        return true;
    else
        return false;

}

unsigned int hex_to_char(char c1, char c2)
{
    unsigned int a, b;

    if ('a' <= c1 && c1 <= 'f')
        a = (c1 - 'a' + 10);
    else if ('A' <= c1 && c1 <= 'F')
        a = (c1 - 'A' + 10);
    else
        a = (c1 - '0');

    if ('a' <= c2 && c2 <= 'f')
        b = (c2 - 'a' + 10);
    else if ('A' <= c2 && c2 <= 'F')
        b = (c2 - 'A' + 10);
    else
        b = (c2 - '0');

    return (a << 4) + b;
}
