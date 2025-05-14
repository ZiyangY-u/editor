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

# decimal to binary string
function d2b(num) {
    _hex = sprintf("%x", num)
    cmd = sprintf("echo \"obase=2;%d\" | bc", num)
    cmd | getline _bin
    close(cmd)
    return _bin
}

function rep(s, n) {
    _r = ""
    while (n-- > 0) _r = _r s;
    return _r;
}

function progress_bar(_total_line, bar_len, extra_info) {
    if (NR % 1000 == 0) {
        done = int((NR / _total_line) * bar_len)
        undone = bar_len - 1 - done
        printf "Progress: %.3f% [%s>%s] %s \r", (NR * 100 / _total_line), rep("=", done), rep(" ", undone), extra_info
    }
}

# compare time xx:xx:xx.xxx
function calc_elapse(t1, t2) {
    split(t1, _t1_arr, ":")
    _t1 = _t1_arr[1] * 3600 + _t1_arr[2] * 60 + _t1_arr[3]
    split(t2, _t2_arr, ":")
    _t2 = _t2_arr[1] * 3600 + _t2_arr[2] * 60 + _t2_arr[3]
    return _t2 - _t1
}

BEGIN {
    # IGNORECASE = 1

    # FS = "[()]" # xml/html
    # FS = "[\\[\\]]"
    # FS = "-"
    # FS = "\t"
    # FS = ","
    # FS = ":"
    # FS = "\\/\\/"

    OFS="\t"
    # RS = "\n" # Record Separator

    "date +%Y%m%d" | getline current_date
}

# main here
{













}
