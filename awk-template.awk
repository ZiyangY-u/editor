@include "/root/.config/nvim/awk-lib/functions.awk"

BEGIN {
    # IGNORECASE = 1

    # FS = "[()]" # xml/html
    # FS = "[\\[\\]]"
    # FS = "\t"
    # FS = ","

    OFS="\t"
    # RS = "\n" # Record Separator

    "date +%Y%m%d" | getline current_date
}

# main here
{













}
