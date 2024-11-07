function print_rest(start_col) { # print_rest(2): print col 3, 4, 5...
    for (i = 1; i <= start_col; i++) { $i = "" }
    print substr($0, start_col+1)
}

function underscores_to_camelcase(content) {
    split(content, arr, "")
    rst = ""
    for (i = 0; i < length(arr); i++) {
        if (arr[i] == "_")
            rst = rst toupper(arr[++i])
        else
            rst = rst tolower(arr[i])
    }
    return rst
}

function camelcase_to_underscores(content) {
    split(content, arr, "")
    rst = tolower(arr[1])
    for (i = 2; i <= length(arr); i++) {
        if (arr[i] ~ /[A-Z]/)
            rst = rst "_" tolower(arr[i])
        else
            rst = rst arr[i]
    }
    return rst
}

function is_comment_line() {
    if ($0 ~ /^[ \t]*\/\//)
        return 1
    return 0
}

function capitalize(word) {
    first = toupper(substr(word, 1, 1))
    rest = substr(word, 2)
    first = first rest
    return first
}

function java_get(word) { _w = "get" toupper(substr(word, 1, 1)) substr(word, 2); return _w }
function java_set(word) { _w = "set" toupper(substr(word, 1, 1)) substr(word, 2); return _w }

function ltrim(s) { sub(/^[ \t\r\n]+/, "", s); return s }
function rtrim(s) { sub(/[ \t\r\n]+$/, "", s); return s }
function trim(s)  { return rtrim(ltrim(s)); }

BEGIN {
    # IGNORECASE = 1
    FS = "." # Field Separator
    # RS = "\n" # Record Separator
    # OFS = "\t" # Output Field Separator for `print`
    # ORS = "\n" # Output Record Separator for `print`
    output_flag = 0
    tmp = ""
    }

# main here
{
    if (ltrim($0) ~ /^let/) {
        print ltrim($0)
    }
}


END { }
