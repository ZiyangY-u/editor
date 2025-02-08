" batch rename files
fu! RenameFiles(path)
    let [tempname, idx] = [tempname(), 1]
    exe 'tabe '.tempname
    for f in split(trim(system(printf("ls %s", a:path))))
        cal append(0, printf('mv %s %s;', f, f))
    endfor
    sil exe ':1|lcd ' . a:path
    bo vsplit
    exe printf('e +98;norm\ zt %s', g:awk_file)

endf
com! -nargs=0 RenamePwd :cal RenameFiles(trim(system('pwd')))
com! -nargs=0 RenameCurrent :cal RenameFiles(expand('%:p:h'))
