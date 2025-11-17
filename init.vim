" clear all autocommands first
autocmd!
colorscheme vim
" => Environment -------------------- {{{
set enc=utf-8
set fencs=ucs-bom,utf-8,sjis,latin-1,defalut
filetype on                     " let vim detect file type
filetype plugin indent on       " let vim use different indent for different file type
syntax enable                   " Enable syntax Highlighting
set bs=indent,eol,start
set nobk swf
set udf             " save undo history
set history=300
set hidden          " enable to change buffer without save changes
set shada=<800,:700,'100,@1000,/700,h,n~/nvim/shada
set updatetime=77
set mmp=10000
set undolevels=50
set notermguicolors

" Indention
set ai et sta ts=4  " autoindent expandtab smarttab tabstop
ca utab setl noet nosta ts=4
set sr sw=4         " shiftround shiftwidth
" Selection
set virtualedit=all " Very useful!!
" }}}
" => Appearance -------------------- {{{
set nu rnu             " show line number
set cul cuc            " highlight cursor line and column
set lbr nowrap         " stop breaking word when wrap long line
set sc sm nosmd        " showcmd showmatch noshowmode
set conceallevel=0     " do not hide anything
set switchbuf+=usetab,newtab
set title titlestring=%<%F titlelen=0
set ph=10 pw=20

" Statusline
hi mod cterm=bold ctermfg=Black ctermbg=DarkRed
hi totalL cterm=bold ctermfg=White ctermbg=Blue
hi fileType cterm=bold ctermfg=Red ctermbg=Blue
hi posBar ctermfg=Black ctermbg=Blue
hi c1 ctermfg=Black ctermbg=DarkCyan
hi ModColor cterm=bold ctermfg=white ctermbg=68
hi sleepWindow ctermbg=DarkGray
hi texPage ctermbg=128
hi awkShadow ctermbg=235 ctermfg=252
hi awkFS cterm=bold ctermfg=196 ctermbg=DarkCyan

let g:asyncCnt = 0
fu! ActStl(isActive)
    if &ft == 'qf' && a:isActive == 1 | retu " QuickFix List %l/%L %P" | en
    if a:isActive == 0
        retu "%#error#%r%#mod#%m%#sleepWindow# %t %y %= ln:%l/%L %P "
    en
    if IsDyBuf() && exists('*DyStl') | retu DyStl() | en
    let stl=""
    let stl.="%#error#%r%#mod#%m"
    let stl.= (g:jumpMode == 'n' ? "%#ModColor#" : "%#JumpModColor#")
    let stl.="%{(mode()=='n'||mode()=='c')?'  '.g:jumpModeNames[g:jumpMode].' ':''}%{(mode()=='t')?'  TERM ':''}"
    if g:awk_shadow | let stl.='%#awkShadow# 󰆏 ' | en
    let stl.="%<%#c1# %w%{filereadable(expand('%p')) ? Longf(expand('%:p')) : expand('%:p')}"
    if &ft ==# 'awk'
        let fs = trim(system(printf("rg '^\\s*\\bFS' %s | tail -n 1 | awk '{$1=$1};1'", expand('%:p'))))
        let stl.=(" %#awkFS#" . fs)
    endif

    let stl.="%=" " left/right separator
    " virtual column number and byte index number
    if &ft == 'tex' | let stl.='%#texPage# 󰗚 [%{GetPdfLoc()}]' | en " tex Pdf page number
    let stl.="%#posBar#%  %v[%c] %P %#totalL#%L% "
    let stl.=" %#fileType#% %y %{strlen(&fenc)?&fenc:'none'}/%{strlen(&ff)?&ff:''} "
    retu stl
endf

set stl=%!ActStl(1)
au WinNew,WinEnter,BufWinEnter * setl stl=%!ActStl(1) cul
au WinNew,WinEnter,BufWinEnter * if &ft !=# 'nerdtree' | setl cuc | en
au WinLeave * setl stl=%!ActStl(0) nocuc
au WinLeave * if !nvim_get_option_value('diff', {'scope':'local'}) | setl nocul | en

" Non-text display
set lcs=eol:$,tab:<->,lead:∙,space:•,trail:●,nbsp:█
hi nontext ctermfg=244

" High-light colors
"   see more high-light groups using :h highlight-groups
hi Search cterm=underline ctermfg=red ctermbg=none
hi IncSearch cterm=bold ctermfg=black ctermbg=white
hi Folded ctermfg=lightblue ctermbg=236
hi Visual ctermfg=black ctermbg=lightblue
hi VertSplit cterm=bold ctermfg=white ctermbg=none
hi Pmenu ctermfg=white ctermbg=239
hi CursorLine cterm=none ctermbg=DarkGray
hi LineNrAbove ctermfg=blue
hi CursorLineNr cterm=bold ctermfg=white
au InsertLeave * hi CursorLine cterm=NONE ctermbg=DarkGray | setl cuc
au InsertEnter * cal HlInsertRow() | setl nocuc
fu! HlInsertRow()
    hi CursorLine cterm=bold ctermbg=52
    if UltiSnips#CanJumpForwards() || UltiSnips#CanJumpBackwards() | hi CursorLine ctermbg=22
    elseif v:insertmode == 'r' | hi CursorLine ctermbg=54
    elseif g:jpIme | hi CursorLine ctermbg=18
    elseif g:cnIme | hi CursorLine ctermbg=16
    en
endf

" Sign
let g:alphabet = map(range(char2nr('a'),char2nr('z')),'nr2char(v:val)')
let g:ALPHABET = map(range(char2nr('A'),char2nr('Z')),'nr2char(v:val)')
hi MarkSign cterm=none ctermfg=196 ctermbg=DarkGray
hi MarkSignGlobal cterm=none ctermfg=92 ctermbg=DarkGray
hi QfMarkHl cterm=bold ctermfg=227 ctermbg=DarkGray
fu! SignMarks()
    cal sign_unplace('marks', {'buffer':bufnr()})
    for mk in extend(getmarklist(), getmarklist(bufnr()))
        let [mn, pos] = [mk['mark'][1], mk['pos']] " mn for Mark Name
        if mn =~ '\C[a-z]'
            cal sign_define('mark'.mn,{'text':'󰉁'.mn,'texthl':'MarkSign'})
            cal sign_place(char2nr(mn), 'marks', 'mark'.mn, bufnr(), {'lnum':pos[1],'priority':70})
        elseif mn =~ '\C[A-Z]'
            if bufnr() == bufnr(mk['file'])
                cal sign_define('gmark'.mn,{'text':''.mn,'texthl':'MarkSignGlobal'})
                cal sign_place(char2nr(mn), 'marks', 'gmark'.mn, bufnr(), {'lnum':pos[1],'priority':70})
            en
        en
    endfor
    let qfIdx = 1
    for qfItem in getqflist()
        if qfItem['bufnr'] == bufnr()
            let mkName = 'qfmark'.qfIdx
            cal sign_define(mkName,{'text':'󰙒 ','texthl':'QfMarkHl'})
            cal sign_place((qfIdx+1000), 'marks', mkName, bufnr(), {'lnum':qfItem['lnum'],'priority':60})
        en
        let qfIdx += 1
    endfor
endf
com! -nargs=* DMarks :sil exe len(<q-args>)==0?'delm a-z':':delm '.expand(<f-args>)|cal SignMarks()
au WinEnter,BufReadPost <buffer> cal SignMarks()
hi Conceal ctermbg=none ctermfg=46
fu! HideText(pattern, border)
    let pat = a:border ? '/\<'.a:pattern.'\>/' : '/'.a:pattern.'/'
    exe printf('syntax match pat_%s %s conceal cchar= %s', sha256(a:pattern), pat, (&ft==''?'':' containedin=ALL'))
    setl conceallevel=1
endf
com! -bang -range -nargs=0 HideText :cal HideText(Selected(), <bang>0)
com! -range -nargs=0 DHideText :exe printf('syntax clear pat_%s', sha256(Selected()))

" Colorful (ExtMark, AttachColor)
let g:extmk = nvim_create_namespace('MyExtMarks')
fu SetExMark(bn, ln, hl, ...)
    let txt = ' '.join(a:000, ' ')
    let extmk_id = nvim_buf_set_extmark(a:bn, g:extmk, a:ln, 0, { "virt_text":[[txt, a:hl]], "hl_mode":"combine" })
endf
fu DelLineExtMark(namespace, start, end)
    for mkInfo in nvim_buf_get_extmarks(bufnr(''), a:namespace, a:start, a:end, {})
        cal nvim_buf_del_extmark(bufnr(''), a:namespace, mkInfo[0])
    endfor
endf

let g:ColorAttachs='{}' " key: sha256(ft.pat.border); val: [pat, color, border]
fu AttachColor(pattern, color, border, saveFlag)
    let pat = a:border ? '/\<'.a:pattern.'\>/' : '/'.a:pattern.'/'
    exe printf('syntax match pat_%s %s%s', sha256(a:pattern), pat, (&ft==''?'':' containedin=ALL'))
    exe printf('hi pat_%s ctermfg=%d', sha256(a:pattern), a:color)
    if a:saveFlag " update global
        exe 'let _ca = ' . g:ColorAttachs
        let _ca[sha256(&ft.a:pattern.a:border)] = [a:pattern, a:color, a:border]
        let g:ColorAttachs = string(_ca)
    en
endf
fu! AttachTerm(pattern, border, term)
    let pat = a:border ? '/\<'.a:pattern.'\>/' : '/'.a:pattern.'/'
    exe printf('syntax match pat_%s %s%s', sha256(a:pattern), pat, (&ft==''?'':' containedin=ALL'))
    exe printf('hi pat_%s cterm=%s', sha256(a:pattern), a:term)
endf
fu RecoverGAttach()
    exe 'let _ca = ' . g:ColorAttachs
    for [sha, pcb] in items(_ca)
        let [pat, col, border] = pcb
        if sha256(&ft.pat.border) == sha | cal AttachColor(pat, col, border, 0) | en
    endfor
endf
fu GDelAttach(pattern)
    exe 'let _ca = ' . g:ColorAttachs
    if has_key(_ca, sha256(&ft.a:pattern.'0')) | unlet _ca[sha256(&ft.a:pattern.'0')] | en
    if has_key(_ca, sha256(&ft.a:pattern.'0')) | unlet _ca[sha256(&ft.a:pattern.'1')] | en
    let g:ColorAttachs = string(_ca) " save to global
    exe printf('syntax clear pat_%s', sha256(a:pattern))
endf
let g:BufColors={}
au SessionLoadPost,BufWinEnter * cal RecoverGAttach()
let MColors = {'': 196, 'red':196, 'green':118, 'blue':33, 'yellow':220, 'purple':135, 'white':255, 'aqua':45, 'orange':202}
for color in keys(MColors)
    exe printf('hi MVText%s cterm=bold ctermfg=%d', color, MColors[color])
    exe printf('com! -nargs=* SEMark%s :cal SetExMark(bufnr(""), line(".")-1, "MVText%s", <f-args>)', color, color)
    exe printf('com! -bang -range -nargs=0 Attach%s :cal AttachColor(Selected(), %d, <bang>0, 0)', color, MColors[color])
    exe printf('com! -bang -range -nargs=0 GAttach%s : cal AttachColor(Selected(), %d, <bang>0, 1)', color, MColors[color])
    exe printf('com! -nargs=0 BAttach%s :let g:BufColors[bufnr()]=%d', color, MColors[color])
endfor
com! -bang -range -nargs=0 AttachUnderline :cal AttachTerm(Selected(), <bang>0, 'underline')
com! -bang -range -nargs=0 AttachBold :cal AttachTerm(Selected(), <bang>0, 'bold')
com! -nargs=0 DEMarks :cal DelLineExtMark(g:extmk, [line('.')-1,0], [line('.')-1,0])
com! -range -nargs=0 DAttach :exe printf('syntax clear pat_%s', sha256(Selected()))
com! -range -nargs=0 GDAttach :cal GDelAttach(Selected())
com! -nargs=0 DBAttach :unlet g:BufColors[bufnr()]

" Vertical Quick Scope
let g:vertLineMark = nvim_create_namespace('vertLineMark')
const [g:DOWN, g:UP] = [0, 1]
fu! PumRenderVerticalScope(col)
    cal ClearVirtualTxt()
    let ppos = pum_getpos()
    if !has_key(ppos, 'height') | retu | en " exit when pum not showing
    let direct = (has_key(ppos, 'row') && ppos['row'] == (winline()+1)) ? g:DOWN : g:UP
    let [pumHeight, selected] = [float2nr(pum_getpos()['height']), complete_info(['selected'])['selected']]
    for i in range(1, (pumHeight <= 10 ? pumHeight : 10))
        let [txt, hl] = [string(abs(i-(selected%10)-1)%10), 'QuickScopePrimary']
        if direct == g:UP | cal VirtualMarkWrapper(line('.')-pumHeight+i-2, a:col, txt, hl) | en
        if direct == g:DOWN | cal VirtualMarkWrapper(line('.')+i-1, a:col, txt, hl) | en
    endfor
endf
fu! RenderVerticalScope(start, dense, end, col)
    cal ClearVirtualTxt()
    let [offset, upcnt, downcnt] = [a:start, 1, 1]
    while offset <= (a:end == -1 ? max([line('.') - line('w0'), line('w$') - line('w0')]) : a:end)
        let [upln, downln] = [line('.')-offset, line('.')+offset]
        cal VirtualMarkWrapper(upln-1, a:col, string(upcnt), 'QuickScopePrimary')
        cal VirtualMarkWrapper(downln-1, a:col, string(downcnt), 'QuickScopePrimary')
        if foldclosed(upln) == -1 || foldclosed(upln) == upln | let upcnt += 1 | en
        if foldclosed(downln) == -1 || foldclosed(downln) == downln | let downcnt += 1 | en
        let offset += a:dense
    endwhile
endf
fu! ClearVirtualTxt()
    for ns_id in [g:vertLineMark]
        for mkInfo in nvim_buf_get_extmarks(0, ns_id, 0, -1, {})
            cal nvim_buf_del_extmark(0, ns_id, mkInfo[0])
        endfor
    endfor
endf
au OptionSet * if (!empty(matchstr(v:option_new, 'Op$')))
            \| cal nvim_buf_set_extmark(bufnr(), g:vertLineMark, line(".")-1, 0, { "virt_text":[[v:option_new, 'SnipAnon']], "hl_mode":"combine" }) | en
fu! IsBlankLine()
    let ln = getline(line('.'))
    retu len(substitute(ln, '\s', '', 'g')) == 0
endf
nn <silent> d :let b:reg_name = IsBlankLine() ? '_' : v:register<cr>:cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>@=('"'.b:reg_name.'d')<cr>
nn <silent> y :let b:rn = v:register<cr>:cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>@=('"'.b:rn.'y')<cr>
nn <silent> c :let b:reg_name = IsBlankLine() ? '_' : v:register<cr>:cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>@=('"'.b:reg_name.'c')<cr>
nn = :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>=
nn zf :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>zf
nn V :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>V
nn <c-v> :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr><c-v>
au CursorMoved * if index(['V','v',"\<C-V>"], mode())>=0|sil cal RenderVerticalScope(1,1,-1,virtcol('.')-1)|en
au CursorMoved,TextChanged,InsertEnter,TextYankPost * if index(['V','v',"\<C-V>"], mode())<0|sil cal ClearVirtualTxt()|en

" Roadmap
au ExitPre * if exists('g:roadmapbuf') | exe 'bd!'.g:roadmapbuf | en
au CursorHold * if exists('g:roadmapbuf') && index(tabpagebuflist(), g:roadmapbuf) >= 0 | cal timer_pause(g:refresh, 0) | en
com! -nargs=0 Roadmap :cal ToggleRoadmap()
fu! ToggleRoadmap()
    if !exists('g:roadmapbuf') || !bufexists(g:roadmapbuf)
        let g:roadmapbuf = bufadd('') | call bufload(g:roadmapbuf) | en
    cal RefreshRoadMap('')
    if index(tabpagebuflist(), g:roadmapbuf) == -1
        exe 'bo vsplit |b'.g:roadmapbuf.'|vert res 25'
        cal setbufvar(g:roadmapbuf, '&rnu', 0) | cal setbufvar(g:roadmapbuf, '&nu', 0)
        cal setbufvar(g:roadmapbuf, '&ft', 'roadmap')
        syn match rmap_mks    /󰉁.*/  containedin=ALL | hi rmap_mks      ctermfg=196
        syn match rmap_git    /.*/  containedin=ALL | hi rmap_git      ctermfg=208
        syn match rmap_anchor / .*/ containedin=ALL | hi rmap_anchor   ctermfg=129
        syn match rmap_qf     /󰙒 .*/ containedin=ALL | hi rmap_qf       ctermfg=227
        syn match rmap_curr   /^>/   containedin=ALL | hi rmap_curr     ctermfg=82
        syn match rmap_extmk  / .*/ containedin=ALL | hi rmap_extmk    ctermfg=154
        wincmd p " jump back to main window
    en
endf

fu! CurrentLn()
    retu (IsDyBuf() ? trim(split(getline('.'), '|')[0]) : line('.'))
endf
fu! EndLn()
    retu (IsDyBuf() ? b:dy_total_ln : line('$'))
endf

fu! RefreshRoadMap(timer)
    if !exists('g:roadmapbuf') || &ft == 'roadmap' | retu | en
    if index(tabpagebuflist(), g:roadmapbuf) < 0 | cal timer_pause(g:refresh, 1) | en
    " clear buf content first
    for i in range(1, 999) | cal setbufline(g:roadmapbuf, i, '') | endfor
    call setbufline(g:roadmapbuf, 1, ['  Roadmap:'])

    let marks = GetMarks()

    if !has_key(marks, str2nr(CurrentLn())) | let marks[str2nr(CurrentLn())] = '>>>>>' | en
    if exists('b:anchorLn') && b:anchorLn != 0 | let marks[str2nr(b:anchorLn)] = ' ' | en

    let [sortedlist, idx] = [sort(map(keys(marks), {_,v -> str2nr(v)}), 'n'), 2]
    for ln in sortedlist
        if !has_key(marks, ln) | continue | en
        if CurrentLn() == str2nr(ln) && marks[ln] == '>>>>>'
            call setbufline(g:roadmapbuf, idx, ['>'])
        el
            let fmt = (CurrentLn() == str2nr(ln) ? '> ' : '  '). '%'.len(EndLn()).'d %s'
            call setbufline(g:roadmapbuf, idx, [printf(fmt, ln, marks[ln])])
        en
        let idx += 1
    endfor
endf
fu! GetMarks() " marks for road map and jumping
    if IsDyBuf()
        let b:roadmarks = sort(map(keys(copy(b:dy_marks)), {_,v -> str2nr(v)}), 'n')
        retu copy(b:dy_marks)
    endif

    let marks = {}
    for mk in getmarklist(bufnr()) " marks
        let [mkn, ln] = [mk['mark'], mk['pos'][1]]
        if index(g:alphabet, mkn[1:]) >= 0 | let marks[str2nr(ln)] = '󰉁'.mkn[1:].' '.trim(getline(ln)) | en
    endfor
    for mkinfo in nvim_buf_get_extmarks(bufnr(), g:extmk, 0, -1, {'details':v:true}) " extmarks
        let [ln, txt] = [mkinfo[1]+1, mkinfo[3]['virt_text'][0][0]]
        let marks[str2nr(ln)] = (has_key(marks, str2nr(ln)) ? marks[str2nr(ln)] : '').txt
    endfor
    if FugitiveStatusline() != '' && filereadable(expand('%:p')) " git diffs
        let path = getcwd()
        cal chdir(expand('%:p:h'))
        for dif in split(system('git diff --unified=0 '.expand('%').'| rg ^@@'), '\n')
            let ln = trim(matchstr(dif, '+\d*'))[1:]
            let marks[ln] = " ".trim(getline(ln))
        endfor
        cal chdir(path)
    en
    for qf in filter(copy(getqflist()), {_,i -> i['bufnr']==bufnr()}) | let marks[qf['lnum']] = '󰙒 '.trim(qf['text']) | endfor
    let b:roadmarks = sort(map(keys(marks), {_,v -> str2nr(v)}), 'n')
    retu marks
endf
fu! GoMark(flag) " 0 for prev; 1 for next
    let next = filter(copy(b:roadmarks), {_, i -> a:flag ? (i > CurrentLn()) : (i < CurrentLn())})
    if len(next) > 0
        let target = (a:flag ? next[0] : next[-1])
        exe (IsDyBuf() ? 'DyLocate '.target : target)
    en
    cal RefreshRoadMap('')
endf
let g:refresh = timer_start(1000, 'RefreshRoadMap', {'repeat': -1})

" file system movement
fu! InitFileMoveMap()
    let [g:fileMoveMap, _files] = [{}, split(system('find '.expand('%:p:h').' -maxdepth 1 -not -type d '), '\n')]
    if len(_files) == 1
        let g:fileMoveMap[_files[0]] = {'prev':'', 'next':''}
        return
    endif

    for idx in range(len(_files))
        let [_prev, _next] = [_files[idx], _files[idx]]
        if idx != 0 | let _prev = _files[idx-1] | endif
        if idx != len(_files) - 1 | let _next = _files[idx+1] | endif
        let g:fileMoveMap[_files[idx]] = {'prev' : _prev, 'next' : _next}
    endfor
endf
au BufEnter * if filereadable(expand('%:p')) && g:jumpMode=='F' | cal InitFileMoveMap() | en

" Quick Comment

" Diff
hi DiffText ctermbg=88
hi DiffChange ctermbg=none
hi DiffDelete ctermbg=245
hi DiffAdd ctermbg=86 ctermfg=black
fu! Diffthese()
    let [curr, wins] = [win_getid(), gettabinfo(tabpagenr())[0]['windows']]
    for winId in wins
        cal win_gotoid(winId) | diffthis
    endfor
    cal win_gotoid(curr)
endf
com! -nargs=0 Dfthese :cal Diffthese()
" FreezeLeft
fu! FreezeLeft()
    exe 'only | vertical split '.expand('%:p')
    cal Diffthese()
    exe "norm \<c-w>l"
    setlocal nonu nornu scl=no fdc=0
    exe "norm \<c-w>h"
    setlocal scrollopt=ver,jump
endf
com! -nargs=0 FreezeLeft :cal FreezeLeft()

" Pair Hint
hi PairHint cterm=bold ctermfg=red ctermbg=black
hi PairHintNext cterm=bold ctermfg=yellow ctermbg=black
fu! MarkPairs(pair_info)
    cal ClearVirtualTxt()
    for pi in a:pair_info
        cal MarkPair(pi.start, pi.end, pi.left, pi.right, pi.hl)
    endfor
endf
fu! MarkPair(start, end, left, right, hl)
    if a:start > 0 | cal VirtualMarkWrapper(line('.')-1, a:start-1, a:left, a:hl) | en
    if a:end > 0 | cal VirtualMarkWrapper(line('.')-1, a:end-1, a:right, a:hl) | en
endf
fu! s:MarkRst(jobId, data, event)
    if (!exists('b:phJid') && !exists('b:qhJid')) || a:jobId != b:phJid && a:jobId != b:qhJid | retu | en
    let rst = trim(a:data[0])
    if match(rst, '\v^-?\d+. -?\d+.') >= 0
        let _col = wincol()-getwininfo(win_getid())[0]['textoff']
        let [pairs, pair_info] = [split(rst, ' '), []]
        let [_start, _end] = pairs[:1]
        let [_l1, _l2] = [strlen(_start)-1, strlen(_end)-1]
        cal add(pair_info, {'start': _col + _start[:_l1-1], 'end':_col + _end[:_l2-1], 'left':_start[_l1], 'right':_end[_l2], 'hl':'PairHint'})
        if len(pairs) >= 4 && str2nr(_start[:_l1-1]) <= 0
            let [_start, _end] = pairs[2:3]
            let [_l1, _l2] = [strlen(_start)-1, strlen(_end)-1]
            cal add(pair_info, {'start': _col + _start[:_l1-1], 'end':_col + _end[:_l2-1], 'left':_start[_l1], 'right':_end[_l2], 'hl':'PairHintNext'})
        endif
        cal MarkPairs(pair_info)
    endif
endf
fu! PairHint()
    if virtcol('.') > virtcol('$')-1 | retu | en
    let cchar_nr = strgetchar(getline('.')[col('.') - 1:], 0)
    if !empty(getline('.')) && mode() == 'n' && cchar_nr >= 0
        let ch_width = system("hexdump -v -e '/1 \"%02x\"' | /root/.config/nvim/char_width", nr2char(cchar_nr))
        let ccol = virtcol('.') - (ch_width-1)
        let bs = system("hexdump -v -e '/1 \"%02x\"'", getline('.'))
        let b:phJid = jobstart('echo ' . bs .' | '. join(['/root/.config/nvim/pair_hint', ccol, &tabstop], ' '), {'stdout_buffered':v:true, 'on_stdout':function('s:MarkRst')})
        let b:qhJid = jobstart('echo ' . bs . ' | '. join(['/root/.config/nvim/quote_hint', ccol, &tabstop], ' '), {'stdout_buffered':v:true, 'on_stdout':function('s:MarkRst')})
    endif
endf
au CursorHold * if &ft!='xxd' | cal PairHint() | en
" log highlight
com! -nargs=0 LogHl :so ~/.config/nvim/syntax/log.vim
" }}}
" => Automatic -------------------- {{{
" au InsertLeave * :execute 'sil! .s/\s\+$//'
set wmnu wim=list:longest,full fic wic
" set nrformats+=octal " let CTRL-A/CTRL-X support octal number
"   auto check time
au WinEnter,CursorHold,FocusGained * if expand('%')!=""|checktime

"   add dictionaries here. tip: add outside candidates through dictionary file
set dict+=/usr/share/dict/en
set dict+=/usr/share/dict/esp

set cot=menu,menuone,noselect,preview ssop+=globals

"   auto completion
let [g:completingId, g:jpIme, g:cnIme, g:inserted, g:refreshFlag, g:pathQueue, g:omniExclude, g:serviceBlackList] = [0, 0, 0, '', 0, {}, {}, {}]
fu! SendService(arg1, arg2)
    let cmd = ['~/.config/nvim/complete_service.py', a:arg1, a:arg2]
    retu join(cmd, ' ')
endf
let g:completeKinds = {1:' Text',2:' Method',3:'󰊕 Function',4:' Constructor',5:' Field',6:'󰫧 Variable',7:' Class',8:' Interface',9:'󰕳 Module',10:' Property',11:'Unit',12:'Value',13:'Enum',14:' Keyword',15:' Snippet',16:'Color',17:'File',18:'Reference',19:'Folder',20:'EnumMember',21:' Constant',22:'Struct',23:'Event',24:' Operator',25:'TypeParameter',}
fu! LspItemsToCompleteItems(fromLsp)
    let rst = []
    for item in sort(a:fromLsp.result.items, {i1, i2 -> len(i1.label) - len(i2.label)})[:10]
        cal add(rst, {'word' : substitute(trim(item.label), '^•', '', ''), 'menu' : g:completeKinds[item.kind]})
    endfor
    retu rst
endf
fu! RenderCandidate(_, word)
    let seq = split(a:word, ' ')
    let menu = len(seq) == 1 ? g:completeKinds[1] : join(seq[1:], ' ')
    retu {'word':seq[0].b:candidateSupply, 'menu':menu}
endf
fu! s:GotCandidates(jobId, data, event)
    let b:candidateSupply = (g:pLang == 'de' ? ' ' : '')
    if a:jobId == g:completingId && mode() == 'i'
        let [candidates, b:c_items, g:inserted] = [filter(a:data, {_,item -> item != ''}), [], InsertingWord()]
        if &omnifunc != '' && !g:jpIme && !g:cnIme && !has_key(g:omniExclude, &ft) " blocking request
            let luacmd = "vim.lsp.buf_request_sync(".bufnr().",'textDocument/completion', vim.lsp.util.make_position_params(), 500)"
            try
                let _clientId = luaeval("next(".luacmd.")")
                let fromlsp = luaeval(luacmd."["._clientId."]")
                let b:c_items = LspItemsToCompleteItems(fromlsp)
            catch | endtry
        endif
        cal extend(b:c_items, map(candidates, function('RenderCandidate')))
        if col('.') >= 2 && count(split(getline('.')[:col('.')-1], ' ')[-1], '/') >= 2
            sil cal nvim_feedkeys("\<c-x>\<c-f>", 'i', v:false)
        else
            let b:c_page = 1
            cal PumPageLoc(b:c_page)
        endif
    endif
endf
let g:CMN = {0:'Normal', 1:'New', 2:'Length', 3:'Chosen'} " CandidateModeName
fu! PumPageLoc(pn)
    let c_len = len(b:c_items)
    if 0 < a:pn && a:pn * 10 <= (c_len + (c_len % 10 > 0 ? 10 : 0))
        let [start, end, b:c_page] = [(a:pn-1)*10, 10*a:pn-1, a:pn]
        cal complete(col('.') - len(InsertingWord()), b:c_items[start:end])
        let total_page = len(b:c_items)/10 + (len(b:c_items)%10>0?1:0)
        cal nvim_buf_set_extmark(bufnr(), g:vertLineMark, line(".")-1, 0,
                    \ { "virt_text":[[printf('[%d/%d]', b:c_page, total_page), 'SnipAnon'],
                    \[printf(' %s', g:CMN[g:candidatesOrderMode%4] ), 'SnipMark']],
                    \"hl_mode":"combine" })
    endif
    retu ''
endf
ino <m-,> <c-r>=PumPageLoc(b:c_page-1)<cr>
ino <m-.> <c-r>=PumPageLoc(b:c_page+1)<cr>
let g:candidatesOrderMode = 0
ino <m-i> <c-\><c-o>:let g:candidatesOrderMode+=1 \| cal RefreshCandidates()<cr>
fu! RefreshCandidates()
    let cw = InsertingWord()
    if len(cw) < 1 || complete_info(['mode'])['mode'] == 'files' | retu | en
    let query = g:jpIme ? '-query_jp' : g:cnIme ? '-query_cn' : '-query'.(g:pLang == '' ? '' : '_'.g:pLang)
    let g:completingId = jobstart(SendService(query, printf("\"%s\" \"%s\" %d", cw, expand('%p'), g:candidatesOrderMode)), {'stdout_buffered':v:true, 'on_stdout':function('s:GotCandidates')})
endf
fu! RefreshService(timer)
    if g:refreshFlag == 1 || empty(g:pathQueue) | retu | en
    let cmd = SendService('-add_path', join(keys(g:pathQueue), ' '))
    let [g:refreshFlag, g:pathQueue] = [1, {}] " set running flat
    cal jobstart(cmd, {'on_exit': {jobId, data, event -> execute('let g:refreshFlag = 0|redrawtabline')}, 'detach':v:true})
endfunction
au BufReadPost,BufWritePost,BufEnter * if filereadable(bufname(bufnr())) && !has_key(g:serviceBlackList, bufname(bufnr()))
            \| let g:pathQueue[expand('%:p').':'.getbufvar(bufnr(), "&fenc")] = 1 | en
cal timer_start(1500, 'RefreshService', {'repeat': -1})
au CursorMovedI,CursorHoldI,TextChangedP * sil redraw! | cal RefreshCandidates() | cal ClearVirtualTxt()
au CompleteChanged * cal PumRenderVerticalScope(virtcol('.')-len(InsertingWord())-3)
" au CursorMovedI * if complete_info()['mode'] == 'function' | cal nvim_feedkeys("\<C-x>\<C-u>", "i", 1) | en
fu! PostComplete()
    if exists("v:completed_item['word']")
        cal jobstart(SendService((g:jpIme ? '-chosen_jp' : (g:cnIme ? '-chosen_cn' : '-chosen')), v:completed_item['word'].' '.g:inserted), {'detach':v:true})
        let g:exAnonExpand = ''
    en
endf
au CompleteDonePre * if complete_info(['mode'])['mode'] == 'files' && !empty(complete_info(['items']).items)
            \| sil cal nvim_feedkeys("\<c-x>\<c-f>", 'i', v:false) | en
au CompleteDone * redraw! | cal PostComplete()
au CompleteDone * if (g:jpIme || g:cnIme) && v:completed_item != {} | cal nvim_feedkeys("\<esc>a", 'i', v:false) | en
au User ImeChanged if (g:jpIme || g:cnIme) | exe "ino <silent> <BS> <BS><esc>a" | else | exe "sil! iu <BS>" | en
"   <tab> for select candidate, j+n for quick selection
im <silent><expr> <tab> pumvisible() ? "\<down>" : (UltiSnips#CanExpandSnippet() ? "\<c-l>" : "\<tab>")
ino <silent><expr> <s-tab> pumvisible() ? "\<up>" : "\<tab>"
for i in range(2, 9)
    exe printf("im j%d %s<cr>", i, repeat("<tab>", i))
    exe printf("im J%d %s<cr>", i, repeat("<s-tab>", i))
endfor
exe printf("im j%d %s<cr>", 0, repeat("<tab>", 10))
exe printf("im j<space> %s<cr>", "<tab>")
"   snip expand
im <silent><expr> <c-l> (g:canSnipExpand \|\| UltiSnips#CanExpandSnippet()) ? "\<c-r>=UltiSnips#ExpandSnippet()\<cr>" :
            \ AnonExpand() != '' ? "\<c-r>=UltiSnips#Anon(AnonExpand(), InsertingWord(), '', 'i', '', {})<cr>" :
            \ UltiSnips#CanJumpForwards() ? "\<c-k>" :
            \ "\<esc>A"
"   FZF integration
ino <expr> <c-x><c-k> fzf#vim#complete(extend(FzfFloatWin(), {'source':'cat /usr/share/dict/en /usr/share/dict/esp /usr/share/dict/ngerman'}))
ino <expr> <c-x><c-l> fzf#vim#complete#line({}, 1)
ino <expr> <c-x><c-h> fzf#vim#complete#buffer_line({}, 1)
nn <F1> :Helptags!<CR>
"   Consumable Autocmd
let g:cmdToConsume = []
fu! ConsumeCmd()
    let [_cmds, g:cmdToConsume] = [g:cmdToConsume, []] " clear cmd list
    for cmd in _cmds | cal execute(cmd) | endfor
endf
au BufWinEnter *.* sil cal ConsumeCmd()|cal SignMarks()
"   Yank History
let [g:yankHistory, g:YankHistorySave] = [[], '[]']
au TextYankPost * cal AddYankHist(getreg('"'))
let g:syncClip = 0
fu! AddYankHist(toAdd)
    if g:syncClip == 1 | cal setreg('+', a:toAdd) | en
    let [tmpl, sha] = [[], sha256(a:toAdd)]
    for item in g:yankHistory
        if sha256(item) != sha | cal add(tmpl, item) | en
    endfor
    cal add(tmpl, substitute(a:toAdd, '\\', '\\\\', 'g'))
    let g:yankHistory = len(tmpl) > 100 ? tmpl[-100:] : tmpl
    if match(a:toAdd, '^\i*$') >= 0
        cal jobstart(SendService('-chosen', a:toAdd), {'detach':v:true}) | en
    let g:YankHistorySave = string(filter(copy(g:yankHistory), {_,his -> stridx(his, "\n") == -1}))
endf
fu! PutYankHist(target)
    if len(a:target) == 1
        let @" = a:target[0]
    else
        echoh MoreMsg | echo 'delimiter (one char):' | echoh None
        let delimiter = nr2char(getchar())
        let @" = join(a:target, (delimiter == "\<cr>" ? "\n" : delimiter))
    endif
    norm p
    cal AddYankHist(getreg('"'))
endf
au SessionLoadPost * exe 'let g:yankHistory = ' . g:YankHistorySave
fu! FzfFloatWin()
    let fzfCurOpts = {'width':55, 'height': 15,
                \ 'xoffset': (virtcol('.')*1.0)/winwidth(0) + 0.07,
                \ 'yoffset': (winline()*1.0)/winheight(0) + 0.2}
    retu {'source':reverse(copy(g:yankHistory)), 'options':g:MfzfOpts, 'window':fzfCurOpts}
endf
nn <c-p> :cal fzf#run(extend({'sinklist': function('PutYankHist')}, FzfFloatWin()))<cr>
ino <expr> <c-p> fzf#vim#complete(extend(FzfFloatWin(), {'source':reverse(filter(copy(g:yankHistory), {_,his -> stridx(his, "\n") == -1}))}))
" awk misc
let [g:awk_file, g:awk_shadow, g:awk_func] = ['~/.config/nvim/awk-template.awk', 0, '~/.config/nvim/awk-lib/functions.awk']
ca aa %!awk -f <c-r>=g:awk_file<cr> FILE_NAME=<C-R>=expand('%:p')<CR>
ca af !awk -f <c-r>=g:awk_file<cr> FILE_NAME=<C-R>=expand('%:p')<CR>
ca ar AwkRange
ca raf r !awk -f <c-r>=g:awk_file<cr> FILE_NAME=<C-R>=expand('%:p')<CR>
ca an cal AwkToTemp()<cr>
ca ae tabe \| e +/main/;norm\ ztjj <c-r>=g:awk_file<cr>
ca aef tabe \| e <c-r>=g:awk_func<cr>
ca ase bo vsplit \| e +/main/;norm\ ztjj <c-r>=g:awk_file<cr>
ca asef bo vsplit \| e <c-r>=g:awk_func<cr>
fu! AwkToTemp() " direct awk result to a new temporary file
    let target_file = expand('%:p')
    if IsDyBuf() | let target_file = b:dy_file | endif
    cal execute(printf('tabe | e %s | r !awk -f %s %s', tempname(), g:awk_file, target_file))
    exe "norm ggdd:w\n"
endf
fu! AwkRange(n)
    exec printf('.r !for run in {1..%d} ; do echo ; done', a:n)
    exec printf('norm %dk', a:n-1)
    sil exec printf('.,.+%d !awk -f %s FILE_NAME=%s', a:n-1, g:awk_file, expand('%:p'))
endf
com! -nargs=1 AwkRange :cal AwkRange(<f-args>)
fu! AwkOp(type)
    let range = (a:type ==# 'line' ? "'[,']" : ".")
    exe printf("%s!awk -f %s FILE_NAME=%s", range, g:awk_file, expand('%:p'))
    if g:autoIndentFlg == 1 | exe 'norm! `]j=`[' | en " auto indent after Op
endf
nn <silent> ,a :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)\|set opfunc=AwkOp<cr>g@
" openpyxl misc
com! -nargs=0 EdXl tabe | e +/script-here/;norm\ ztjj ~/.config/nvim/xl-script.py
ca xl !python3 ~/.config/nvim/xl-script.py <C-R>=expand('%:p')<cr>
ca xlrb !python3 ~/.config/nvim/xl-rollback.py <C-R>=expand('%:p')<cr>
" QuickFix Reflection
fu! OpenQfBuf()
    let [g:qfbufnr, idx] = [bufadd('QuickFix-Reflection'), 1]
    cal bufload(g:qfbufnr)
    cal setbufvar(g:qfbufnr, '&ft', 'qfedit')
    for qfItem in getqflist()
        cal setbufline(g:qfbufnr, idx, [printf("%4d | %5d |%s", qfItem['bufnr'], qfItem['lnum'], qfItem['text'])])
        let idx += 1
    endfor
    exe 'tabe |b'.g:qfbufnr
endf
fu! ReflectOneline(ln)
    let raw = getline(a:ln)
    let bn = str2nr(raw[:match(raw, '|')-1])
    let raw = raw[match(raw, '|')+1:]
    let ln = str2nr(raw[:match(raw, '|')-1])
    let raw = raw[match(raw, '|')+1:]
    if !bufloaded(bn) | cal bufload(bn) | endif
    cal setbufline(bn, ln, [raw])
    return bn
endf
fu! ReflectAll()
    let target = {}
    for ln in range(line('$'))
        let bn = ReflectOneline(ln+1)
        redraw | echo printf('Reflecting... (%d/%d)', ln+1, line('$'))
        let target[bn] = 1
    endfor
    for bn in keys(target)
        exe 'b'.bn | update
    endfor
    exe 'bd!'.g:qfbufnr
    redraw | echo 'Done!'
    norm :q
endf
com! -nargs=0 QfEdit :cal OpenQfBuf()
" sqlfluff misc
let g:fluffConfigPath = ''
fu! SqlOp(type)
    exe printf("%s!sqlfluff fix --quiet -", (a:type ==# 'line' ? "'[,']" : "."))
endf
nn <silent> ,,s :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)\|set opfunc=SqlOp<cr>g@
let g:sqlLintMk = nvim_create_namespace('sqlLintMk')
fu! s:putSqlLintRst(jobId, data, event) abort
    let g:asyncCnt -= 1 | redrawt
    let bufnr = '' " get bufnr from tab-windows
    for tn in range(1, tabpagenr('$'))
        let winIds = gettabinfo(tn)[0]['windows']
        let bufnrs = uniq(map(winIds, {_,wi -> getwininfo(wi)[0]['bufnr']}))
        let bufnr = filter(copy(bufnrs), {_, bn -> getbufvar(bn, 'sqlJobId') == a:jobId})
        if !empty(bufnr) | break | en
    endfor
    if empty(bufnr) | return | en

    for info in filter(copy(a:data), '!empty(v:val)')
        let _info = split(info, '|') 
        let [ln, txt] = [str2nr(_info[0]), printf('■ %s|%s', _info[1], _info[2])]
        cal nvim_buf_set_extmark(bufnr[0], g:sqlLintMk, ln-1, 0, { "virt_text":[[txt, 'SnipMark']], "hl_mode":"combine" })
    endfor
endf
fu! SqlLintCmd()
    let g:asyncCnt += 1
    cal DelLineExtMark(g:sqlLintMk, 0, -1)
    let cmd = printf("sqlfluff lint %s --format json %s |", expand('%'), (empty(g:fluffConfigPath) ? '' : ' --config '.g:fluffConfigPath))
    let cmd .= " python3 -c 'import sys, json;"
    let cmd .= " [print(v[\"start_line_no\"], v[\"code\"], v[\"description\"], sep=\"|\") for v in json.load(sys.stdin)[0][\"violations\"]]'"
    return cmd
endf
com! -nargs=0 SQLint :let b:sqlJobId = jobstart(SqlLintCmd(), {'stdout_buffered':v:true, 'on_stdout':function('s:putSqlLintRst')})

" }}}
" => Handle -------------------- {{{
" :h key-notation to get more key combination patterns or Ctrl-V to hard-coding

" leader, second leader ','
let mapleader=" "

" Moving
"   <c-y>, <c-e>, zh, zl for scroll window
au WinEnter,BufReadPost * sil exe 'nn <Left> ' . winwidth(0) / 6 . 'zh'
au WinEnter,BufReadPost * sil exe 'nn <Right> ' . winwidth(0) / 6 . 'zl'
nn ^ g^
"   to next non-ascii char, origin from Japanese, so 'j'
nmap ,gj /[^\x00-\x7F]\+<CR>
nn <Down> <c-d>
nn <Up> <c-u>
"   FZF moving
nn <leader>m :Marks!<CR>
nn <leader>l @=(&filetype=='ark'?':cal IndoEuropeanFZF()':':Lines!')<CR><CR>
vn <leader>l "vy:let@"=@0\|Lines! <C-R>v<CR>
nn ,l :BLines!<CR>
vn ,l "vy:let@"=@0\|BLines! <C-R>v<CR>
"   enhanced jump back
fu! BufJumpBack()
    let curBufName = expand('%:p')
    wh curBufName == expand('%:p')
        exe "norm! \<C-O>"
        let _ = bufnr('%')
    endw
endf
fu! ModWinResize()
    if g:jumpMode != 'w' | retu | en
    let [h, l] = (win_screenpos(winnr())[1] == 1 ? ['<', '>'] : ['>', '<'])
    exe 'nn h <c-w>'.h
    exe 'nn l <c-w>'.l
endf
nn <a-o> :cal BufJumpBack()<cr>
let g:jumpMode = 'n'
let g:jumpModeNames = {'n':'Normal','m':'Mark','F':'Fold','s':'Scroll','q':'Quickfix','d':'Diff','w':'Window','c':'Conflict', 'r':'Roadmap', 'f':'FileSystem'}
fu! OmniJumpBoot(backNormFlag)
    let jumpMoves = {'nj':'j','nk':'k',
                \'mj':"]'", 'mk':"['",
                \'qj':':cn<cr>','qk':':cp<cr>',
                \'Fj':'zj','Fk':'zk','Fh':':setl fdl-=1<CR>','Fl':':setl fdl+=1<CR>',
                \'fj':":sil cal MEdit(g:fileMoveMap[expand('%:p')]['next'])<cr>", 'fk':":sil cal MEdit(g:fileMoveMap[expand('%:p')]['prev'])<cr>",
                \'wj':'<c-w>-','wk':'<c-w>+','wh':'<c-w>>','wl':'<c-w><',
                \'sj':'<c-d>','sk':'<c-u>','sh':'60h','sl':'60l',
                \'rj':':sil cal GoMark(v:true)<cr>', 'rk':':sil cal GoMark(v:false)<cr>',
                \'cj':':let @/="\\m^======="<cr>n','ck':':let @/="\\m^======="<cr>N',
                \'cl':'V?\m^<<<<<<<<cr>d/\m^>>>>>>><cr>dd','ch':'V/\m^>>>>>>><cr>d?\m^<<<<<<<<cr>dd',
                \'dj':'<Plug>(signify-next-hunk)','dk':'<Plug>(signify-prev-hunk)','dh':'<c-w>h','dl':'<c-w>l'}
    let modeChar = 'n'
    echoh MoreMsg | echo join(values(g:jumpModeNames), ' - ') | echoh None
    if a:backNormFlag == 0
        let modeChar = nr2char(getchar()) " wait for a mode char
    en
    if modeChar == 'r' | cal ToggleRoadmap() | en " open road map
    if modeChar == 'F' | cal InitFileMoveMap() | en
    exe printf("hi CursorLine cterm=NONE ctermbg=%s", (modeChar == 'c' ? '167' : 'DarkGray'))
    let g:jumpMode = has_key(g:jumpModeNames, modeChar) ? modeChar : 'n'
    exe printf('hi JumpModColor cterm=bold ctermfg=%d ctermbg=%d', char2nr(g:jumpMode), ((char2nr(g:jumpMode) + 16) % 256))
    for direct in split('hjkl', '\zs')
        exe printf('nn %s %s', direct, get(jumpMoves, g:jumpMode.direct, direct))
    endfor
    cal ModWinResize()
endf
au WinEnter * sil cal ModWinResize()
nn <leader>j :cal OmniJumpBoot(0)<CR>
nn <leader><leader> :cal OmniJumpBoot(1)<cr>
" past and auto-indent
let g:autoIndentFlg = 1
fu! IIP() " If Indent Past
    if g:autoIndentFlg != 1 || &ft == '' | retu -1 | en
    let lines = count(getreg(v:register), "\<NL>")
    retu lines
endf
nn <silent> p @=(IIP() > 0 ? "p=".(IIP() == 1 ? "l" : (IIP()-1)."j") : "p")<CR>
nn <silent> P @=(IIP() > 0 ? "P=".(IIP() == 1 ? "l" : (IIP()-1)."j") : "P")<CR>

" Hiraishin  -------------------- {{{
let g:HRSmode=1 " HiRaiShin mode
let g:hda=(exists('g:hda') ? g:hda : {}) " hda for 'hiraishin directory anchors'
nn <leader>H @=(has_key(g:hda,getcwd())==1 ? ':unlet g:hda[getcwd()]' : ':let g:hda[getcwd()]=1')<CR><CR>
nn <silent> <leader>Y :cal fzf#run({'source': keys(g:hda), 'sink': 'lcd','window':{'width':0.9,'height':0.6}})<CR>
nn <silent> <leader>D :cal fzf#run({'source': keys(g:hda), 'sink': {p -> execute('unlet g:hda["'.p.'"]')}, 'window':{'width':0.9,'height':0.6}})<CR>
nn <silent> <leader>o @=(g:HRSmode==1?':cal HiraishinOpen("", "MEdit", 0)':':Files')<CR><CR>
vn <silent> <leader>o @=(g:HRSmode==1?':cal HiraishinOpen(Selected(), "MEdit", 0)':':Files')<CR><CR>
vn <silent> <leader>O @=(g:HRSmode==1?':cal HiraishinOpen(".".Selected(), "MEdit", 0)':':Files')<CR><CR>
let g:openExclude = ['"*.class"']
let g:openExcludePath = ['"*/target/*"', '"*/.git/*"']
fu! OpenByFile(fn)
    let [paths, e] = ['', empty(g:openExclude) ? '' : ' -not -name '.join(g:openExclude, ' -not -name ')]
    let e .= empty(g:openExcludePath) ? '' : ' -not -ipath '.join(g:openExcludePath, ' -not -ipath ')
    for anchor in keys(extend(copy(g:hda), {getcwd():1})) " include cwd
        let paths .= ' '.RelPath(anchor, getcwd())
    endfor
    retu printf('find %s %s -type f %s', paths, ' -ipath "*'.trim(a:fn).'*"', e)
endf
fu! OpenByTarget(q, t)
    let rgCmds = ''
    if trim(a:q) != ''
        let findCmd = OpenByFile(a:q)
        retu printf('%s | xargs rg -l --hidden -F "%s"', findCmd, a:t)
    en
    for anchor in keys(extend(copy(g:hda), {getcwd():1})) " include cwd
        let rgCmds .= printf('rg -l --hidden -F "%s" %s;', a:t, anchor)
    endfor
    retu rgCmds
endf
fu MEdit(path)
    let cmd = bufnr(a:path) > 0 ? ('b'.bufnr(a:path)) : ('edit '.a:path)
    exe cmd
endf
com! -nargs=1 MEdit :cal MEdit(<f-args>)
fu! HiraishinOpen(query, sink, showSize) " query.target
    let queries = split(' '.a:query, '[\./@]')
    let q = a:query=='' ? '' : queries[0] " query for file
    let t = len(queries) > 1 ? (exists('*ReduceTarget') ? ReduceTarget(queries[1]) : queries[1]) : '' " target for content

    if t != ''
        let findCmds = OpenByTarget(q, t) " target orient
        let @/ = '\<'.t.'\>'
        let g:cmdToConsume = ["norm ggn", 'setl stl=%!ActStl(1) cuc cul']
    el
        let findCmds = OpenByFile(trim(q))   " file name orient
    en
    if a:showSize == 1 | let findCmds.= " -print0 | xargs -0 ls -lhS | awk '{printf \"%5s|%s\\n\", $5, $9}'" | endif
    cal fzf#run({'source':findCmds, 'sink':a:sink, 'options':extend(copy(g:MfzfOpts), ['--query='.trim(q)])})
endf
" }}}

xn <expr> <Up> { 'V':repeat('k', winheight(0)/3) }[mode()]
xn <expr> <Down> { 'V':repeat('j', winheight(0)/3) }[mode()]
xn <silent>x :<C-U>call cursor(line("'}")-1,col("'>"))<CR>`<1v``
" Quick back to normal mode
let g:PreferQuitIme = 0
ino <silent> jk <esc>:if g:PreferQuitIme==1 \| let [g:jpIme, g:cnIme] = [0, 0] \| do User ImeChanged \|en<cr>
ino <silent> jK <esc>:if g:PreferQuitIme==0 \| let [g:jpIme, g:cnIme] = [0, 0] \| do User ImeChanged \|en<cr>
cno <expr> jk getcmdtype() == ':' ? '<c-u><esc>' : 'jk'
tno jk <c-\><c-n>
xn JK <esc>

" Searching
"   see "h /character-classes for more pattern shortcut
nn <f6> :let @+ = join(getline(2, '$'), "\n") " copy content<CR>
set ic scs hls is nows   " ignorecase smartcase hlsearch incsearch nowrapscan
vn * y/<C-R>"<cr>
vn # y?<C-R>"<cr>
"   QuickFix searching
let g:qfHist = (exists('g:qfHist') ? g:qfHist : {}) " qfSearchHistory
set gp=rg\ --vimgrep\ --ignore-case\ --hidden\ --follow
com! -nargs=* QfSearch :sil exe 'vimgrep /'.(len(<q-args>)==0?Selected():<q-args>).'/j '.join(GetBufFilePath(v:false), " ")
com! -nargs=0 QfJearch :sil exe 'vimgrep /[^\x00-\x7F]/j '.expand('%')|copen|setl cul
nn ,F yiw:QfXearch <c-r>"
vn ,F y:QfXearch <c-r>"
nn ,,F yiw:QfXearch! <c-r>"
vn ,,F y:QfXearch! <c-r>"
com! -bang -nargs=* QfXearch :cal Xearch(<bang>0, <f-args>)
com! -nargs=0 QfAll :cal fzf#run({'source': keys(g:qfHist), 'sink': {inst->setqflist(g:qfHist[inst])},})
com! -nargs=1 QfYank :cal extend(g:qfHist, {<f-args>:getqflist()}) " save search result
com! -nargs=0 QfRemove :cal fzf#run({'source': keys(g:qfHist), 'sink': {inst->execute('unl g:qfHist["'.inst.'"]')},})
fu! QfMark()
    let [_, lnum, cnum, _, _] = getcurpos()
    let qfItem = [{'bufnr':bufnr(), 'lnum':lnum, 'col':cnum, 'text': getline('.')}]
    cal setqflist(extend(getqflist(), qfItem))
    cal SignMarks()
endf
com! -nargs=0 QfMark :cal QfMark()

" Fold
set fdm=manual fdl=99 fdc=auto:7
hi FoldColumn ctermbg=None ctermfg=blue

" Windows
"   split
fu! SplitOp(sc, query) " run a split cmd first, then operate
    let op = nr2char(getchar())
    let opts = extend(copy(g:MfzfOpts), ['--query='.a:query])
    if (op ==# 'o') " Open File
        cal HiraishinOpen(a:query, a:sc.'MEdit', 0)
    elseif (op ==# 'O')
        cal HiraishinOpen('.'.a:query, a:sc.'MEdit', 0)
    elseif (op == 'b') " Buffer
        cal ClearNoName()
        let sorted = fzf#vim#_buflisted_sorted()
        cal fzf#run({'source':map(sorted, {_,bn->bn.' '.bufname(bn)}),
                    \'sink':{bn->execute(a:sc.'b'.matchstr(bn, '^[0-9]*'))}, 'options':opts,})
    elseif (op ==# 't') " Tag
        cal GoToTag(a:sc.'MEdit', GetDefault(a:query, expand("<cword>")))
    elseif (op == 'q') " QuickFix
        cal fzf#run({'source': map(getqflist(), {_,qf -> printf('+%d %d %s | %s', qf['lnum'], qf['bufnr'], Shortf(bufname(qf['bufnr'])), trim(qf['text']))}),
                    \'sink': {pi->execute(a:sc.'b '.matchstr(pi, '+\d*\s\d*'))}, 'options':opts,})
    elseif (op == 'm') " ExMarks
        cal fzf#run({'source': GetAllExmarks(), 'sink': {mk->execute(a:sc.'b '.matchstr(mk, '+\d*\s\d*'))}, 'options':opts,})
    elseif (op ==# 'T') " Terminal
        echoh MoreMsg | echo '[N]ew [C]urrent' | echoh None
        let _op = nr2char(getchar())
        exe (_op ==# 'c') ? 'FloatermNew --cwd='.expand('%:h') : (_op ==# 'n' ? 'FloatermNew' : 'FloatermToggle')
    elseif (op ==# 'f') " temporary file
        let tempname = tempname()
        cal fzf#run({'source': [tempname], 'sink': {tf->execute(a:sc.'MEdit '.tf)}, 'options':opts,})
    elseif (op ==# 'g') " Git modified file
        let git_cmd = 'git status -s | rg "(^ M )|(^A  )|(^?? )" | sed "s/\(^ M \)\|\(^A  \)\|\(^?? \)//"'
        cal fzf#run({'source': git_cmd, 'dir':expand('%:p:h'), 'sink': {tf->execute(a:sc.'MEdit '.tf)}, 'options':opts,})
    el
        exe a:sc."|norm \<C-L>"
    en
endf
nn ,s :cal SplitOp('bo vsplit\|', '')<CR>
nn ,S :cal SplitOp('bo split\|', '')<CR>
vn ,s :cal SplitOp('bo vsplit\|', Selected())<CR>
vn ,S :cal SplitOp('bo split\|', Selected())<CR>
fu! Getfloatopt(width, height)
    retu {'relative':'editor','width':a:width, 'height':a:height, 'col':(&columns - a:width)/2, 'row':(&lines - a:height)/2}
endf
nn ,f :cal SplitOp("cal nvim_open_win(bufnr(), 1, Getfloatopt(100, 30))\|", '')<CR>
vn ,f :cal SplitOp("cal nvim_open_win(bufnr(), 1, Getfloatopt(100, 30))\|", Selected())<CR>
nn ,o :let [g:bufToOpen, g:lnToGo, g:cmdToConsume] = [bufnr(), line('.'), ['norm zz']] \| quit! \| exe 'b +'.g:lnToGo.' '.g:bufToOpen<CR>
"   window navigation from any mode
for direct in split('hjkl', '\zs')
    exe printf('tno <a-%s> <c-\><c-n><c-w>%s', direct, direct)
    exe printf('nn <a-%s> <c-w>%s', direct, direct)
endfor

" Tab (ngt to go go n-th tab)
com! -bang -nargs=0 SetAnchor :let b:anchorLn=(<bang>0 ? 0 : line('.'))
set stal=2
hi TabLine cterm=none ctermfg=black ctermbg=247
hi Title cterm=bold ctermfg=red
hi Git ctermfg=Black ctermbg=185
hi Trans ctermfg=227 ctermbg=31
hi Obss ctermfg=Black ctermbg=118
hi CSInfo cterm=bold ctermfg=white ctermbg=blue
hi PreferLang ctermfg=black ctermbg=135
nn ,t :cal SplitOp('tabe \|', '')<CR>
vn ,t :cal SplitOp('tabe \|', Selected())<CR>
nn ,T :cal SplitOp('-tabe \|', '')<CR>
vn ,T :cal SplitOp('-tabe \|', Selected())<CR>
nn t gt
nn T gT

" buf-renmaing and dynamic-read file display
let g:buf_name = {}
com! -nargs=1 RenameBuf :let g:buf_name[bufnr()] = <f-args>
fu! Bufname(bn)
    if getbufvar(a:bn, 'is_dy_buf') == 1
        retu getbufvar(a:bn, 'dy_file')
    elseif has_key(g:buf_name, a:bn)
        retu g:buf_name[a:bn]
    endif
    return bufname(a:bn)
endf

fu! Shortf(fname)
    retu fnamemodify(a:fname, ':p:t')
endf
fu! Longf(fpath)
    if match(a:fpath, fnamemodify($MYVIMRC, ':p:h').'/.*') == 0
        retu ' '.fnamemodify(a:fpath, ':t')
    endif
    retu RelPath(a:fpath, getcwd())
endf
let g:asyncrun_red = {'':"", 'running':"  ", 'failure':"  "}
fu! ActTal()
    let [tal, curr] = ['', tabpagenr()]
    hi cc ctermfg=black ctermbg=lightgreen
    for tn in range(1, tabpagenr('$'))
        let [fg, bg] = ['white', 244-(tn % 6)]
        let winIds = gettabinfo(tn)[0]['windows']
        let bufnrs = uniq(map(winIds, {_,wi -> getwininfo(wi)[0]['bufnr']}))
        for bn in bufnrs
            if has_key(g:BufColors, bn) | let fg = string(g:BufColors[bn]) | en
        endfor
        let fname = map(bufnrs, {_,bn -> Shortf(Bufname(bn))})
        exe printf('hi c%s ctermfg=%s ctermbg=%s', bg, fg, bg)
        exe printf('hi ct%s ctermfg=lightred ctermbg=%s', bg, bg)
        let tal .= (tn==curr?'':'%#ct'.bg.'#%  '.tn).'%#c'.(tn==curr?'c':bg).'#%  '.join(fname,'|').' '
    endfor
    let tal .= "%#TabLine#%="
    " running indicators
    let tal .= "%#error#%{g:asyncCnt > 0 ? '  '.g:asyncCnt.' ':''}".(g:asyncrun_status!='success'?g:asyncrun_red[g:asyncrun_status]:'')
    let tal .= "%{gutentags#statusline() == '' ? '' : ' 󱈢 '}"
    if g:refreshFlag == 1 | let tal .= "%#CSInfo#%{'[󱦟'.(empty(g:pathQueue) ? ']' : ' '.len(g:pathQueue).']')}" | en
    let tal .= "%#CSInfo#".(g:asyncrun_status=='success' ? '  ':'')
    let tal .= "%#Git#%{FugitiveStatusline()}"
    let tal .= "%#Trans#%{g:TransMode}%{g:jpIme||g:cnIme ? '  󰗊 ' : ''}"
    let tal .= "%#PreferLang#%{g:pLang}"
    let tal .= "%#Obss#%{ObsessionStatus()}"
    retu tal
endfu
set tal=%!ActTal()

" Buffers
nn ,b :cal ClearNoName()\|cal fzf#vim#buffers({}, 1)<CR>
vn ,b :cal ClearNoName()\|cal fzf#vim#buffers(Selected(), {}, 1)<CR>
nn ,db :cal fzf#run({'source': GetBufFilePath(v:false), 'sink': 'bd', 'options':['-m', '--reverse', '--prompt=delete buf > ']})<cr>

" Shortcuts
"   execute current line as bash cmd ('e' for 'execute')
nn ,E :.w !bash<CR>
vn ,E :.w !bash<CR>
"   turn off highlight
nn <silent> <C-l> :<C-u>noh<CR><C-l>
"   quick to command (using ' for cover ; original function)
nn ; :
nn q; q:
xn ; :
nn ' ;
"   moving a line up or down
nn <a-u> ddp
nn <expr> <a-i> (line('$') == line('.') \|\| line('.') == 1) ? 'ddP' : 'ddkP'
"   file operations
nn ,q @=((expand('%')=='')?':quit!':((&mod==0)?':quit':':echo"Not Saved"'))<CR><CR>
nn ,Q :quita!<CR>
nn ,w @=(&ft == 'qfedit' ? ':cal ReflectAll()' : ':update')<CR><CR>
ca qa sil cal ClearTmpBuf() \| qall
"   surround operations ('s' for surround, 'S' for remove surround)
nn s :set opfunc=SurroundOp<cr>g@
vn s :<c-u>cal SurroundOp(visualmode())<cr>
nn S :cal DeSurroundOp()<cr>
"   change current letter by its next (for quick fix misspell)
nn <expr> <BS> col(".") == (col("$")-1) ? 'xP' : 'xhP'
"   replace content
nn <leader>r r
nn <silent> r :let b:reg_name = v:register<cr>:set opfunc=ReplaceOp<cr>g@
nn <silent> ,r :set opfunc=ReplaceOpFzf<cr>g@
nm <silent> rr Vr
vn <leader>r r
vn r :<c-u>let b:reg_name = v:register<cr>:cal ReplaceOp(visualmode())<cr>
vn ,r :cal ReplaceOpFzf(visualmode())<cr>
"   fzf commands
nn ,c :Commands!<cr>
"   compensate for Visual Edition
nn D Dh
"   quick to command, line macro need of visual selection
vn ,q :norm! @
"   leave current window open
nn <leader>n :only<CR>
nn <leader>N :cal CloseTab()<CR>
fu! CloseTab()
    echoh MoreMsg | echo '[h]left [o]ther [l]right' | echoh None
    let op = nr2char(getchar())
    if op ==# 'o'
        tabonly
    elseif op ==# 'h'
        while tabpagenr() != 1 | -tabc | endwhile
    elseif op ==# 'l'
        while tabpagenr() != tabpagenr('$') | +tabc | endwhile
    endif
endf
" quick commands
ca su %!sort -u
"   quick for register
map - "_
nn x "_x
nn <silent> K @=(index(['ark','text'],&ft)>=0?':cal Wiki(expand("<cword>"))':(&ft=='vim'?'K':':cal Google(&ft." ".expand("<cword>"))'))<CR><CR>
nn gl :cal LspAction()<CR>
fu! LspAction()
    let prefix = 'vim.lsp.buf.'
    let actTable = { 'a':'code_action', 'd':'definition', 'k':'hover', 'i':'implementation', 'r':'references', 'n':'rename', }
    let infoList = values(map(copy(actTable), {k,v -> k..':'..v}))
    echom reduce(infoList, {acc,val -> acc..' '..val}, '')
    let actChar = nr2char(getchar()) " wait for a action char
    if has_key(actTable, actChar)
        let cmd = 'lua '.prefix.actTable[actChar]."()"
        cal execute(cmd)
    en
endf
nn gt :cal GoToTag('e', expand("<cword>"))<cr>
fu TagRender(edit, tag)
    let [cmd, fn, kind] = [a:tag['cmd'], a:tag['filename'], a:tag['kind']]
    let relPath = RelPath(fn, getcwd())
    if RelPath(expand('%:p'), getcwd()) == relPath
        retu ':norm '.cmd.'gg " current - '.kind " tag in current file
    el
        retu printf('%s +%d %s " %s', a:edit, cmd, relPath, kind)
    en
endf
fu! GoToTag(edit, query)
    let tagExp = '\v(^'.a:query.'$)' "use strict match
    let tags = taglist(tagExp)
    let entries = map(tags, {_,tag -> TagRender(a:edit, tag)})
    cal fzf#run({'source':entries, 'sink':function('execute'), 'options':g:MfzfOpts})
endfu
" Toggle
fu! ToggleAll()
    echoh MoreMsg | echo '[C]ontext [B]lankChar auto[I]ndent [H]orizonCursor [A]wkShadow [R]ainbowBacket' | echoh None
    let ch = nr2char(getchar())
    if ch == 'c' | sil exe ':cal SignMarks()|ContextToggle'| en
    if ch == 'b' | exe ':setl '.(&list == 1 ? 'nolist' : 'list') | en
    if ch == 'h' | exe (&cuc == 1 ? 'setl nocuc' : 'setl cuc') | en
    if ch == 'r' | exe 'RainbowToggle' | en
    if ch == 'i'
        let g:autoIndentFlg = (g:autoIndentFlg == 1 ? 0 : 1)
        echo 'auto indent '.(g:autoIndentFlg == 1 ? 'ON' : 'OFF')
    endif
    if ch == 'a'
        let [g:awk_file, g:awk_shadow] = ['~/.config/nvim/awk-'.(g:awk_shadow ? 'template' : 'shadow').'.awk', !g:awk_shadow]
    endif
endf
nn <f2> :cal ToggleAll()<cr>

" Repeat Enhance
nn <leader>; :History!:<CR>
nn <leader>/ :History!/<CR>

" Marks
fu! EnhancedMark() abort
    let availMark = ''
    let usedLocal = map(getmarklist(bufnr()), {_, v -> v['mark'][1]})
    let usedGobal = map(getmarklist(), {_, v -> v['mark'][1]})
    for ch in extend(copy(g:alphabet), g:ALPHABET)
        if index(usedLocal, ch) < 0 && index(usedGobal, ch) < 0
            let availMark .= ch.' '
        en
    endfor
    echoh MoreMsg | echo availMark | echoh None
    let markId = getchar()
    let markChar = nr2char(markId)
    if markChar !~ '[a-z ]'
        retu
    elseif markId == 32 " blank space for next available mark
        let [markId, markChar] = [char2nr(availMark[0]), availMark[0]]
    elseif index(usedGobal, markChar) >= 0
        cal sign_unplace('marks', {'id':markId})
    en
    sil exe 'sil norm! m'.markChar
    cal sign_define('mark'.markChar,{'text':'󰈿'.markChar,'texthl':'QuickScopePrimary'})
    cal sign_place(markId, 'marks', 'mark'.markChar, bufnr(), {'lnum':line('.'),'priority':70})
    cal SignMarks()
endf
nn m :cal EnhancedMark()<CR>
" Encodings
ca jis e ++enc=ms932
ca dos e ++ff=dos
ca jdos e ++enc=sjis ++ff=dos
" }}}
" => plugins --------------------------- {{{
cal plug#begin('~/.vim/plugged')

    " Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
    Plug 'SirVer/ultisnips'
    Plug 'preservim/vim-pencil'
    Plug 'itchyny/vim-cursorword'
    Plug 'machakann/vim-highlightedyank'
    Plug 'voldikss/vim-floaterm'
    Plug 'preservim/tagbar'
    Plug 'ryanoasis/vim-devicons'
    Plug 'andymass/vim-matchup'
    Plug 'ap/vim-css-color'
    Plug 'gelguy/wilder.nvim', { 'do': ':UpdateRemotePlugins' }
    Plug 'ggandor/leap.nvim'
    Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
    Plug 'junegunn/fzf.vim'
    Plug 'junegunn/vim-easy-align'
    Plug 'kana/vim-textobj-user'
    Plug 'kevinhwang91/nvim-bqf'
    Plug 'ludovicchabant/vim-gutentags'
    Plug 'mattn/emmet-vim'
    Plug 'maxmellon/vim-jsx-pretty'
    Plug 'mbbill/undotree'
    Plug 'mechatroner/rainbow_csv'
    Plug 'mfussenegger/nvim-jdtls'
    Plug 'mhinz/vim-signify'
    Plug 'neovim/nvim-lspconfig'
    Plug 'pangloss/vim-javascript'
    Plug 'preservim/nerdtree'
    Plug 'rafaqz/ranger.vim'
    Plug 'rhysd/git-messenger.vim'
    Plug 'skywind3000/asyncrun.vim'
    Plug 'tpope/vim-characterize'
    Plug 'tpope/vim-commentary'
    Plug 'tpope/vim-fugitive'
    Plug 'tpope/vim-jdaddy'
    Plug 'tpope/vim-obsession'
    Plug 'tpope/vim-sleuth'
    Plug 'tpope/vim-scriptease'
    Plug 'unblevable/quick-scope'
    Plug 'wellle/context.vim'
    Plug 'wellle/targets.vim'
    Plug 'williamboman/nvim-lsp-installer'
    Plug 'yuezk/vim-js'
    Plug 'luochen1990/rainbow'

cal plug#end()
" }}}
" => Plugin-configs -------------------- {{{
" commentary
au VimEnter * if exists('*commentary')|unmap gcc|en
nn gc :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr><Plug>Commentary
nn gC :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>:set opfunc=ReverseCommentOp<cr>g@
vn gC :cal ReverseCommentOp(visualmode())<cr>
fu! ReverseCommentOp(type) " comment uncommented line and uncomment commented line
    let [smark, emark] = ["[", "]"]
    if a:type ==# 'V' || a:type ==# 'v'
        let [smark, emark] = ["<", ">"]
    endif
    let [startLn, endLn] = [nvim_buf_get_mark(0, smark)[0], nvim_buf_get_mark(0, emark)[0]]
    cal execute(':'.startLn) " move to start line
    while startLn <= endLn
        exec 'norm ' . (startLn == endLn ? 'gcl' : 'gclj')
        let startLn += 1 " comment each line
    endwhile
endfu
" emmet
let g:user_emmet_install_global = 0
let g:user_emmet_leader_key = '<c-y>'
" nerdtree
ca tf NERDTreeFind
" fzf.vim
let $FZF_DEFAULT_OPTS='--no-preview -0'
let g:fzf_preview_window = []
hi Purple ctermfg=135 ctermbg=none
let g:fzf_colors = {'hl':['fg', 'Purple'], 'hl+':['fg', 'Purple']}
let g:MfzfOpts = ['-1', '-m', '-i', '--reverse',]
" ultisnips
fu! UltiExpand(fromVisual)
    let [snips, query] = [UltiSnips#SnippetsInCurrentScope(1), '']
    if a:fromVisual == 1
        let Sink = {snip -> execute('norm! gv"_c'.split(snip, "	")[0]."\<c-r>=UltiSnips#ExpandSnippet()\<cr>")}
    el
        let query = expand("<cword>")
        let Sink = {snip -> execute('norm! "_ciw'.split(snip, "	")[0]."\<c-r>=UltiSnips#ExpandSnippet()\<cr>")}
    en
    cal fzf#run(extend(FzfFloatWin(), {'source': values(map(snips, {k,v -> k."	".v})), 'sink': Sink, 'options':['-1', '-i', '--query='.query]}))
endf
let g:UltiSnipsExpandTrigger="<c-x><c-j>"
let g:UltiSnipsJumpForwardTrigger="<c-k>"
let g:UltiSnipsJumpBackwardTrigger="<c-j>"
ino <a-l> <esc>:cal UltiExpand(0)<cr>
let g:UltiSnipsSnippetDirectories=["UltiSnips", "mycoolsnippets"]
let g:UltiSnipsEditSplit="context"
vn <c-l> :cal UltiSnips#SaveLastVisualSelection()<cr>:cal UltiExpand(1)<cr>
nn <silent> <f4> :UltiSnipsEdit<cr>
nn <silent> ,<f4> :UltiSnipsEdit!<cr>
let g:snipsMk = nvim_create_namespace('snippetMarks')
hi SnipMark cterm=bold ctermfg=227
hi SnipAnon cterm=bold ctermfg=198
hi CompleteFun cterm=bold ctermfg=154
let [g:exAnonExpand, g:expandingId, g:canSnipExpand] = ['', 0, v:false]
fu! SnipScope(timer)
    cal DelLineExtMark(g:snipsMk, 0, -1)
    if mode() != 'i' | retu | en
    if UltiSnips#CanExpandSnippet()
        let [snips, g:canSnipExpand] = [UltiSnips#SnippetsInCurrentScope(), v:true]
        let txt = join(values(map(snips, {_,v -> '󰧼 '.v})), ' ')
        cal nvim_buf_set_extmark(bufnr(), g:snipsMk, line(".")-1, 0, { "virt_text":[[txt, 'SnipMark']], "hl_mode":"combine" })
    el | let g:canSnipExpand = v:false | en
    let txt = AnonExpand()
    if txt != ''
        let start = virtcol('.') - len(InsertingWord()) - 1
        let mark = (g:jpIme ? '󰗊 ' : '󰧻 ') . txt
        cal nvim_buf_set_extmark(bufnr(), g:snipsMk, line(".")-1, 0, { "virt_text":[[mark, 'SnipAnon']], "hl_mode":"combine" }) | en
endf
let g:snipScopeTimer = timer_start(100, 'SnipScope', {'repeat': -1})
au InsertEnter * let g:exAnonExpand = '' | cal timer_pause(g:snipScopeTimer, 0)
au InsertLeave * cal timer_pause(g:snipScopeTimer, 1)
au InsertLeave * cal DelLineExtMark(g:snipsMk, 0, -1)
au CursorMovedI * cal timer_start(100, 'AnonRefresh')
fu! s:GetExpanded(jobId, data, event) abort
    if a:jobId == g:expandingId
        let g:exAnonExpand = a:data[0] | endif
endf
fu! InsertingWord()
    let frontText = getline('.')[:col('.')-2]
    if !g:jpIme && !g:cnIme
        if &ft == 'vim'
            retu trim(matchstr(frontText, '[-&:[:ident:]]*$'))
        elseif &ft == 'c'
            retu trim(matchstr(frontText, '[-:[:ident:]]*$'))
        else
            retu trim(matchstr(frontText, '[-&[:ident:]]*$'))
        endif
    else
        if frontText[len(frontText)-1] =~ '\C[a-z]'
            retu trim(matchstr(frontText, '\.\?[-/[:lower:]]*$'))
        else " do not involve Japanese characters
            retu trim(matchstr(frontText, '[\x00-\x1F\x21-\x7F]*$'))
        endif
    en
endf
fu! AnonRefresh(timer)
    let cw = InsertingWord()
    if cw == '' | retu | en
    let cmd = g:jpIme ? ("~/.config/nvim/romaji_hirakana '".substitute(cw, '^\\', '', '')."'") : printf('~/.config/nvim/anon_expand %s %s %s', cw, &ft, expand('%:t'))
    let g:expandingId = jobstart(cmd, {'on_stdout': function('s:GetExpanded'), 'stdout_buffered':v:true})
endf
fu! AnonExpand() " Anon Expand: regex match and regex replace and expand!
    if g:exAnonExpand != '' | retu substitute(g:exAnonExpand, '<cr>', "\<cr>", 'g') | en
    retu ''
endf
" leap.nvim
nn <leader>f :lua require('leap').leap{ target_windows = { vim.fn.win_getid() } }<cr>
hi LeapLabel cterm=bold ctermfg=red ctermbg=none
" quick-scope
let g:qs_highlight_on_keys = ['f', 'F', 't', 'T']
hi QuickScopePrimary ctermfg=red
hi QuickScopeSecondary ctermfg=91
" vim-matchup
let g:matchup_matchparen_offscreen = {}
let g:matchup_matchparen_enabled   = 0
" context.vim
let g:context_enabled = 0
" fugitive
let g:fugitive_no_maps = 1
ca gi Git<cr>
ca gl tab Git log -n 500 --pretty=tformat:"commit %H%d%nparent %P%nauthor %an <%ae> %ci%n%n%B" --author-date-order --abbrev=40
ca glg tab Git log -n 100 --graph --pretty='%H %s %d %ad %ae' --date=short --author-date-order
ca glga tab Git log -n 100 --graph --pretty='%H %s %d %ad %ae' --date=short --all --author-date-order
ca glp tab Git log -p -- %
ca gb tab Git branch
ca gbd cal fzf#run({'source':'git branch', 'dir':expand('%:p:h'), 'sink':{gb->execute('Git branch -d '.gb)}, 'options':extend(copy(g:MfzfOpts), ['--prompt=delete branch > ']), })<cr>
ca gc Git commit
ca gca Git commit --amend<cr>
ca gco cal fzf#run({'source':'git branch', 'dir':expand('%:p:h'), 'sink':{gb -> execute('Git checkout '.gb)}, 'options':extend(copy(g:MfzfOpts), ['--prompt=checkout > ']), })<cr>
ca gch Git checkout
ca gm Git merge
ca gcmt Git blame --date=format-local:'%Y/%m/%d %H:%M:%S'
ca gpl AsyncRun -cwd=<C-R>=expand('%:p:h')<CR> git pull origin <c-r>=fugitive#Head(0,FugitiveGitDir())<CR>
ca gps AsyncRun -cwd=<C-R>=expand('%:p:h')<CR> git push origin <c-r>=fugitive#Head(0,FugitiveGitDir())<CR>
" vim-easy-align
xn g= <Plug>(EasyAlign)
nn g= :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr><Plug>(EasyAlign)
let g:easy_align_delimiters = {
            \ '>': { 'pattern': '>>\|=>\|>' },
            \ '/': { 'pattern': '//\+\|/\*\|\*/', 'delimiter_align': 'l', 'ignore_groups':   ['!Comment'] },
            \}
" wilder.nvim
call wilder#setup({'modes': [':', '/']})
call wilder#set_option('renderer', wilder#popupmenu_renderer({ 'highlighter': wilder#basic_highlighter(), }))
" Gutentags
let g:gutentags_ctags_extra_args = ['-n']
" Undotree
set udf
let g:undotree_WindowLayout=2
let g:undotree_ShortIndicators=1
let g:undotree_SetFocusWhenToggle=1
let g:undotree_HelpLine=0
fu g:Undotree_CustomMap()
    nmap <buffer> k     <plug>UndotreeNextState
    nmap <buffer> j     <plug>UndotreePreviousState
    nmap <buffer> K     <plug>UndotreeNextSavedState
    nmap <buffer> J     <plug>UndotreePreviousSavedState
    nmap <buffer> <c-k> <plug>UndotreeRedo
    nmap <buffer> <c-j> <plug>UndotreeUndo

    nmap <buffer> h     <plug>UndotreeTimestampToggle
    nmap <buffer> l     <plug>UndotreeFocusTarget
endf
nn <leader>u :UndotreeToggle<cr>
" devicons
let g:webdevicons_enable_nerdtree = 1
" HighlightedYank
let g:highlightedyank_highlight_duration = 150
hi HighlightedyankRegion ctermbg=191
" asyncrun.vim
let g:asyncrun_open=8
fu! AsyncRunPost()
    if g:asyncrun_status == 'failure' | copen | wincmd w | en
    if g:texCompilePending == 1
        exe printf('AsyncRun xelatex --jobname=%s.tmp %s', expand('%:r'), expand('%:p'))
        let g:texCompilePending = 0
    endif
    if match(g:asyncrun_info, '^xelatex') >= 0 && g:asyncrun_status == 'success' " set tmp.pdf to real pdf
        let target_path = split(g:asyncrun_info)[2]
        exe printf('!mv %s.tmp.pdf %s.pdf', fnamemodify(target_path, ':p:r'), fnamemodify(target_path, ':p:r'))
    en
    redrawt
endf
au User AsyncRunStop :cal AsyncRunPost()
" vim-floaterm
tmap ,q jk:quit<cr>
tmap <F3> jk:FloatermNext<cr>
" text-object
call textobj#user#plugin('calling', { 'calling': { 'pattern': '\<\w*[\./@]\w*\>', 'select': ['v'], },})
" rainbow
let g:rainbow_conf = {
            \	'ctermfgs': ['lightblue', 'lightyellow', 'lightgreen', 'lightcyan', 'lightmagenta'],
            \	'operators': '',
            \	'parentheses': ['start=/(/ end=/)/ fold', 'start=/\[/ end=/\]/ fold', 'start=/{/ end=/}/ fold'],
            \}
" }}}
" => File type Specific -------------------- {{{
aug filetypes
    " au BufReadPost * if line("'\"") <= line('$') | sil norm! g`"

    au BufRead *.la,*.gr set ft=ark
    au BufRead *.ztool set ft=ztool
    au BufRead *.tex set ft=tex

    au FileType text setl wrap noai sw=2 fdm=expr fde=getline(v:lnum)=~'^\\s*$'&&getline(v:lnum+1)=~'\\S'?'<1':1
    au FileType text,ark :let g:TransMode=GetDefault(g:TransMode, 'Latin')
    au FileType text,ark :let g:WikiTag=GetDefault(g:WikiTag, '\#English')
    au FileType fzf setl nonu nornu
    au FileType javascript,tex setl ts=2 sw=2
    au FileType vim setl tw=0
    au FileType html,javascript,css,xml :EmmetInstall
    au FileType python,vim,c setl ofu=v:lua.vim.lsp.omnifunc
    au FileType git setl fdm=syntax fdl=0
    au FileType sql setlocal commentstring=--\ %s
    " au BufWritePre * :sil! ClearTailBlank
    " auto save file to OneDrive
    au BufWritePost init.vim sil exe ':!cp ~/.config/nvim/init.vim ~/OneDrive'
    au BufWritePost *.tex cal CompileTex()
    au BufRead targets.txt,history.txt let g:pLang='de'
aug END
" }}}
" => Functions -------------------- {{{
com! -nargs=0 CTailBlank :%s/\s\+$//
com! -nargs=0 CHeadBlank :%s/^\s\+//
com! -nargs=0 CBlank :exe (IsDyBuf() ? printf("!sed -i '/^$/d' %s", b:dy_file) : printf("%%!awk '{$1=$1};1'"))
com! -nargs=0 CEmptyLine :exe printf("%%!awk '\\!/^%s$/ {print}'", (&ff == 'dos' ? "\\r" : ""))
com! -nargs=0 Ztool :e ~/desktop/tool.ztool

fu AutoSetWindowWidth()
    norm mzH
    let hln = line('.')                         " head line number
    let tln = line('.') + winheight(0) - 1      " tail line number
    let cmd = 'sed -n '.hln.','.tln.'p '.expand('%').' | wc -L'
    exe ':vert res ' . (str2nr(system(cmd)) + 5)
    norm `z
    execute('DMarks z')
endf
com! -nargs=0 AuWidth :cal AutoSetWindowWidth()
com! -nargs=0 AuHeight exe ':res '.line('$')

fu! OmniTranslit(fname, fargs, content)
    if a:fname == '' | retu a:content | en
    let TransFn = function(a:fname, a:fargs)    " tune the trans func first
    retu TransFn(a:content)                     " return transliterated
endf
fu! Selected() " get visual selected content
    exe 'norm! `<v`>"vy'
    retu @v
endf
fu! GetBufFilePath(withEncoding) " return a list
    if a:withEncoding == v:false
        retu map(filter(range(1,bufnr('$')), 'buflisted(v:val) && filereadable(bufname(v:val))'), 'fnamemodify(bufname(v:val), ":p")') | en
    retu map(filter(range(1,bufnr('$')), 'buflisted(v:val) && filereadable(bufname(v:val))'), 'fnamemodify(bufname(v:val), ":p").":".getbufvar(v:val, "&encoding")')
endf
fu! GetDefault(v, default)
    if empty(a:v) | retu a:default
    el | retu a:v
    en
endf
fu! CompileTex()
    if g:asyncrun_status != 'running'
        exe printf('AsyncRun xelatex --jobname=%s.tmp %s', expand('%:r'), expand('%:p'))
    else
        let g:texCompilePending = 1 | en
endf
fu! QuickRun()
    if &ft == 'vim' | so %
    elseif &ft == 'tex' | cal CompileTex()
    elseif &ft == 'python' | :!python3 %
    elseif &ft == 'c' | :silent !cc %
    elseif expand('%:p') == trim(system('realpath '.g:db_script)) | cal RunDb()
    en
    do User UserQuickRun
endf
nn <silent> <f5> :cal QuickRun()<cr>
fu! ClearNoName() abort
    for buf in getbufinfo()
        if bufname(buf.bufnr) == '' && buflisted(buf.bufnr) == 1 | sil exe 'bd'.buf.bufnr | en
    endfor
endf
fu! ClearTmpBuf()
    if exists('g:roadmapbuf') | sil exe 'bd! '.g:roadmapbuf | en
    for buf in getbufinfo()
        let path = expand('#'.buf.bufnr.':p')
        if match(path, '^/tmp/nvim') >= 0 || match(path, '^man://') >= 0
            sil exe 'bd! '.path | en
    endfor
endf
au ExitPre * sil cal ClearTmpBuf() | cal ClearNoName()
fu! RelPath(path, anchor) " return relative path
    if a:path == '' | retu '' | en
    retu trim(system('realpath '.a:path.' --relative-to '.a:anchor))
endf
fu! VirtualMarkWrapper(ln, col, txt, hl)
    if a:ln+1 > 0 && a:ln+1 <= line('$')
        cal nvim_buf_set_extmark(bufnr(''), g:vertLineMark, a:ln, 0, {
                    \ "virt_text":[[a:txt, a:hl]],
                    \ "virt_text_win_col": a:col, })
    en
endf
fu Cap(word) " Capitalize first letter
    retu substitute(a:word, '^.', '\u&', '')
endfu
fu! GetAllExmarks()
    let marks = []
    for bn in filter(range(1,bufnr('$')), 'buflisted(v:val) && filereadable(bufname(v:val))')
        for mkinfo in nvim_buf_get_extmarks(bn, g:extmk, 0, -1, {})
            let [ln, txt] = [mkinfo[1] + 1, nvim_buf_get_extmark_by_id(bn, g:extmk, mkinfo[0], {'details':v:true})[2]['virt_text'][0][0]]
            let lnTxt = getbufline(bn, ln)[0]
            cal add(marks, printf('+%d %d %s | %s', ln, bn, Shortf(bufname(bn)), trim(lnTxt . ' ' . txt)))
        endfor
    endfor
    retu marks
endf

" ----------------- Operator Functions -----------------
" Replace-Operator
fu! ReplaceOpFzf(type)
    let Sink = {t -> execute(['let @" = "'.t.'"', "let b:reg_name='".'"'."'", "cal AddYankHist(getreg('".'"'."'))" , 'cal ReplaceOp("'.a:type.'")'])}
    cal fzf#run(extend({ 'sink': Sink }, FzfFloatWin()))
endf
fu! ReplaceOp(type)
    if a:type ==# 'v'
        exe printf('norm! `<v`>"_d"%sP', b:reg_name)
    elseif a:type ==# 'char'
        exe 'norm! mz'
        exe printf('norm! `[v`]"_d"%sP', b:reg_name)
        sil exe 'norm! `z'
        sil cal execute('DMarks z')
    elseif a:type ==# 'V'
        exe printf('norm `<V`>"_d"%sP', b:reg_name)
    elseif a:type ==# 'line'
        exe printf('norm `]$v`[0"_d"%sP', b:reg_name)
    en
endf
" Surround-Operator
fu! SurroundOp(type)
    let start = nr2char(getchar()) " wait for a char to surround
    let end = get({'(':')','[':']','{':'}','<':'>'}, start, start)
    if start =~ "\<esc>" || start =~ "\<c-c>" | retu | en
    if a:type ==# 'v'
        exe printf("norm! `>a%s\<esc>`<i%s", end, start)
    elseif a:type ==# 'char' || a:type ==# 'line'
        if start == "\<CR>" " surrounded by carriage return
            exe printf("norm! `[v`]\"sc%s%s\<esc>k\"sP", start, end)
        else
            exe printf("norm! `[v`]\"sc%s%s\<esc>\"sP", start, end)
        en
    en
    exe 'norm! `<'
endf
fu! DeSurroundOp()
    let [lpairs, rpairs] = [{'(':')','[':']','{':'}'}, {')':'(',']':'[','}':'{'}]
    let quotes = {'"':'"', "'":"'", '<':'>', '`':'`', '_':'_'}
    let curr_ch = matchstr(getline('.'), '\%'.col('.').'c.')
    if has_key(lpairs, curr_ch)
        exe 'norm! mz%x`zx'
    elseif has_key(rpairs, curr_ch)
        exe 'norm! %mz%x`zx'
    el
        exe 'norm! mzxf'.get(quotes, curr_ch, curr_ch).'x`z'
    en
    execute('DMarks z')
endf
" -------------------- Convert ----------------------
" CamelCase under_scores operator
fu! CaseConvert(content)
    let converted = match(a:content, '_\([A-Z]\)') >= 0 ? tolower(a:content) : a:content
    if match(a:content, '_\([a-z]\)') >= 0 " u2c
        retu substitute(converted, '_\([a-z1-9]\)', '\u\1', 'g')
    elseif match(a:content, '\(\u\?\l\+\)\(\u\)') >= 0 " c2u
        retu substitute(converted, '\(\u\?\l\+\)\(\u\)', '\l\1_\l\2', 'g')
    el
        retu tolower(converted)
    en
endf
fu! CaseConvertOp(type)
    exe 'norm! mz`[v`]"vy'
    exe 'norm! `[v`]"_c' . CaseConvert(@v) ."\<esc>`z"
    execute('DMarks z')
endf
nn <silent> ,,<tab> :set opfunc=CaseConvertOp<cr>g@
vn <silent> ,,<tab> c<C-R>=OmniTranslit('CaseConvert', [], '<C-R>-')<CR><ESC>

" -------------------- Web Search ----------------------
fu! WebSearch(content, url, escapeMap, postOnlyFlg)
    let resultTarget = ''
    for ch in split(a:content, '\zs')
        let resultTarget .= get(a:escapeMap, ch, ch)
    endfor
    if a:postOnlyFlg == 0
        exe 'sil !msedge.exe '. a:url . resultTarget . ' &' | redraw!
    else
        echo 'open only by PostWebSearch'
    endif
    let g:LastWebSearchURL = substitute(a:url . resultTarget, ' ', '%20', 'g')
    do User PostWebSearch
endf

let g:WikiTag = ''
fu! Wiki(word, ...)
    let esMap = {'ā':'a','ē':'e','ī':'i','ū':'u','ō':'o','ᾱ':'α','ῡ':'υ','ῑ':'ι','ȳ':'y'}
    cal WebSearch(get(a:, 1, a:word) . g:WikiTag, 'https://en.wiktionary.org/wiki/', esMap, 0)
endf
fu! Google(content, ...)
    let esMap = {' ':'\ '}
    let q = len(a:000) == 0 ? a:content : join(a:000, ' ')
    cal WebSearch(q, 'https://www.google.com/search\?q=', esMap, 0)
endf

for site in ['Wiki', 'Google'] "  if no arg is given, then search current word
    exe printf('com! -nargs=* %s cal %s(expand("<cword>"), <f-args>)', site, site)
    exe printf('com! -nargs=0 -range %sv cal %s(Selected())', site, site)
endfor
" -------------------- Greek Misc ----------------------
fu! Greek(content)
    retu system("~/OneDrive/greek/translator.py '" . a:content . "'")
endf
fu! Latin(content)
    if len(a:content) == 0 | retu '' | en
    cal digraph_set('s-', 'ß')
    let rst = ''
    for ch in a:content
        if index(['-', ':', "'"], ch) >= 0 && !empty(rst) && match(rst[-1:-1], '\h') >= 0
            let [last, rst] = [rst[-1:-1], rst[:-2]]
            let rst .= digraph_get(last.ch)
        el
            let rst .= ch
        en
    endfor
    retu rst
endf
fu! GrTransOp(type) " operator needs a type arg
    exe 'norm! `[v`]"vy`[v`]"_c'.Greek(@v)
endf

" nn <silent> ,<tab> :set opfunc=GrTransOp<cr>g@
" replace in visual: c for change <C-R> for get output from = register
vn <silent> ,<tab> c<C-R>=OmniTranslit('Greek', [], '<C-R>-')<CR><ESC>

fu! IndoEuropeanFZF()
    let reload_cmd = printf('~/OneDrive/lat-locator.sh %s || true', '{q}')
    let spec = {'options': ['--phony', '--bind', 'change:reload:'.reload_cmd]}
    cal fzf#vim#grep('echo "type to search"', 1, spec, 1)
endf
let [g:transCache, g:TransMode, g:pLang] = ['', '', ''] " pLang for prefer language
fu! TranslitMode()
    hi CursorLine ctermbg=31 | redraw | let ch = getchar()
    if ch == 27 || (g:transCache[-1:-1] == 'j' && ch == 107) " ESC
        hi CursorLine cterm=NONE ctermbg=DarkGray
        cal ClearVirtualTxt() | let g:transCache = '' | retu
    elseif ch == "\<BS>" && len(g:transCache) > 0            " backward
        let g:transCache = g:transCache[:-2]
    elseif nr2char(ch) == "\<CR>" || nr2char(ch) == "\<tab>" " complete
        let g:transCache = ''
        cal nvim_put([getreg('"')], "c", 0, 1)
        hi CursorLine cterm=NONE ctermbg=DarkGray | retu
    el                                                     " feed to Greek cache
        let g:transCache .= nr2char(ch)
        cal setreg('"', OmniTranslit(g:TransMode, [], g:transCache)) " save temporary
    en
    cal ClearVirtualTxt()
    cal VirtualMarkWrapper(line('.')-1, virtcol('.')-1, OmniTranslit(g:TransMode, [], g:transCache), 'Search')
    redraw | cal TranslitMode()
endf
nn <silent> ,<tab>i :cal TranslitMode()<CR>
nn <silent> ,<tab>o o<esc>:cal TranslitMode()<CR>
nn <silent> ,<tab>l :let g:TransMode='Latin'<CR>
nn <silent> ,<tab>g :let g:TransMode='Greek'<CR>
ino <silent> jj <c-\><c-o>:let [g:jpIme,g:cnIme] = (g:jpIme == 1 ? [0,0] : [1,0])\|do User ImeChanged\|cal HlInsertRow()\|cal RefreshCandidates()<CR>
ino <silent> jc <c-\><c-o>:let [g:jpIme,g:cnIme] = (g:cnIme == 1 ? [0,0] : [0,1])\|do User ImeChanged\|cal HlInsertRow()\|cal RefreshCandidates()<CR>
im <silent><expr> <cr> (g:jpIme && complete_info().selected == -1) ? "<c-l>" : "<cr>"
fu! DeMarkAutoReplace()
    let currTwo = getline('.')[col('.')-3:col('.')-2]
    if currTwo == ' .' | cal nvim_feedkeys("\<BS>\<BS>.\<space>", "i", 1) | en
    if currTwo == ' ,' | cal nvim_feedkeys("\<BS>\<BS>,\<space>", "i", 1) | en
    if currTwo == ' ?' | cal nvim_feedkeys("\<BS>\<BS>?\<space>", "i", 1) | en
    if currTwo == ' !' | cal nvim_feedkeys("\<BS>\<BS>!\<space>", "i", 1) | en
endf
au TextChangedI * if g:pLang == 'de' | cal DeMarkAutoReplace() | en
" -------------------- Calc Misc -----------------------
fu! NumTrans(fmt, num)
    let fmtMap = {'x': '0x%X', 'b': '0b%08b', 'd': '%d'}
    retu printf(get(fmtMap, a:fmt, ''), a:num)
endf
vn <silent> <tab>nx c<C-R>=OmniTranslit('NumTrans', ['x'], '<C-R>-')<CR><ESC>
vn <silent> <tab>nb c<C-R>=OmniTranslit('NumTrans', ['b'], '<C-R>-')<CR><ESC>
vn <silent> <tab>nd c<C-R>=OmniTranslit('NumTrans', ['d'], '<C-R>-')<CR><ESC>
" evaluate expression and replace
nn <silent> ,e :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)\|set opfunc=EvalOp<cr>g@
nn <silent> ,,e :cal RenderVerticalScope(1,1,-1,virtcol('.')-1)\|set opfunc=EvalFeedOp<cr>g@
vn <silent> ,e <esc>gvc<c-r>=py3eval(substitute(getreg('"'), '\n', ' ', 'g'))<CR><esc><c-l>
fu! EvalOp(type)
    exec printf("norm! `]$v`[0d")
    cal setbufline(bufnr(), line('.'), [py3eval(substitute(getreg('"'), '\n', ' ', 'g'))])
endf
fu! EvalFeedOp(type) " feed variables
    exec printf("norm! `]$v`[0y")
    let code = "py3 \n" . getreg('"')
    exec code
endf
" ------------------- Windows Misc -----------------------
fu WinPath(mntPath) " convert wsl mnt path to windows path
    retu substitute(a:mntPath, '/mnt/\([a-zA-Z]\)', '\1:', '')
endf
com! -nargs=0 WSLview exe 'sil !wslview %'
" com! -nargs=0 Notepad exe 'sil !subl.exe -a '.WinPath(expand('%')).':'.line('.')
com! -nargs=0 Notepad exe 'sil !powershell.exe -Command "Start-Process notepad -WindowStyle Maximized '.WinPath(expand('%')).'"'
com! -nargs=0 Directory exe 'sil !explorer.exe /select,' . substitute(WinPath(expand('%:p')), '/', '\\\\', 'g')
com! -nargs=0 EdComplete e ~/.config/nvim/complete_service.py
com! -nargs=0 EdAnon tabe | e ~/.config/nvim/anon_expand.c
ca emk AsyncRun -cwd=~/.config/nvim ./compile.sh

vn <silent><leader>y <esc>:cal VisYankToWinClipboard()<cr>
fu! VisYankToWinClipboard()
    hi HighlightedyankRegion ctermbg=129
    norm! gv"+y
endf
fu! s:RecoverHl(jobId, data, event) abort
    hi HighlightedyankRegion ctermbg=191
endf
nn <silent><leader>y :hi HighlightedyankRegion ctermbg=129<cr>:cal RenderVerticalScope(1,1,-1,virtcol('.')-1)<cr>"+y
au TextYankPost * cal jobstart('sleep 0.5', {'on_exit':function('s:RecoverHl')})
nn ,<c-v> "+p
nn ,,<c-v> "+P
nmap ,R "+r
" ------------------- Latex Misc -----------------------
let g:PdfLoc = 1
fu! GetPdfLoc()
    let cmd = 'sed -n "1,'.line('.').'{/newpage/p}" '.expand('%:p')
    let rst = split(system(cmd), '\n')
    retu 1 + len(rst)
endf
com! -nargs=0 Pdf exe 'sil !SumatraPDF.exe -reuse-instance -page ' . GetPdfLoc() . ' ' . WinPath(substitute(expand('%:p'), '.tex$', '.pdf', ''))
com! -nargs=0 PdfLoc exe 'sil !SumatraPDF.exe -reuse-instance -page ' . g:PdfLoc . ' ' . WinPath(substitute(expand('%:p'), '.tex$', '.pdf', ''))
com! -nargs=0 EdTexMacros tabe | e ~/.config/nvim/tex/zzmakros.sty
au BufWritePost zzmakros.sty cal system('cp ~/.config/nvim/tex/zzmakros.sty ~/texmf/tex/xelatex/')
" ------------------- Async Misc -----------------------
let g:texCompilePending = 0
"  qfSearchCmd { qfEntry : [jobId list] }
"  qfListTobe { jobId : [qfResult] }
"  let one qfEntry in qfSearchCmd hold multiple jobId
let [g:qfSearchCmd, g:qfListTobe] = [{}, {}]
let g:AutoPop = 1
fu! s:OnGetRst(jobId, data, event) dict " parse rg result line by line
    for ln in a:data
        let posInfo = matchstr(trim(ln), '^.*:\d*:\d*:')
        let blc = split(posInfo, ':') " Buf Ln Col
        let showTxt = substitute(trim(ln), posInfo, '', '')
        if (len(blc) > 0)
            let qfItem = [{'bufnr':bufnr(blc[0], 1), 'lnum':blc[1], 'col':blc[2], 'text': showTxt}]
            sil cal extend(g:qfListTobe[a:jobId], qfItem)
        en
    endfo
endf
fu! ComparePos(pl, pr)
    if a:pl['bufnr'] != a:pr['bufnr']
        retu a:pl['bufnr'] > a:pr['bufnr']
    elseif a:pl['lnum'] != a:pr['lnum']
        retu str2nr(a:pl['lnum']) > str2nr(a:pr['lnum'])
    elseif a:pl['col'] != a:pr['col']
        retu str2nr(a:pl['col']) < str2nr(a:pr['col']) " for result in same line, let cursor move right to left
    en
    retu 0
endf
fu! s:OnExit(jobId, data, event) abort " merge multiple rg result by qfEntry
    for [entry, jobIdLst] in items(g:qfSearchCmd) " search qfEntry by a:jobId
        if index(jobIdLst, a:jobId) >= 0
            let qfEntry = entry | break
        en
    endfor
    let tobeLists = {} " let same position (buf, ln, col) to be added once
    for jobid in g:qfSearchCmd[qfEntry]
        for pos in g:qfListTobe[jobid]
            let blc = join([pos['bufnr'], pos['lnum'], pos['col']], '-')
            let tobeLists = has_key(tobeLists, blc) ? tobeLists : extend(tobeLists, {blc:pos})
        endfor
    endfor
    cal setqflist(sort(values(tobeLists), function('ComparePos')))
    cal extend(g:qfHist, {qfEntry:getqflist()}) " save search result
    let g:asyncCnt -= 1
    if g:asyncCnt == 0 && g:AutoPop == 1 | copen | en
endf
let g:asynQfOpts = {'on_stdout': function('s:OnGetRst'), 'on_exit': function('s:OnExit')}
fu! AsyncSearch(target, cmdArgs, qfEntry)
    let g:asyncCnt += 1
    let jobId = jobstart(extend(['rg', '--vimgrep', '-i', '--hidden', a:target], a:cmdArgs), g:asynQfOpts)
    let g:qfListTobe[jobId] = [] " init qfList for this job id
    let g:qfSearchCmd[a:qfEntry] = has_key(g:qfSearchCmd, a:qfEntry) ? extend(g:qfSearchCmd[a:qfEntry], [jobId]) : [jobId]
endf
fu! Xearch(...) " bang, target, opts...
    let [g:qfSearchCmd, g:qfListTobe, bang, toSearch] = [{}, {}, a:000[0], a:000[1]]
    let paths = g:HRSmode==1 ? keys(extend({getcwd():1}, g:hda)) : [getcwd()]
    let qfEntry = (g:HRSmode==1?' ':'').'Xearch'.(bang?'! ':' ').toSearch.' '.join(a:000[2:], ' ')
    " search without border if bang or no-ASCII target
    let toSearch = (bang || match(toSearch, '[^\x00-\x7F]') >= 0) ? toSearch : '\b'.toSearch.'\b'
    let args = len(a:000) > 2 ? extend(paths, map(a:000[2:], {_,v -> '-t='.v})) : paths " add filetypes
    cal AsyncSearch(toSearch, args, qfEntry)
    if bang && (match(toSearch, '_\([a-zA-Z]\)') >= 0 || match(toSearch, '\(\u\?\l\+\)\(\u\)') >= 0) " u2c
        cal AsyncSearch(CaseConvert(toSearch), args, qfEntry)
    en
    if match(toSearch, '[^\x00-\x7F]') >= 0 " no-ASCII char
        cal AsyncSearch(toSearch, extend(args, ['--encoding=sjis']), qfEntry)
    en
endf
" }}}
exec 'so '.fnamemodify($MYVIMRC, ":p:h").'/hex_open.vim'
exec 'so '.fnamemodify($MYVIMRC, ":p:h").'/properties_open.vim'
exec 'so '.fnamemodify($MYVIMRC, ":p:h").'/rename_files.vim'
exec 'so '.fnamemodify($MYVIMRC, ":p:h").'/embed-sql.vim'
exec 'so '.fnamemodify($MYVIMRC, ":p:h").'/dynamic-read.vim'

" => LSP -------------------- {{{
lua << EOF
require("nvim-lsp-installer").setup {}
local lspconfig = require('lspconfig')
lspconfig.pyright.setup{}
lspconfig.html.setup{}
lspconfig.cssls.setup{}
lspconfig.vimls.setup{}
lspconfig.clangd.setup{}
lspconfig.texlab.setup{}
lspconfig.awk_ls.setup{}
EOF
" }}}
