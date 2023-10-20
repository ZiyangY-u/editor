" let d = {'true': 'false'}

" echo 'true'[0] =~ '\u'
"     for mark in filter(keys(g:hma), {mk -> split(mk)[0] == string(bufnr('%'))})
"         call matchadd('HMarks', '\%'.split(mark, '-')[1].'l')
"     endfor
" let lst = ['java', 'asp']
" echo map(lst, {_,v -> '--'.v})
" let test = {1: ['a', 'b', 'c'], 2:['d', 'e', 'f']}
" echo extend({1:'hello'}, test)
" echo test
" for pos in map(getqflist(), {_,v->v['bufnr'].' '.v['lnum'].' '.v['text']})
"     echo pos
" endfor
" let pos = getqflist()[0]
" echo pos
" fu! Locate(posInfo)
"     let [bn, ln] = [a:posInfo['bufnr'], a:posInfo['lnum']]
"     cal bufload(bn)
"     exe 'b'.bn.'|'.ln
" endfu
" か

" cal Locate(pos)
" com! -nargs=* TstCom :echo len(<q-args>)
" cal fzf#vim#buffers({}, 1)
" echo substitute('test_string_ab', '_\([a-z]\)', '\u\1', 'g')
" echo substitute('_string_ab', '_\([a-z]\)', '\u\1', 'g')
" echo substitute('testStringABCiO', '\(\u\?\l\+\)\(\u\)', '\l\1_\l\2', 'g')
" echo match('_a', '_\([a-z]\)')

" fu! ChainConvert(content, ...)
"     let rst = a:content
"     for fn in a:000
"         let ConvertFn = function(fn)
"         let rst = ConvertFn(rst)
"     endfor
"     return rst
" endfu

" echo ChainConvert('ABC_EFT', 'tolower', 'CaseConvert')
" set tal=something
" 1   2   3   4   5   6   7
" 1   6   11  16  21  26  31
"                 4   9   14  19   24
"                             2    7
" 1 + 5*(n-1) = 1 + 5n -5

" fu! ActTal()
"     let [tal, curr] = ['', tabpagenr()]
"     hi cc ctermfg=black ctermbg=lightgreen
"     for tn in range(1, tabpagenr('$'))
"         let bg = 256-((5*tn-4) % 24)
"         let fg = bg > 243 ? 'Black' : 'White'
"         exe 'hi c'.bg.' ctermfg='.fg.' ctermbg='.bg
"         let winIds = gettabinfo(tn)[0]['windows']
"         let bufnrs = uniq(map(winIds, {_,wi -> getwininfo(wi)[0]['bufnr']}))
"         let fname = map(bufnrs, {_,bn -> fnamemodify(bufname(bn), ':p:t')})
"         let tal .= '%#c'.(tn==curr?'c':bg).'#%  '.join(fname,'/').' '
"     endfor
"     let tal .= '%#TabLineFill#%'
"     retu tal
" endfu

" set tal=%!ActTal()
" let winIds = gettabinfo(1)[0]['windows']
" let bufnrs = map(winIds, {_,wi -> getwininfo(wi)[0]['bufnr']})
" " let fname = fnamemodify(bufname(bufnr), ':p:t')
" let fname = map(bufnrs, {_,bn -> fnamemodify(bufname(bn), ':p:t')})
" echo fname
" for tn in range(1, 20)
"     let bg = 256-((5*tn-4) % 17)
"     echo bg
" endfor

" echo luaeval('1+1')
" let l = ['xml', 'java']
" echo map(l, {_,v -> 't='.v})
" REMARK

" let markId = getchar()
" let markChar = nr2char(markId)
" if markId == 32
"     echo markId
" endif

" for mkInfo in nvim_buf_get_extmarks(bufnr(''), g:extmark_ns, [line('.')-1,0], [line('.')-1,0], {})
"     cal nvim_buf_get_extmark_by_id(mark_ns, mkInfo[0])
" endfor
" let f = split('abc.def', '\.')
" echo f[0]

" let list = UltiSnips#SnippetsInCurrentScope(1)
" echo keys(list)

" echo split('abc.def', '[\./]')
" highlight redbg ctermfg=black ctermbg=lightred
" highlight bluebg ctermfg=black ctermbg=lightblue
" highlight greenbg ctermfg=black ctermbg=230
" cal matchaddpos('redgb', [[line('.') - 9, getpos('.')[2]]])


" fun! ClearVirtScope()
"     for mkInfo in nvim_buf_get_extmarks(0, g:vertLineMark, 0, -1, {})
"         cal nvim_buf_del_extmark(0, g:vertLineMark, mkInfo[0])
"     endfor
" endf

" fu! RenderVirtScope()
"     let offset = 1
"     while offset <= winheight(0)
"         cal VertMarkWrapper(line('.')-offset-1, string(offset), 'QuickScopePrimary')
"         cal VertMarkWrapper(line('.')+offset-1, string(offset), 'QuickScopePrimary')
"         let offset += 1
"     endwhile
" endfu
" nn d :let b:reg_name = v:register<cr>:cal RenderVirtScope()<cr>@=('"'.b:reg_name.'d')<cr>
" nn y :let b:reg_name = v:register<cr>:cal RenderVirtScope()<cr>@=('"'.b:reg_name.'y')<cr>
" nn c :let b:reg_name = v:register<cr>:cal RenderVirtScope()<cr>@=('"'.b:reg_name.'c')<cr>
" nn = :cal RenderVirtScope()<cr>=
" au CursorMoved,TextChanged,InsertEnter,TextYankPost * sil cal ClearVirtScope()

" cal fzf#run({'source':'ls', 'sink':{arg->execute('echo '.'"'.arg.'"')}, 'options':['-m', '-i']})
" fun! EchoArgs(...)
"     echo a:000
" endf

" com! -bang -nargs=* TestBang :cal EchoArgs(<f-args>)

" highlight QuickMove cterm=bold ctermfg=red ctermbg=none
" fun! QuickMoveRender()
"     let marks = extend(map(range(char2nr('0'),char2nr('9')),'nr2char(v:val)'), ['[', ']', ';', "'", ',', '.', '/'])
"     let anchor = {}
"     let [idx, top, bot, mi] = [line('w0')+1, line('w0')+1, line('w$')+1, 0]
"     cal reverse(extend(extend(marks, g:ALPHABET), g:alphabet))
"     while idx <= bot && mi < len(marks)
"         let ci = min([indent(idx-1), indent(idx), indent(idx+1)])
"         let end = max([len(getline(idx-1)), len(getline(idx)), len(getline(idx+1))])
"         while ci < end && mi < len(marks)
"             cal VertMarkWrapper(idx-1, ci-1, marks[mi], 'QuickMove')
"             let anchor[marks[mi]] = [idx, ci]
"             let [ci, mi] = [ci + 18, mi + 1]
"         endwhile
"         let idx = idx + 3
"     endwhile
"     return anchor
" endf

" fun! QuickMove(anchor)
"     echoh MoreMsg | echo 'Type to move:' | echoh None
"     let anchorChar = nr2char(getchar()) " wait for a anchor char
"     if has_key(a:anchor, anchorChar)
"         cal cursor(a:anchor[anchorChar][0], a:anchor[anchorChar][1])
"     endif
" endf

" nn <silent> ,f :cal QuickMove(QuickMoveRender())<cr>
" nn <silent> ,f :let _a=QuickMoveRender()<cr>:cal QuickMove(_a)<cr>

" fun! OpenFloatWin(content, fun) abort " list of lines
"     let [width, height] = [max(map(copy(a:content),'len(v:val)')), len(a:content)]
"     let buf = nvim_create_buf(v:false, v:true)
"     cal nvim_buf_set_lines(buf, 0, -1, v:true, a:content)
"     let ui = nvim_list_uis()[0]
"     let opts = {'relative': 'win', 'width': width, 'height': height,
"                 \'col': (ui.width/2) - (width/2), 'row': (ui.height/2) - (height/2),
"                 \'style': 'minimal', 'border': 'rounded'}
"     let win = nvim_open_win(buf, 1, opts)
"     call nvim_win_set_option(win, 'winhl', 'Normal:MoreMsg')
"     " cal function(a:fun)
"     " call nvim_win_close(win, v:true)
" endfu

" let content = ['normal', 'mark', 'fold', 'scroll', 'quickfix', 'diff', 'window']
" let g:myFloatWin = OpenFloatWin(content)
" call nvim_win_close(win, v:true)
" nn <leader>j :cal OpenFloatWin(content, 'OmniJumpBoot')<CR>

" au WinNew * echom 'hello again'

" fun! Diffboth()
"     let curr = win_getid()
"     let wins = gettabinfo(tabpagenr())[0]['windows']
"     for winId in wins
"         cal win_gotoid(winId)
"         diffthis
"     endfor
"     cal win_gotoid(curr)
" endf
" com! -nargs=0 Diffboth :cal Diffboth()

" fu! CompleteTrigger()
"     if complete_info()['mode'] == 'files'
"         cal nvim_feedkeys("\<c-x>\<c-f>", "i", 1)
"     endif
" endf
" au CompleteDonePre * sil cal CompleteTrigger()
" au CompleteDone * sil cal CompleteTrigger()
" ~/desktop/sas/git/env/ag-asis.vim
" ino <c-x><c-j> <esc>:cal UltiExpand(expand("<cword>"))<cr>

" let qfIdx = 1
" for qfItem in getqflist()
"     if qfItem['bufnr'] == bufnr()
"         echom 'to mark'
"         let mkName = 'qfmark'.qfIdx
"         cal sign_define(mkName,{'text':qfIdx,'texthl':'QuickScopePrimary'})
"         cal sign_place((qfIdx+1000), 'marks', mkName, bufnr(), {'lnum':qfItem['col'],'priority':70})
"     endif
"     let qfIdx += 1
" endfor

" exe 'norm G\<plug>UndotreeEnter'
" echo undotree()['entries'][0]

" let g:TravelDepth = 99
" fu! UTreeTravel()
"     let [tempfile1, tempfile2] = [tempname(), tempname()]
"     let [idx, entries] = [1, []]
"     let Sink = {l -> execute('silent norm'.matchstr(l, '\v\d+g-'))}
"     while idx < g:TravelDepth
"         cal writefile(getbufline(bufnr(), '^', '$'), tempfile1)
"         silent norm g-
"         cal writefile(getbufline(bufnr(), '^', '$'), tempfile2)
"         let difflines = split(system(g:undotree_DiffCommand.' '.tempfile1.' '.tempfile2),"\n")
"         cal filter(difflines, 'v:val !~ "^---$"')
"         cal extend(entries, map(difflines[1:], {_,l -> idx.'g- '.l}))
"         let idx += 1
"     endwhile
"     " back to top
"     exe "silent norm ".g:TravelDepth."g+"
"     " echo entries
"     cal fzf#run({'source': entries, 'sink': Sink, 'options':['--bind']})
" endfu

" nmap <f6> :call UTreeTravel()<cr>

" let pat = '請求'
" let checksum = system("echo -n '".pat."' | md5sum | awk '{print $1}'")
" echo checksum

" echo expand('%:p')
" echo expand('%:p:h:h:h')
" echo substitute(expand('%:p'), expand('%:p:h:h:h').'/', '', '')
" let l = 1420
" for i in range(1, 40)
"     let l *= 1.05
"     echo i l
" endfor
"
" let val = 170000 + 6000 - 16000
" let disc = 1 - ((2 + 1.0/4) / 8)
" echo val * disc + 16000 - 119500
" echo 120 - 27.5 * 0.5 - 78

" let ch = getchar()
" echo ch

" let g:GreekCache .= 'b'
" let g:GreekCache .= 'c'
" echo g:GreekCache
" let g:GreekCache = g:GreekCache[:-2]
" echo g:GreekCache

" fu! GreekVisualRender(content)
"     echo a:content
"     cal ClearVirtScope()
"     cal nvim_buf_set_extmark(bufnr(''), g:greekVisual, line('.')-1, 0, {
"                 \ "virt_text":[[a:content, 'GreekVisual']],
"                 \ "virt_text_win_col": virtcol('.')-1, })
" endf

" let g:GreekCache = ''
" let g:greekVisual = nvim_create_namespace('greekVisual')
" hi GreekVisual cterm=underline ctermfg=red ctermbg=none
" fu! GrTransMode()
"     let ch = getchar()
"     if ch == 27 " ESC
"         let g:GreekCache = '' | retu
"     elseif ch == "\<BS>" && len(g:GreekCache) > 0
"         let g:GreekCache = g:GreekCache[:-2]
"     elseif nr2char(ch) == "\<CR>"
"         let [tmp, g:GreekCache] = [g:GreekCache, '']
"         exe 'norm! i'.GrTrans(tmp) | retu
"     else " feed to Greek Translator
"         let g:GreekCache .= nr2char(ch)
"     endif
"     cal ClearVirtScope()
"     cal ClearVirtScope()|VertMarkWrapper(line('.')-1, virtcol('.')-1, GrTrans(g:GreekCache), 'GreekVisual')
"     redraw | cal GrTransMode()
" endf
" nn <silent> <tab><tab> :cal GrTransMode()<CR>

" " echo winnr('$')
" let pprevwin = win_getid()
" " echo pprevwin

" au ExitPre * if exists('g:roadmapbuf') | exe 'bd!'.g:roadmapbuf | endif
" com! -nargs=0 Roadmap :cal ToggleRoadmap()
" fu! ToggleRoadmap()
"     " cal RefreshRoadMap()
"     if !exists('g:roadmapbuf') || !bufexists(g:roadmapbuf)
"         let g:roadmapbuf = bufadd('')
"         call bufload(g:roadmapbuf)
"     endif
"     if index(tabpagebuflist(), g:roadmapbuf) == -1
"         exe 'bo vsplit |b'.g:roadmapbuf.'|vert res 25'
"         cal setbufvar(g:roadmapbuf, '&rnu', 0)
"         cal setbufvar(g:roadmapbuf, '&nu', 0)
"         cal setbufvar(g:roadmapbuf, '&ft', 'roadmap')
"         syntax match rmap_mks /󰈿.*/ containedin=ALL | hi rmap_mks ctermfg=196
"         syntax match rmap_git /.*/ containedin=ALL | hi rmap_git ctermfg=185
"         syntax match rmap_anchor / .*/ containedin=ALL | hi rmap_anchor ctermfg=129
"         syntax match rmap_curr /^>/ containedin=ALL | hi rmap_curr ctermfg=82
"     endif
" endf
" fu! RefreshRoadMap(timer)
"     " clear buf content first
"     for i in range(1, 999) | cal setbufline(g:roadmapbuf, i, '') | endfor
"     call setbufline(g:roadmapbuf, 1, ['Roadmap:'])

    " let marks = {}
    " for mk in getmarklist(bufnr())
    "     let [mkn, ln] = [mk['mark'], mk['pos'][1]]
    "     let marks[str2nr(ln)] = '󰈿'.mkn[1:]
    " endfor
    " for [id, txt] in exists('b:extmks') ? items(b:extmks) : items({})
    "     let ln = nvim_buf_get_extmark_by_id(bufnr(), g:extmk, str2nr(id), {})[0] + 1
    "     let marks[str2nr(ln)] = (has_key(marks, str2nr(ln)) ? marks[str2nr(ln)] : '').' '.txt
    " endfor
    " for dif in FugitiveStatusline() != '' ? split(system('git diff --unified=0 '.expand('%').'| ag ^@@'), '\n') : []
    "     let ln = trim(matchstr(dif, '+\d*'))[1:]
    "     let marks[ln] = " git diff"
    " endfor

    " if !has_key(marks, str2nr(line('.'))) | let marks[str2nr(line('.'))] = '>>>>>' | endif
    " if exists('b:anchorLn') && b:anchorLn != 0
    "     let marks[str2nr(b:anchorLn)] = ' '.(line('.') < b:anchorLn ? 'before' : 'after')
    " endif
    " let [sortedlist, idx] = [sort(map(keys(marks), {_,v -> str2nr(v)}), 'n'), 2]
    " for ln in sortedlist
    "     if line('.') == str2nr(ln) && marks[ln] == '>>>>>'
    "         call setbufline(g:roadmapbuf, idx, ['>'])
    "     else
    "         let fmt = (line('.') == str2nr(ln) ? '> ' : '  '). '%'.len(line('$')).'d %s'
    "         call setbufline(g:roadmapbuf, idx, [printf(fmt, ln, marks[ln])])
    "     endif
    "     let idx += 1
    " endfor
" endf
" let g:refresh = timer_start(1000, 'RefreshRoadMap', {'repeat': -1})

" " au CursorMoved * if exists('g:roadmapbuf') && index(tabpagebuflist(), g:roadmapbuf) | cal RefreshRoadMap() | endif
" if exists('g:refresh')
"     cal timer_stop(g:refresh)
" endif
" cal ToggleRoadmap()

" let test = '@@ -294,3 +293,0 @@'
" echo trim(matchstr(test, '+\d*'))[1:]

" fu! CurrWord()
"     norm a
"     echom UltiSnips#CanExpandSnippet()
" endf
" ino <c-x><c-j> <esc>:cal CurrWord()<cr>

" fu! ActStl(isActive)
"     if &ft == 'qf' && a:isActive == 1 | retu " QuickFix List %l/%L %P" | en
"     if a:isActive == 0
"         retu "%#error#%r%#mod#%m%#sleepWindow# %t %y %= ln:%l/%L %P "
"     en
"     let stl=""
"     let stl="%{matchstr(getline('.')[:col('.')-1], \'\\w*$\')}"
"     let stl.="%#error#%r%#mod#%m"
"     let stl.="%#ModColor#%{(mode()=='n')?'  '.g:jumpModeNames[g:jumpMode].' ':''}%{(mode()=='t')?'  TERM ':''}"
"     let stl.="%<%#c1# %w%{filereadable(expand('%p'))?RelPath(expand('%:p'),getcwd()):expand('%:p')}"

"     let stl.="%=" " left/right separator
"     " virtual column number and byte index number
"     let stl.="%#posBar#%  %v[%c] %P %#totalL#%L% "
"     let stl.=" %#fileType#% %y %{strlen(&fenc)?&fenc:'none'}/%{strlen(&ff)?&ff:''} "
"     retu stl
" endf

" echo matchstr('something here', '\w*$')

" let b:AnonExpand = 0
" im <silent><expr> <tab> UltiSnips#CanExpandSnippet() ? "\<c-x>\<c-j>" :
"             \ pumvisible() ? "\<Down>" :
"             \ UltiSnips#CanJumpForwards() ? "\<c-k>" :
"             \ AnonExpand() != '' ? "\<c-r>=UltiSnips#Anon(AnonExpand(), matchstr(getline('.')[:col('.')-1], \'\\S*$\'))<cr>" :
"             \ "\<tab>"

" fu! AnonExpand()
"     let cw = trim(matchstr(getline('.')[:col('.')-1], '\S*$'))
"     if cw == 'afc'
"         retu 'ABC'
"     else
"         retu ''
"     endif
" endf

