BEGIN {
    # CONVFMT = %.6g # conversion format for numbers
    # FS = "|" # Field Separator
    maxemp="Jerry"
    maxrate=0
    names=""
}

{
    print ;
    names = names $1 " "
}
$2 > maxrate { maxrate = $2 ; maxemp = $1 }

END {
    printf "highest hourly rate: %f, for %s\n", maxrate, maxemp
    print names
}
