function print_rest(start_col) { # print_rest(2): print col 3, 4, 5...
    for (i = 1; i <= start_col; i++) { $i = "" }
    print substr($0, start_col+1)
}

# print line except `col`
function print_except(col) {
    for (i = 1; i <= NF; i++) 
        if (i != col) printf "%s%s", $i, OFS
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

BEGIN {
    IGNORECASE = 1
    # FS = "//" # Field Separator
    # RS = "\n" # Record Separator
    # OFS = "\t" # Output Field Separator for `print`
    # ORS = "\n" # Output Record Separator for `print`
    output_flag = 0
    tmp = ""

    calens_o = "\tカレンダー"         "\tー"   "\tYYYY/MM"
    calenl_o = "\tカレンダー"         "\tー"   "\tYYYY/MM/DD"
    pop_o    = "\tポップアップ"       "\t可"   "\tイベント・処理詳細参照"
    text_o   = "\tテキストボックス"   "\t可"   "\tー"
    num_o    = "\tテキストボックス"   "\tー"   "\tー"
    drops_o  = "\tドロップダウン"     "\tー"   "\tー"
    dropm_o  = "\tドロップダウン"     "\t可"   "\tー"
    check_o  = "\tチェックボックス"   "\tー"   "\tー"
    link_o   = "\tリンク"             "\tー"   "\tー"

    # printf "AND ("
    }

# main here
{

    # gsub(" calens", calens_o, $0)
    # gsub(" calenl", calenl_o, $0)
    # gsub(" pop", pop_o, $0)
    # gsub(" text", text_o, $0)
    # gsub(" num", num_o, $0)
    # gsub(" drops", drops_o, $0)
    # gsub(" dropm", dropm_o, $0)
    # gsub(" check", check_o, $0)
    # gsub(" link", link_o, $0)
    # print NR, $0

    # printf "%d\t%s", NR, $1
    # if ($2 ~ /btn/) { printf "\tボタン\n" }
    # if ($2 ~ /check/) { printf "\tチェックボックス\n" }
    # if ($2 ~ /lbl/) { printf "\tラベル\n" }
    # if ($2 ~ /lnk/) { printf "\tラベル/リンク\n" }


    # printf "◆%d.\n", NR
    # printf "%s\n", $2

    # if (NR > 1)
    #     printf "OR %s LIKE '%入力したメニュー%'\n", $0
    # else
    #     printf "%s LIKE '%入力したメニュー%'\n", $0

    # if (NR > 1)
    #     printf "AND %s NOT LIKE '%入力したメニュー%'\n", $0
    # else
    #     printf "%s NOT LIKE '%入力したメニュー%'\n", $0

    # gsub("入力したサイト", "入力したメニュー", $0)
    # print $0

    # printf "%d\t%s\t%s\n", NR, $2, $3

    # printf "%sが入力されているかつ限定される場合\n", $0
}


END {
    # printf ")"
    }
