function print_rest(_start_col) { # print_rest(2): print col 3, 4, 5...
    for (_i = 1; _i <= _start_col; _i++) { $_i = "" }
    print substr($0, _start_col+1)
}

# print line except `col`
function print_except(_col) {
    for (_i = 1; _i <= NF; _i++)
        if (_i != _col) printf "%s%s", $_i, OFS
}

function underscores_to_camelcase(_content) {
    split(_content, _arr, "")
    _rst = ""
    for (_i = 0; _i < length(_arr); _i++) {
        if (_arr[_i] == "_")
            _rst = _rst toupper(_arr[++_i])
        else
            _rst = _rst tolower(_arr[_i])
    }
    return _rst
}

function camelcase_to_underscores(_content) {
    split(_content, _arr, "")
    _rst = tolower(_arr[1])
    for (_i = 2; _i <= length(_arr); _i++) {
        if (_arr[_i] ~ /[A-Z]/)
            _rst = _rst "_" tolower(_arr[_i])
        else
            _rst = _rst _arr[_i]
    }
    return _rst
}

function is_comment_line(fname) {
    if ($0 ~ /^[ \t]*\/\// && (fname ~ /\.java$/ || fname ~ /\.js/))
        return 1
    return 0
}

function is_number(_number) {
    if (_number +0 == _number)
        return 1
    return 0
}

function capitalize(_word) { _w = toupper(substr(_word, 1, 1)) substr(_word, 2); return _w }

function java_get(_word) { _w = "get" toupper(substr(_word, 1, 1)) substr(_word, 2); return _w }
function java_set(_word) { _w = "set" toupper(substr(_word, 1, 1)) substr(_word, 2); return _w }

function ltrim(_s) { sub(/^[ \t\r\n]+/, "", _s); return _s }
function rtrim(_s) { sub(/[ \t\r\n]+$/, "", _s); return _s }
function trim(_s)  { return rtrim(ltrim(_s)); }

# excel: get column name by column number
function xls_n2c(n) {
    _rst = ""
    n1 = n % 26
    _rst = _rst sprintf("%c", 64+(n1 == 0 ? 26 : n1))

    if (n > 26) {
        _n2 = (n - 26)
        n2 = int((n - 26) / 26) % 26
        c = 65+(_n2%26 == 0 ? n2-1 : n2)
        if (c == 64) c = 90

        _rst = _rst sprintf("%c", c)
    }

    if (n > 702) {
        _n3 = (n - 26) % (26 * 26)
        n3 = int((n-26)/ (26 * 26)) % 26
        c = 64 + (_n3 == 0 ? n3-1 : n3)
        _rst = _rst sprintf("%c", c)
    }
    rs = ""
    for (_i = length(_rst); _i > 0; _i--)
        rs = rs substr(_rst, _i, 1)

    return rs

}

# excel: get column number by column name
function xls_c2n(_name) {
    _convert="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if (length(_name) == 1)
        return index(_convert, substr(_name, 0, 1))
    else if (length(_name) == 2)
        return 26 + 26 * (index(_convert, substr(_name, 1, 1))-1) + \
        index(_convert, substr(_name, 2, 1))
    else if (length(_name) == 3)
        return 702 + 702 * (index(_convert, substr(_name, 1, 1))-1) + \
        26 * (index(_convert, substr(_name, 2, 1)) - 1) + \
        index(_convert, substr(_name, 3, 1))
}

# minimum split for new field separator
function msplit(content, fs, num) {
    split(content, arr, fs)
    for (_i = 0; _i <= length(arr); _i++) {
        if (_i == num) return arr[_i]
    }
}

BEGIN {
    IGNORECASE = 1

    # FS = "[()]" # xml/html
    # FS = "[{}]" # Field Separator
    # FS = "-" # Field Separator
    # FS = "\t" # Field Separator
    FS = "," # Field Separator
    # FS = "=" # Field Separator
    # FS = "Request-START" # Field Separator

    OFS=","
    # RS = "\n" # Record Separator

    "date +%Y%m%d" | getline current_date

    start = 114
    offset = xls_c2n("AH") - xls_c2n("B")
    p_flag = 0

}

# main here
{

    for (i = 1; i <= NF; i++) {
        if (i != 1) { printf "," }
        if (is_number($i)) {
            # n = $i / 2
            n = $i
            cmd = ("/mnt/c/Users/ziyan/desktop/sas/git/env/SAS_INTE_PJ-367-format.py -5 " n)
            cmd | getline out[i];
            printf "\"%s\"", out[i]
            close(cmd)
        }
        else printf "%s", $i
    }
    printf "\n"













}
