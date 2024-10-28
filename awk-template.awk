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

BEGIN {
    # IGNORECASE = 1
    FS = "\t" # Field Separator
    # RS = "\n" # Record Separator
    OFS = "\t" # Output Field Separator for `print`
    # ORS = "\n" # Output Record Separator for `print`
    }

# main here
{
    # 1. just filter
    # if ($0 ~ /exec-10/) { print $0 }
    # if ($0 ~ /exec-3/ && $0 ~ /==/ && $0 !~/Parameters/) { print $0 }

    # 2. exclude
    # if ($0 !~ /Parameters/) { print $0 }
    if ($0 ~ /exec-5/) print $0

    # if ($0 !~ /Parameters/ && $0 ~ /^2024/) {
    #     sub(" ", "\t")
    #     sub(" ", "\t")
    #     sub(": ==>", "\t")
    #     sub(": <==", "\t")
    #     sub("Preparing:", "Preparing:\t")
    #     sub("Total:", "Total:\t")
    #     gsub(/ /, "", $4)
    #     print $2, $3, $4
    # }

    # 3. match and action
    # if ($0 ~ /pat/) {
    #     sub("info", "debug");
    #     print $0
    # } else print $0
}


END { }
