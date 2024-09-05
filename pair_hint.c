#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <stdint.h>

#define STACK_DEEP 1000

struct pair {
    int vcol;
    char bracket;
};

struct pair stack[STACK_DEEP];
int sp = -1;
void push(struct pair p) {
    if (sp < STACK_DEEP)
        stack[++sp] = p;
    else
        perror("error: stack full, can't push\n");
}

/* lbs 28 ( rbs 29 )
 * lbm 5b [ rbm 5d ]
 * lbb 7b { rbb 7d }
 * tab 09
 * */

int is_lb(char c) {
    if (c == '(' || c == '[' || c == '{')
        return 1;
    return 0;
}
int is_rb(char c) {
    if (c == ')' || c == ']' || c == '}')
        return 1;
    return 0;
}

int is_left_bracket(int stack_idx) {
    if (stack[stack_idx].bracket == '(' || stack[stack_idx].bracket == '[' || stack[stack_idx].bracket == '{')
        return 1;
    return 0;
}

int is_right_bracket(int stack_idx) {
    if (stack[stack_idx].bracket == ')' || stack[stack_idx].bracket == ']' || stack[stack_idx].bracket == '}')
        return 1;
    return 0;
}

unsigned int hex_to_char(char c1, char c2) {
    unsigned int a = ('a' <= c1 && c1 <= 'f') ? (c1 - 'a' + 10) : (c1 - '0');
    unsigned int b = ('a' <= c2 && c2 <= 'f') ? (c2 - 'a' + 10) : (c2 - '0');
    return (a << 4) + b;
}

char get_target(char bracket) {
    switch (bracket) {
        case '(': return ')';
        case '[': return ']';
        case '{': return '}';
        case ')': return '(';
        case ']': return '[';
        case '}': return '{';
        default: break;
    }
    return bracket;
}

int find_close_bracket(int start_sp) {
    int bdepth = 0;
    char target = get_target(stack[start_sp].bracket);
    for (int i = start_sp+1 ; i <= sp ; i++) {
        if (is_left_bracket(i))
            bdepth++;
        if (bdepth == 0 && is_right_bracket(i) && target == stack[i].bracket)
            return i;
        if (bdepth != 0 && is_right_bracket(i))
            bdepth--;
    }
    return -1;
}

int find_start_brackt(int start_sp) {
    int bdepth = 0;
    char target = get_target(stack[start_sp].bracket);
    for (int i = start_sp-1 ; i >= 0 ; i--) {
        if (is_right_bracket(i))
            bdepth++;
        if (bdepth == 0 && is_left_bracket(i) && target == stack[i].bracket)
            return i;
        if (bdepth != 0 && is_left_bracket(i))
            bdepth--;
    }
    return -1;
}

/* pair hint:
 * first param : cursor column
 * second param : tabstop */
int main(int argc, char *argv[])
{
    int col = atoi(argv[1]);
    int ts = atoi(argv[2]);
    int vcol = 1;
    char c1, c2, c;
    uint32_t unicode;
    struct pair p;
    /* store all bracket to stack */
    while ((c1 = getchar()) != EOF) {
        c2 = getchar();
        c = hex_to_char(c1, c2);
        if (c == '\t') {
            vcol += ts;
            continue;
        }
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
            vcol++; /* printf("2 col: U+%04X\n", unicode); */
        else if (unicode == 0xff5f && unicode == 0xff60)
            vcol++; /* printf("2 col: U+%04X\n", unicode); */
        else if (0xffe0 <= unicode && unicode <= 0xffe6)
            vcol++; /* printf("2 col: U+%04X\n", unicode); */
        else if (0x3041 <= unicode && unicode <= 0x3096) // Hiragana
            vcol++; /* printf("2 col: U+%04X\n", unicode); */
        else if (0x30a1 <= unicode && unicode <= 0x30ff) // Katakana
            vcol++; /* printf("2 col: U+%04X\n", unicode); */
        else if (0x4e00 <= unicode && unicode <= 0x9fff) // kannji
            vcol++; /* printf("2 col: U+%04X\n", unicode); */
        else if (0x3000 <= unicode && unicode <= 0x303f) // CJK Symbols and Punctuation Block
            vcol++; /* printf("2 col: U+%04X\n", unicode); */

        if (is_lb(c) || is_rb(c)) {
            p.vcol = vcol;
            p.bracket = c;
            push(p);
        }
        vcol++;
    }

    /* for (int i = 0 ; i <= sp ; i++) { */
    /*     struct pair p = stack[i]; */
    /*     printf("%c %d\n", p.bracket, p.vcol); */
    /* } */

    if (sp == 0) /* no brakets */
        return 0;

    int brackt_depth = 0;
    int colp = 0;
    int cci; // close col index
    int find_surround_flg = 1;

    while (stack[colp+1].vcol <= col)
        if (++colp == sp) break;

    /* print column number relative to current column */
    if (stack[colp].vcol == col) {
        if (is_left_bracket(colp) && (cci = find_close_bracket(colp)) != -1)
            printf("%d%c %d%c", stack[colp].vcol - col, stack[colp].bracket, stack[cci].vcol - col, stack[cci].bracket);
        if (is_right_bracket(colp) && (cci = find_start_brackt(colp)) != -1)
            printf("%d%c %d%c", stack[cci].vcol - col, stack[cci].bracket, stack[colp].vcol - col, stack[colp].bracket);
        find_surround_flg = 0;
    }

    /* find surrounding bracket */
    if (find_surround_flg == 1)
        for (int i = colp ; i >= 0 ; i--) {
            if (brackt_depth == 0 && is_left_bracket(i) && (cci = find_close_bracket(i)) != -1) {
                printf(" %d%c %d%c", stack[i].vcol - col, stack[i].bracket, stack[cci].vcol - col, stack[cci].bracket);
                break;
            }
            if (is_right_bracket(i))
                brackt_depth++;
            if (is_left_bracket(i))
                brackt_depth--;
        }

    /* find next bracket */
    for (int i = colp+1 ; i < sp ; i++) {
        if (is_left_bracket(i) && (cci = find_close_bracket(i)) != -1) {
            printf(" %d%c %d%c", stack[i].vcol - col, stack[i].bracket, stack[cci].vcol - col, stack[cci].bracket);
            break;
        }
    }

    return 0;
}
