#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

#define w0 word[0]
#define w1 word[1]
#define w2 word[2]
#define w3 word[3]
#define w4 word[4]
#define w5 word[5]

#define match(l, r) (strcmp(l, r) == 0)
#define matchn(l, r, n) (strncmp(l, r, n) == 0)
#define todigit(x) (x - '0')

bool is_all_digit(char* word) {
    while (*word != '\0')
        if (!isdigit(*word++))
            return false;
    return true;
}

bool is_all_upper(char* word) {
    while (*word != '\0') {
        if (*word < 'A' || *word > 'Z')
            return false;
        word++;
    }
    return true;
}

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
    else if (w0 == 'a' && isdigit(w1))
        printf("argv[%c]", w1);
}

void sql_expand(char *word) {
    if (strlen(word) >= 2 && word[0] == 't' && is_all_digit(word+1))  // t3 -> TOP 3
        printf("TOP %d", atoi(word+1));
    else if (strlen(word) >= 2 && word[0] == 'l' && is_all_digit(word+1)) // l3 -> LIMIT 3
        printf("LIMIT %d", atoi(word+1));
    else if (matchn("ct", word, 2) && is_all_digit(word+2)) { // create table ...
        printf("create table $0 (au integer ");
        int n = atoi(word+2);
        for (int i = 0 ; i < n ; i++) printf(", c%d text", i+1);
        printf(");");
    } else if (match("s", word) || (matchn("s", word, 1) && is_all_digit(word+1))) { // select [top n] * from
        int tn = strlen(word) > 1 ? atoi(word+1) : 0;
        printf("SELECT ");
        if (tn > 0) printf("TOP %d ", tn);
        printf("* FROM ");
    }
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

void awk_decode_wildcard(char c) {
    switch (c) {
        case 'd': printf("%%d"); break;
        case 's': printf("%%s"); break;
        case 'f': printf("%%f"); break;
        case 'n': printf("\\n"); break;
        case 't': printf("\\t"); break;
        case 'q': printf("'"); break;
        case 'Q': printf("\\\""); break;
        case 'c': printf(","); break;
        default: break;
    }
}

void awk_printf(char* word) {
    int slen = strlen(word);
    printf("printf \"");
    for (int i = 1 ; i < slen ; i++) {
        awk_decode_wildcard(word[i]);
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
        awk_decode_wildcard(word[i]);
    }
    printf("\", $0)");
}

void awk_sub(char* word) {
    int slen = strlen(word);
    char last_char = word[slen - 1];
    printf("gsub(\"");
    awk_decode_wildcard(last_char);
    printf("\", \"$0\"); printf \"%%s\\n\", \\$0");
}

void awk_sql_insert(char* word) {
    int n = atoi(word + 1);
    printf("printf \"insert into $0 values (%%d");
    for (int i = 0 ; i < n ; i++) printf(", '%%s'");
    printf(");\\n\", NR");
    for (int i = 1 ; i <= n ; i++) printf(", \\$%d", i);
}

void awk_grep_print(char* word) {
    int len = 0;
    if (strlen(word) > 2) // has length suffix
        len = atoi(word+2);
    printf("printf \"%%s:%%d:%%s\\n\", FILENAME, FNR, ");
    if (len == 0)
        printf("\\$0");
    else printf("substr(\\$0, 1, %d)", len);
}

void awk_tmp_table(int n) {
    printf("if (NR != 1) printf \"union\"<cr>");
    printf("printf \" select ");
    for (int i = 1 ; i <= n ; i++) {
        if (i != 1) printf(", ");
        printf("'%%s' as 'col%d'", i);
    }
    printf("\\n\"");
    for (int i = 1 ; i <= n ; i++)
        printf(", \\$%d", i);

}


void awk_expand(char *word) {
    if (strlen(word) == 0)
        return;
    if (w0 == 'p' && isdigit(w1) && strlen(word) == 2) // p3 -> print $3
        printf("print \\$%d", todigit(w1));
    else if (strlen(word) == 1 && isdigit(w0)) // 3 -> $3
        printf("\\$%d", todigit(w0));
    else if (w0 == 'p') // printf
        awk_printf(word);
    else if (matchn(word, "sp", 2)) // sprintf
        awk_sprintf(word);
    else if (matchn("sub", word, 3) && strlen(word) > 3) // quick sub
        awk_sub(word);
    else if (strlen(word) >= 2 && w0 == 'i' && isdigit(w1)) // insert clause for embed sqlite
        awk_sql_insert(word);
    else if (is_all_digit(word)) // 123 -> $1, $2, $3
    {
        printf("\\$%d", todigit(w0));
        while (*(++word) != '\0') printf(", \\$%d", todigit(*word));
    }
    else if (matchn(word, "gp", 2))
        awk_grep_print(word);
    else if (isdigit(w0) && w1 == 'l') // 2l -> $2 ~ //
        printf("\\$%d ~ /$0/", todigit(w0));
    else if (isdigit(w0) && match(word+1, "nl")) // 2nl -> $2 ~! //
        printf("\\$%d !~ /$0/", todigit(w0));
    else if (w0 == 't' && isdigit(w1) && strlen(word) == 2) // t3 -> trim($3)
        printf("trim(\\$%d)", todigit(w1));
    else if (matchn(word, "tmpt", 4) && is_all_digit(word+4)) // template table
        awk_tmp_table(atoi(word+4));

    else if (is_all_upper(word)) // excel c2n, this should be last
        printf("xls_c2n(\"%s\")", word);
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
