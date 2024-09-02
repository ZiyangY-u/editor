#include <stdio.h>
#include <stdlib.h>

#define LIST_LEN 1000

struct quote {
    int vcol;
    char qc; /* quote char */
};

struct quote list[LIST_LEN];
int lp = -1;
void push(struct quote q) {
    if (lp < LIST_LEN)
        list[++lp] = q;
    else
        perror("error: stack full, can't push\n");
}

int is_quote(char c) {
    if (c == '\'' || c == '"')
        return 1;
    return 0;
}

int is_single_quote(int list_idx) {
    if (list[list_idx].qc == '\'')
        return 1;
    return 0;
}
int is_double_quote(int list_idx) {
    if (list[list_idx].qc == '"')
        return 1;
    return 0;
}

int find_close_quote(int start_lp, char quote) {
    for (int i = start_lp+1 ; i < lp ; i++)
        if (list[i].qc == quote)
            return list[i].vcol;
    return 0;
}
int find_start_quote(int start_lp, char quote) {
    for (int i = start_lp-1 ; i >= 0 ; i++)
        if (list[i].qc == quote)
            return list[i].vcol;
    return 0;
}

unsigned int hex_to_char(char c1, char c2) {
    unsigned int a = ('a' <= c1 && c1 <= 'f') ? (c1 - 'a' + 10) : (c1 - '0');
    unsigned int b = ('a' <= c2 && c2 <= 'f') ? (c2 - 'a' + 10) : (c2 - '0');
    return (a << 4) + b;
}

int main(int argc, char *argv[])
{
    int col = atoi(argv[1]);
    int ts = atoi(argv[2]);
    int vcol = 1;
    char c1, c2, c;
    int to_esc = 0;
    struct quote q;
    /* store all quotes to list */
    while ((c1 = getchar()) != EOF) {
        c2 = getchar();
        c = hex_to_char(c1, c2);
        if (c == '\t') {
            vcol += ts;
            continue;
        }

        if (to_esc) {
            to_esc = 0;
            vcol++;
            continue;
        }
        if (c == '\\') {
            to_esc = 1;
            vcol++;
            continue;
        }

        if ((c & 0xF0) == 0xF0) { /* four-byte unicode */
            getchar(); getchar(); getchar();
            getchar(); getchar(); getchar();
            vcol++;
        } else if ((c & 0xE0) == 0xE0) {
            getchar(); getchar();
            getchar(); getchar();
            vcol++;
        } else if ((c & 0xC0) == 0xC0) {
            getchar(); getchar();
        }

        if (to_esc != 1 && is_quote(c)) {
            q.vcol = vcol;
            q.qc = c;
            push(q);
        }
        vcol++;
    }

    /* for (int i = 0 ; i <= lp ; i++) { */
    /*     struct quote q = list[i]; */
    /*     printf("%c %d\n", q.qc, q.vcol); */
    /* } */

    if (lp == 0)
        return 0;

    int colp = 0, close_quote;
    int find_surround_flg = 1;

    while (list[colp].vcol <= col)
        if (++colp == lp) break;

    if (list[colp].vcol == col) {
        /* find forward */
        if (colp % 2 == 1 && (close_quote = find_close_quote(colp, list[colp].qc)) != 0)
            printf("%d %d", list[colp].vcol, close_quote);
        /* find backward */
        if (colp % 2 == 0 && (close_quote = find_start_quote(colp, list[colp].qc)) != 0)
            printf("%d %d", close_quote, list[colp].vcol);
        find_surround_flg = 0;
    }

    /* if (find_surround_flg == 1) */
    /*     for (int i = colp ; i >= 0 ; i--) */
    /*         if (i % 2 == 0 && (close_quote = find_close_quote(i, list[i].qc)) != 0) { */
    /*             /1* printf("by sourround\n"); *1/ */
    /*             printf(" %d %d", list[i].vcol, close_quote); */
    /*             break; */
    /*         } */

    /* /1* find next quote *1/ */
    /* for (int i = colp+1 ; i < lp ; i++) */ 
    /*     if (i % 2 == 1 && (close_quote = find_close_quote(i, list[i].qc)) != 0) { */
    /*         /1* printf("by next\n"); *1/ */
    /*         printf(" %d %d", list[i].vcol, close_quote); */
    /*         break; */
    /*     } */

    return 0;
}
