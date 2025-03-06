#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define w0 word[0]
#define w1 word[1]
#define w2 word[2]
#define w3 word[3]
#define w4 word[4]

#define match(l, r) (strcmp(l, r) == 0)
#define matchn(l, r, n) (strncmp(l, r, n) == 0)

void vim_expand(char *word) {
    if (match("fu", word))
        printf("fu! %s()<cr>endf", word+2);
    else if (match("hl", word))
        printf("hi %s cterm=bold ctermfg=$1 ctermbg=$2", word+2);
}

void xml_expand(char *word) {
    if (match("s", word)) 
        printf("SELECT ");
    else if (match("d", word)) 
        printf("DISTINCT ");
    else if (match("f", word))
        printf("FROM ");
    else if (match("#", word))
        printf("#{$0}");
}

void c_expand(char* word) {
    if (match("cu", word))
        printf("const uint32_t ");
}

void sql_expand(char *word) {
    if (strlen(word) >= 2 && word[0] == 't' && isdigit(word[1])) {
        printf("TOP ");
        while (isdigit(*++word)) printf("%c", *word);
    }
    else if (match("inn", word))
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
    if (match("w", word))
        printf("(weak)");
    if (match("iw", word))
        printf("(insep weak)");
    if (strncmp("i", word, 1) && isdigit(w1))
        printf("(insep %c strong)", w1);
    if (match("sw", word))
        printf("(seq weak)");
    if (strncmp("s", word, 1) && isdigit(w1))
        printf("(sep %c strong)", w1);
    if (w0 == 'C')
        printf("Cog. ");
    if (match("ff", word))
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
    if (match("bl", word))
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
        case 's': printf("gsub(\" \", \"$0\")"); break;
        case 'q': printf("gsub(\"'\", \"$0\")"); break;
        case 'Q': printf("gsub(\"\\\"\", \"$0\")"); break;
    }
    printf("; print \\$0");
}

void awk_sql_insert(char* word) {
    int n = atoi(word + 1);
    printf("printf \"insert into $0 values (%%s");
    for (int i = 1 ; i < n ; i++) printf(", %%s");
    printf(");\\n\"");
    for (int i = 0 ; i < n ; i++) printf(", \\$%d", i);
}

void awk_expand(char *word) {
    if (w0 == 'p' && isdigit(w1) && strlen(word) == 2) // p3 -> print $3
        printf("print \\$%d", w1 - '0');
    else if (strlen(word) == 1 && isdigit(w0)) // 3 -> $3
        printf("\\$%d", w0 - '0');
    else if (strlen(word) == 2 && isdigit(w0) && isdigit(w1)) // 12 -> $12
        printf("\\$%d%d", w0 - '0', w1 - '0');
    else if (w0 == 'p') // printf
        awk_printf(word);
    else if (matchn(word, "sp", 2)) // sprintf
        awk_sprintf(word);
    else if (matchn("sub", word, 3)) // quick sub
        awk_sub(word);
    else if (strlen(word) >= 2 && w0 == 'i' && isdigit(w1)) // insert clause for embed sqlite
        awk_sql_insert(word);
}

/* argv[1]: word, argv[2]: filetype */
int main(int argc, char *argv[])
{
    if (argc < 3)
        return 0;
    if (match("vim", argv[2]))
        vim_expand(argv[1]);
    if (match("sql", argv[2]))
        sql_expand(argv[1]);
    if (match("java", argv[2]))
        java_expand(argv[1]);
    if (match("ark", argv[2]))
        ark_expand(argv[1]);
    if (match("css", argv[2]))
        css_expand(argv[1]);
    if (match("xml", argv[2]))
        xml_expand(argv[1]);
    if (match("c", argv[2]))
        c_expand(argv[1]);
    if (match("gitcommit", argv[2]))
        git_expand(argv[1]);
    if (match("awk", argv[2]))
        awk_expand(argv[1]);

    return 0;
}
