BEGIN {
    # IGNORECASE = 1

    # FS = "[()]" # xml/html
    # FS = "[\\[\\]]"
    # FS = "\t"
    # FS = ","
    # FS = "\\."
    # FS = ":"
    # FS = "/"
    # FS = "\""

    OFS="\t"
    # RS = "\n" # Record Separator

    "date +%Y%m%d" | getline current_date
    cnt = 0
}

# main here
{








}
