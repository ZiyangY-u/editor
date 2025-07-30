" dynamic read
let g:dynamic_chunk_calc = '~/.config/nvim/dy-chunk-calc'
let g:dynamic_read = '~/.config/nvim/dy-read'
let g:dynamic_bufsize = 1000
let g:dy_line_chunk_size = 10000

fu! IsDyBuf()
    if exists('b:is_dy_buf') && b:is_dy_buf == 1
        retu v:true
    endif
    retu v:false
endf

fu! s:GetProgress(bn, jobId, data, event) abort
    let marks = getbufvar(a:bn, '_chunk_mark') . join(a:data, '|')
    cal setbufvar(a:bn, '_chunk_mark', marks)
    cal setbufvar(a:bn, 'chunk_mark', split(marks, '|'))
    redrawstatus
endf

fu! s:OnDyOpened(bn, jobId, data, event)
    cal setbufvar(a:bn, '_chunk_mark', '')
    redrawstatus
endf

fu! DynamicOpen(file)
    echom 'Openining...'
    let [tempname, file] = [tempname(), trim(system('realpath '.split(a:file, '|')[1]))]
    let bn = bufnr(tempname, 1)
    cal setbufvar(bn, 'dy_file', file)
    cal setbufvar(bn, 'is_dy_buf', 1)
    cal setbufvar(bn, 'dy_total_ln', split(system('wc -l '.file))[0])
    cal setbufvar(bn, 'chunk_mark', ['0'])
    cal setbufvar(bn, '_chunk_mark', '0|')
    cal setbufvar(bn, 'dy_marks', {})

    let job_opts = {'on_stdout' : function('s:GetProgress', [bn]), 'on_exit' : function('s:OnDyOpened', [bn])}
    cal jobstart(g:dynamic_chunk_calc.' '.file.' '.g:dy_line_chunk_size, job_opts)  " async
    " cal setbufvar(bn, 'chunk_mark', ['0'] + split(system(g:dynamic_chunk_calc.' '.file.' '.g:dy_line_chunk_size), '\n')) " sync

    exe 'tabe '.tempname
    cal DynamicLoad(1, g:dynamic_bufsize)
    sil exe ':1|norm zt'
    setl nonu
endf

com! -nargs=1 MDyOpen :cal DynamicOpen(<f-args>) " the first column is size
com! -nargs=0 DyOpen :cal HiraishinOpen('', 'MDyOpen', 1)
com! -nargs=1 DyLocate :cal DyRelocate(<f-args>)

fu! DyReadCmd(pos, start, end, file)
    let offset = b:chunk_mark[a:start/g:dy_line_chunk_size]
    let offset_ln = a:start - (a:start % g:dy_line_chunk_size)
    return a:pos.printf('r !%s %s %d %d %d %d', g:dynamic_read, a:file, offset, a:start, a:end, offset_ln)
endf

fu! DynamicLoad(start, end)
    let cmd = '%d|'.DyReadCmd('0', a:start, a:end, b:dy_file)
    exe cmd
    exe '$d|silent update'
    let [b:dy_topln, b:dy_endln] = [a:start, a:end]
endf

fu! DyRelocate(ln)
    let ln = (a:ln == 'end' ? b:dy_total_ln-g:dynamic_bufsize : str2nr(a:ln))
    if (ln/g:dy_line_chunk_size) >= len(b:chunk_mark)
        echoh Title | echo 'fail to move to uncalculated area' | echoh None | retu
    endif

    if a:ln == 'top' | cal DynamicLoad(1, g:dynamic_bufsize) | sil exe 'norm gg' | retu | endif
    if a:ln == 'end' | cal DynamicLoad(b:dy_total_ln-g:dynamic_bufsize, b:dy_total_ln) | sil exe 'norm G' | retu | endif
    let [ln, half_bs] = [str2nr(a:ln), g:dynamic_bufsize/2]
    if ln > b:dy_total_ln | echoerr 'Over total line' | retu | en
    let [start, end] = [(ln-half_bs >= 1 ? ln-half_bs : 1), (ln+half_bs <= b:dy_total_ln ? ln+half_bs : b:dy_total_ln)]
    cal DynamicLoad(start, end)
    sil exe printf(':%d|norm zz', ln-start+1)
endf

fu! DyExpandUp()
    let [b:line_num, b:winline, upper_ln] = [line('.'), winline(), str2nr(split(getline(1), '|')[0]) - 1]
    if upper_ln == 1 | retu | en
    let [start, end] = [(upper_ln-g:dynamic_bufsize >= 1 ? upper_ln-g:dynamic_bufsize : 1) ,upper_ln]
    let b:line_num += (end - start + 1)
    let cmd = DyReadCmd('0', start, end, b:dy_file)
    let b:dy_topln = start
    cal ExpandAndRecoverWinPos(cmd)
endf

fu! DyExpandDown()
    let [b:line_num, b:winline, lower_ln] = [line('.'), winline(), str2nr(split(getline('$'), '|')[0]) + 1]
    let [start, end] = [lower_ln, (lower_ln+g:dynamic_bufsize >= b:dy_total_ln ? b:dy_total_ln : lower_ln+g:dynamic_bufsize)]
    let cmd = DyReadCmd('$', start, end, b:dy_file)
    let b:dy_endln = end
    cal ExpandAndRecoverWinPos(cmd)
endf

fu! DyNext() " return next line number
    let current_ln = split(getline('.'), '|')[0]+0
    for b:dy_cursor in range(0, len(b:dy_search_rst)-1)
        if b:dy_search_rst[b:dy_cursor] > current_ln
            let current_ln = b:dy_search_rst[b:dy_cursor] | break
        endif
    endfor
    return current_ln
endf

fu! DyPrev() " return previouse line number
    let current_ln = split(getline('.'), '|')[0]+0
    for b:dy_cursor in reverse(range(0, len(b:dy_search_rst)-1))
        if b:dy_search_rst[b:dy_cursor] < current_ln
            let current_ln = b:dy_search_rst[b:dy_cursor] | break
        endif
    endfor
    return current_ln
endf

fu! DySearch(target)
    if exists('b:dy_target') | exe printf('syntax clear pat_%s', sha256(b:dy_target)) | endif
    cal AttachColor(a:target, 196, 0, 0)
    let [cmd, b:dy_target] = [printf('rg -n %s %s | cut -f1 -d:', a:target, b:dy_file), a:target]
    let b:dy_search_rst = split(system(cmd), '\n')
    let [b:dy_cursor, raw] = [0, getline('.')]
    let ln = str2nr(raw[:match(raw, '|')-1])
    while b:dy_cursor < len(b:dy_search_rst) && ln > b:dy_search_rst[b:dy_cursor] | let b:dy_cursor+=1 | endwhile
    cal DyRelocate(b:dy_search_rst[b:dy_cursor])
    nn <silent><buffer> n :cal DyRelocate(DyNext())<cr>
    nn <silent><buffer> N :cal DyRelocate(DyPrev())<cr>
endf

com! -nargs=1 DySearch :cal DySearch(<f-args>)
fu! ExpandAndRecoverWinPos(cmd)
    silent exe a:cmd | silent update
    sil exe ':'.b:line_num.'|norm zt'.(b:winline-2)."\<c-y>"
endf

au CursorHold * if exists('b:is_dy_buf') && b:is_dy_buf==1 && line('$')-line('.') < 20 && b:dy_endln < b:dy_total_ln | cal DyExpandDown() | en
au CursorHold * if exists('b:is_dy_buf') && b:is_dy_buf==1 && line('.') < 20 && b:dy_topln > 1 | cal DyExpandUp() | en

fu! DyStl()
    let stl="%#error#Dy-Reading:"
    if g:jumpMode == 'r' " roadmap
        let stl.="%#JumpModColor# R "
    endif
    let stl.="%<%#c1# %{b:dy_file}"
    let stl.="%=" " left/right separator
    if exists('b:is_dy_buf') && exists('b:chunk_mark') && exists('b:dy_total_ln') && b:_chunk_mark != ''
        let stl.= '%#error# ' . printf(' %.1f', 100.0 * len(b:chunk_mark) * g:dy_line_chunk_size / b:dy_total_ln) . "%{'% '}"
    endif
    let stl.="%#posBar# %{string(b:dy_endln*100.0/b:dy_total_ln).'%'} %{b:dy_total_ln} "
    if exists('b:dy_search_rst')
        let stl.="[%{b:dy_cursor+1}/%{len(b:dy_search_rst)}] "
    endif
    retu stl
endf

fu! DyMark(bn, ln, msg)
    let marks = getbufvar(a:bn, 'dy_marks')
    let marks[a:ln] = a:msg
    cal setbufvar(a:bn, 'dy_marks', marks)
endf

com! -nargs=1 DyMark :cal DyMark(bufnr(), CurrentLn(), <f-args>)
