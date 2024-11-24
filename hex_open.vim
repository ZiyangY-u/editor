" xxd reading
fu! HexOpen(file)
    echom 'Openining...'
    let [tempname, file] = [tempname(), trim(system('realpath '.a:file))]
    exe 'tabe '.tempname
    exe 'r !xxd '.a:file
    sil exe ':1|norm ddzt'
    sil exe 'update'
    set ft=xxd
    au CursorMoved <buffer> cal HlChar()
    setl nonu
endfu
com! -nargs=1 MHexOpen :cal HexOpen(<f-args>)
com! -nargs=0 HexOpen :cal HiraishinOpen('', 'MHexOpen', 0)
let g:hexHighlight = nvim_create_namespace('hexHighlight')
hi HexHl cterm=underline ctermfg=red

fu! ClearHexHl()
    for ns_id in [g:hexHighlight]
        for mkInfo in nvim_buf_get_extmarks(0, ns_id, 0, -1, {})
            cal nvim_buf_del_extmark(0, ns_id, mkInfo[0])
        endfor
    endfor
endf

fu! HlChar()
    cal ClearHexHl()
    let col_map = {2:1,3:1,4:2,5:2,7:3,8:3,9:4,10:4,12:5,13:5,14:6,15:6,17:7,18:7,19:8,20:8,22:9,23:9,24:10,25:10,27:11,28:11,29:12,30:12,32:13,33:13,34:14,35:14,37:15,38:15,39:16,40:16}
    let line = getline('.')
    let col = col('.') - 9 " hex offset
    " in hex range
    if col > 0 && (col-1) % 5 != 0 && col <= 40
        let hlcol = col_map[col] + 51
        cal nvim_buf_set_extmark(bufnr(''), g:hexHighlight, line('.')-1, 0, {
                    \ "virt_text":[[line[hlcol-1], 'HexHl']],
                    \ "virt_text_win_col": hlcol-1, })
    endif
    " in ascii range
    if 43 <= col && col <= 58
        let reverse_map = {1:2,2:4,3:7,4:9,5:12,6:14,7:17,8:19,9:22,10:24,11:27,12:29,13:32,14:34,15:37,16:39}
        let hlcol = reverse_map[col - 42]
        let txt = line[hlcol+8:hlcol+9]
        cal nvim_buf_set_extmark(bufnr(''), g:hexHighlight, line('.')-1, 0, {
                    \ "virt_text":[[txt, 'HexHl']],
                    \ "virt_text_win_col": hlcol+8, })
    endif
endf
