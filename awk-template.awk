BEGIN {
    # IGNORECASE = 1
    FS = "\t" # Field Separator
    # RS = "\n" # Record Separator
    # OFS = ";" # Output Field Separator for `print`
    # ORS = "\n" # Output Record Separator for `print`
}

function print_rest(start_col) { # print_rest(2): print col 3, 4, 5...
    for (i = 1; i <= start_col; i++) { $i = "" }
    print substr($0, start_col+1)
}

{
    print_rest(2)
    }

END {
}
