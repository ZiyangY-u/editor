BEGIN {
    # start_ln = 1
    # end_ln = 30
    # fmt = "%6d |"
}

{
    if (start_ln <= NR && NR <= end_ln) {
        printf fmt, NR
        print $0
    }
    if (NR >= end_ln)
        exit
}
