BEGIN {
    # IGNORECASE = 1
    # FS = "\t" # Field Separator
    # RS = "\n" # Record Separator
    # OFS = ";" # Output Field Separator for `print`
    # ORS = "\n" # Output Record Separator for `print`
}

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

# main here
{
    # if ($0 ~ /private/)
    #     print "model.get" toupper(substr($2, 1, 1)) substr($2, 2)
    if (!is_comment_line())
        print $0
    # else print $0
}


END { }
