#include <stdio.h>
#include <stdlib.h>

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

/* lbs 28 (
 * rbs 29 )
 * lbm 5b [
 * rbm 5d ]
 * lbb 7b {
 * rbb 7d }
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
            return stack[i].vcol;
        if (bdepth != 0 && is_right_bracket(i))
            bdepth--;
    }
    return 0;
}

int find_start_brackt(int start_sp) {
    int bdepth = 0;
    char target = get_target(stack[start_sp].bracket);
    for (int i = start_sp-1 ; i >= 0 ; i--) {
        if (is_right_bracket(i))
            bdepth++;
        if (bdepth == 0 && is_left_bracket(i) && target == stack[i].bracket)
            return stack[i].vcol;
        if (bdepth != 0 && is_left_bracket(i))
            bdepth--;
    }
    return 0;
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
    unsigned int unicode;
    struct pair p;
    /* store all bracket to stack */
    while ((c1 = getchar()) != EOF) {
        c2 = getchar();
        c = hex_to_char(c1, c2);
        if (c == '\t') {
            vcol += ts;
            continue;
        }
        if ((c & 0xF0) == 0xF0) { /* four-byte unicode */
            unicode = c;
            for (int i = 0 ; i < 3 ; i++) {
                c1 = getchar(); c2 = getchar();
                unicode = unicode << 8;
                unicode += hex_to_char(c1, c2);
            }
            vcol++;
        } else if ((c & 0xE0) == 0xE0) { /* three-byte unicode */
            unicode = c;
            for (int i = 0 ; i < 2 ; i++) {
                c1 = getchar(); c2 = getchar();
                unicode = unicode << 8;
                unicode |= hex_to_char(c1, c2);
            }
            vcol++;
        } else if ((c & 0xC0) == 0xC0) { /* two-byte unicode */
            unicode = c;
            c1 = getchar(); c2 = getchar();
            unicode = unicode << 8;
            unicode += hex_to_char(c1, c2);
            vcol++;
        }
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
    int close_col;
    int find_surround_flg = 1;

    while (stack[colp+1].vcol <= col)
        if (++colp == sp) break;

    if (stack[colp].vcol == col) {
        if (is_left_bracket(colp) && (close_col = find_close_bracket(colp)) != 0)
            printf("%d %d", stack[colp].vcol, close_col);
        if (is_right_bracket(colp) && (close_col = find_start_brackt(colp)) != 0)
            printf("%d %d", close_col, stack[colp].vcol);
        find_surround_flg = 0;
    }

    /* find surrounding bracket */
    if (find_surround_flg == 1)
        for (int i = colp ; i >= 0 ; i--) {
            if (brackt_depth == 0 && is_left_bracket(i) && (close_col = find_close_bracket(i)) != 0) {
                printf(" %d %d", stack[i].vcol, close_col);
                break;
            }
            if (is_right_bracket(i))
                brackt_depth++;
            if (is_left_bracket(i))
                brackt_depth--;
        }

    /* find next bracket */
    for (int i = colp+1 ; i < sp ; i++) {
        if (is_left_bracket(i) && (close_col = find_close_bracket(i)) != 0) {
            printf(" %d %d", stack[i].vcol, close_col);
            break;
        }
    }

    return 0;
}
