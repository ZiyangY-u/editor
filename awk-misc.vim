" awk misc

let [g:awk_file, g:awk_shadow, g:awk_func] = ['~/.config/nvim/awk-template.awk', 0, '~/.config/nvim/awk-lib/functions.awk']
ca aa %!awk -f <c-r>=g:awk_file<cr> FILE_NAME=<C-R>=expand('%:p')<CR>
ca ar AwkRange
ca an cal AwkToTemp(v:false)<cr>
ca anr cal AwkToTemp(v:true)<cr>
ca ae tabe \| e +/main/;norm\ ztjj <c-r>=g:awk_file<cr>       " edit awk-file
ca aef tabe \| e <c-r>=g:awk_func<cr>                         " edit awk function file
ca ase bo vsplit \| e +/main/;norm\ ztjj <c-r>=g:awk_file<cr> " split edit awk-file
ca asef bo vsplit \| e <c-r>=g:awk_func<cr>                   " split edit awk function file

fu! AwkToTemp(dyOpenFlg) " direct awk result to a new temporary file
    let [target_file, rstfile] = [expand('%:p'), tempname()]
    if IsDyBuf() | let target_file = b:dy_file | endif
    if a:dyOpenFlg
        echo 'awk processing...'
        cal system(printf('awk -i %s -f %s %s > %s', g:awk_func, g:awk_file, target_file, rstfile))
        cal DynamicOpen(rstfile)
    else
        cal execute(printf('tabe | e %s | r !awk -i %s -f %s %s', rstfile, g:awk_func, g:awk_file, target_file))
        exe "norm ggdd:w\n"
    endif
endf
fu! AwkRange(n)
    exec printf('.r !for run in {1..%d} ; do echo ; done', a:n)
    exec printf('norm %dk', a:n-1)
    sil exec printf('.,.+%d !awk -i %s -f %s FILE_NAME=%s', a:n-1, g:awk_func, g:awk_file, expand('%:p'))
endf
com! -nargs=1 AwkRange :cal AwkRange(<f-args>)
fu! AwkOp(type)
    let range = (a:type ==# 'line' ? "'[,']" : ".")
    exe printf("%s!awk -i %s -f %s FILE_NAME=%s", range, g:awk_func, g:awk_file, expand('%:p'))
    if g:autoIndentFlg == 1 | exe 'norm! `]j=`[' | en " auto indent after Op
endf
nn <silent> ,a :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)\|set opfunc=AwkOp<cr>g@
fu! OnlyOneFS()
    let [originLn, up, down] = [line('.'), line('.')-1, line('.')+1]
    while (trim(getline(up)) != '' && up > 0)
        sil exe up.'s/    FS/    # FS/e'
        let up = up-1
    endwhile
    while (trim(getline(down)) != '' && down < line('$'))
        sil exe down.'s/    FS/    # FS/e'
        let down = down+1
    endwhile
    exec ':'.originLn
endf

au User CommentaryPost if &ft == 'awk' | cal OnlyOneFS() | endif
