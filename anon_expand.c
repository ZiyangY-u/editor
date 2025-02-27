#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define w0 word[0]
#define w1 word[1]
#define w2 word[2]
#define w3 word[3]
#define w4 word[4]

/* exact match */
int ematch(char *pat, char *word) {
    if (strncmp(pat, word, strlen(pat)) == 0)
        return 1;
    return 0;
}

void vim_expand(char *word) {
    if (ematch("fu", word))
        printf("fu! %s()<cr>endf", word+2);
    else if (ematch("hl", word))
        printf("hi %s cterm=bold ctermfg=$1 ctermbg=$2", word+2);
}

void xml_expand(char *word) {
    if (ematch("s", word)) 
        printf("SELECT ");
    else if (ematch("d", word)) 
        printf("DISTINCT ");
    else if (ematch("f", word))
        printf("FROM ");
    else if (ematch("#", word))
        printf("#{$0}");
}

void c_expand(char* word) {
    if (ematch("cu", word))
        printf("const uint32_t ");
}

void sql_expand(char *word) {
    if (strlen(word) >= 2 && word[0] == 't' && isdigit(word[1])) {
        printf("TOP ");
        while (isdigit(*++word)) printf("%c", *word);
    }
    else if (ematch("inn", word))
        printf("IS NOT NULL");
}

void _java_variabe(char c) {
    switch (c) {
        case 's': printf("String"); break;
        case 'i': printf("int"); break;
        case 'I': printf("Integer"); break;
        case 'L': printf("Long"); break;
        case 'v': printf("void"); break;
        case 'b': printf("boolean"); break;
        case 'B': printf("BigDecimal"); break;
        default:
        break;
    }
}
void java_expand(char *word) {
    if (strlen(word) == 1) {
        _java_variabe(w0);
        return;
    }
    /* p[r]ivate/p[u]blic/pr[o]tected [s]tatic [f]inal type */
    if ((w0 == 'r' || w0 == 'u' || w0 == 'o') && strlen(word) >= 2) {
        switch (w0) {
            case 'r': printf("private"); break;
            case 'u': printf("public"); break;
            case 'o': printf("protected"); break;
            default: break;
        }
        printf(" ");
        _java_variabe(w1);
    }
}

void ark_expand(char *word) {
    if (isdigit(w0))
        printf("(%c strong)", w0);
    if (strcmp("w", word) == 0)
        printf("(weak)");
    if (strcmp("iw", word) == 0)
        printf("(insep weak)");
    if (strncmp("i", word, 1) == 0 && isdigit(w1))
        printf("(insep %c strong)", w1);
    if (strcmp("sw", word) == 0)
        printf("(seq weak)");
    if (strncmp("s", word, 1) == 0 && isdigit(w1))
        printf("(sep %c strong)", w1);
    if (w0 == 'C')
        printf("Cog. ");
    if (strcmp("ff", word) == 0)
        printf("(< $0)");
}

int _is_margin_padding(char *word) {
    if (w0 != 'm' && w0 != 'p')
        return 0;
    if (w1 != 't' && w1 != 'r' && w1 != 'l' && w1 != 'b')
        return 0;
    if (!isdigit(w2))
        return 0;
    return 1;
}
void _margin_padding(char *word) {
    if (w0 == 'm') printf("margin");
    if (w0 == 'p') printf("padding");
    if (w1 == 't') printf("Top");
    if (w1 == 'r') printf("Right");
    if (w1 == 'l') printf("Left");
    if (w1 == 'b') printf("Bottom");
    printf(": '");
    word+=1;
    while (isdigit(*++word)) 
        printf("%c", *word);
    printf("px'");

}
void css_expand(char *word) {
    if (_is_margin_padding(word))
        _margin_padding(word);
}

void git_expand(char *word) {
    if (strcmp("bl", word) ==0)
        printf("Backlog URL:");
}

void awk_printf(char* word) {
    int slen = strlen(word);
    printf("printf \"");
    for (int i = 1 ; i < slen ; i++) {
        switch (word[i]) {
            case 'd': printf("%%d"); break;
            case 's': printf("%%s"); break;
            case 'f': printf("%%f"); break;
            case 'n': printf("\\n"); break;
            case 't': printf("\\t"); break;
            case 'c': printf(","); break;
            default: break;
        }
    }
    if (word[slen-1] != 'x')
        printf("\", ");
    else
        printf("\"");
}

void awk_sprintf(char* word) {
    int slen = strlen(word);
    printf("s = sprintf(\"");
    for (int i = 2 ; i < slen ; i++) {
        switch (word[i]) {
            case 'd': printf("%%d"); break;
            case 's': printf("%%s"); break;
            case 'f': printf("%%f"); break;
            case 'n': printf("\\n"); break;
            case 't': printf("\\t"); break;
            case 'c': printf(","); break;
            default: break;
        }
    }
    printf("\", $0)");
}

void awk_sub(char* word) {
    int slen = strlen(word);
    char last_char = word[slen - 1];
    switch (last_char) {
        case 't': printf("gsub(\"\\t\", \"$0\")"); break;
        case 'c': printf("gsub(\",\", \"$0\")"); break;
        case 'q': printf("gsub(\"'\", \"$0\")"); break;
        case 'Q': printf("gsub(\"\\\"\", \"$0\")"); break;
    }
    printf(" print \\$0");
}

void awk_expand(char *word) {
    if (w0 == 'p' && isdigit(w1) && strlen(word) == 2) // p3 -> print $3
        printf("print \\$%d", w1 - '0');
    else if (strlen(word) == 1 && isdigit(w0)) // 3 -> $3
        printf("\\$%d", w0 - '0');
    else if (strlen(word) == 2 && isdigit(w0) && isdigit(w1)) // 12 -> $12
        printf("\\$%d%d", w0 - '0', w1 - '0');
    else if (w0 == 'p')
        awk_printf(word);
    else if (w0 == 's' && w1 == 'p')
        awk_sprintf(word);
    else if (strncmp("sub", word, 3) == 0)
        awk_sub(word);
}

/* argv[1]: word, argv[2]: filetype */
int main(int argc, char *argv[])
{
    if (argc < 3)
        return 0;
    if (strcmp("vim", argv[2]) == 0)
        vim_expand(argv[1]);
    if (strcmp("sql", argv[2]) == 0)
        sql_expand(argv[1]);
    if (strcmp("java", argv[2]) == 0)
        java_expand(argv[1]);
    if (strcmp("ark", argv[2]) == 0)
        ark_expand(argv[1]);
    if (strcmp("css", argv[2]) == 0)
        css_expand(argv[1]);
    if (strcmp("xml", argv[2]) == 0)
        xml_expand(argv[1]);
    if (strcmp("c", argv[2]) == 0)
        c_expand(argv[1]);
    if (strcmp("gitcommit", argv[2]) == 0)
        git_expand(argv[1]);
    if (strcmp("awk", argv[2]) == 0)
        awk_expand(argv[1]);

    return 0;
}
