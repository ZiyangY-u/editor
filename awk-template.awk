function print_rest(start_col) { # print_rest(2): print col 3, 4, 5...
    for (_i = 1; _i <= start_col; _i++) { $_i = "" }
    print substr($0, start_col+1)
}

# print line except `col`
function print_except(col) {
    for (_i = 1; _i <= NF; _i++)
        if (_i != col) printf "%s%s", $_i, OFS
}

function underscores_to_camelcase(content) {
    split(content, arr, "")
    rst = ""
    for (_i = 0; _i < length(arr); _i++) {
        if (arr[_i] == "_")
            rst = rst toupper(arr[++_i])
        else
            rst = rst tolower(arr[_i])
    }
    return rst
}

function camelcase_to_underscores(content) {
    split(content, arr, "")
    rst = tolower(arr[1])
    for (_i = 2; _i <= length(arr); _i++) {
        if (arr[_i] ~ /[A-Z]/)
            rst = rst "_" tolower(arr[_i])
        else
            rst = rst arr[_i]
    }
    return rst
}

function is_comment_line(fname) {
    if ($0 ~ /^[ \t]*\/\// && (fname ~ /\.java$/ || fname ~ /\.js/))
        return 1
    return 0
}

function capitalize(word) { _w = toupper(substr(word, 1, 1)) substr(word, 2); return _w }

function java_get(word) { _w = "get" toupper(substr(word, 1, 1)) substr(word, 2); return _w }
function java_set(word) { _w = "set" toupper(substr(word, 1, 1)) substr(word, 2); return _w }

function ltrim(s) { sub(/^[ \t\r\n]+/, "", s); return s }
function rtrim(s) { sub(/[ \t\r\n]+$/, "", s); return s }
function trim(s)  { return rtrim(ltrim(s)); }

function get_excel_col_name(n) {
    rst = ""
    n1 = n % 26
    rst = rst sprintf("%c", 64+(n1 == 0 ? 26 : n1))

    if (n > 26) {
        _n2 = (n - 26)
        n2 = int((n - 26) / 26) % 26
        c = 65+(_n2%26 == 0 ? n2-1 : n2)
        if (c == 64) c = 90

        rst = rst sprintf("%c", c)
    }

    if (n > 702) {
        _n3 = (n - 26) % (26 * 26)
        n3 = int((n-26)/ (26 * 26)) % 26
        c = 64 + (_n3 == 0 ? n3-1 : n3)
        rst = rst sprintf("%c", c)
    }
    rs = ""
    for (_i = length(rst); _i > 0; _i--)
        rs = rs substr(rst, _i, 1)

    return rs

}

# minimum split for new field separator
function msplit(content, fs, num) {
    split(content, arr, fs)
    for (_i = 0; _i <= length(arr); _i++) {
        if (_i == num) return arr[_i]
    }
}

BEGIN {
    # IGNORECASE = 1
    # FS = "[<>]" # xml/html
    # FS = "[{}]" # Field Separator
    FS = "\t" # Field Separator
    # RS = "\n" # Record Separator
    # OFS="\t"

    tbl = ""
    }

# main here
{
    gsub("C285533200", "C271337800", $0)
    print $0
}


END {
    # printf ")"
    }
