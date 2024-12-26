" properties reading
fu! PropertiesOpen(file)
    let [bn, total_ln] = [bufnr(), line('$')]
    echom total_ln
    let [tempname, file] = [tempname(), trim(system('realpath '.a:file))]
    exe 'tabe '.tempname
    let new_bn = bufnr()
    set ft=jproperties
    for ln in range(1, total_ln)
        let raw = getbufline(bn, ln)[0]
        let raw = substitute(raw, '\\', '\\\\', 'g')
        let raw = substitute(raw, '(', '\\(', 'g')
        let raw = substitute(raw, ')', '\\)', 'g')
        let raw = substitute(raw, '<', '\\<', 'g')
        let raw = substitute(raw, '>', '\\>', 'g')
        let raw = substitute(raw, '#', '\\#', 'g')
        let raw = substitute(raw, ' ', '\\ ', 'g')
        let content = system('printf "%b" '.raw) " !!!
        cal setbufline(new_bn, ln, [content])
    endfor
    sil exe 'update'
endfu

com! -nargs=0 PropertiesReopen :cal PropertiesOpen(expand('%:p'))
