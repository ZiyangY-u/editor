" clear all autocommands first
autocmd!
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
set updatetime=200
set maxmempattern=10000

" Indention
set ai et sta ts=4  " autoindent expandtab smarttab tabstop
set sr sw=4         " shiftround shiftwidth
" Selection
set virtualedit=all " Very useful!!
" }}}
" => Appearance -------------------- {{{
set nu rnu             " show line number
set cul cuc            " highlight cursor line and column
set linebreak nowrap   " stop breaking word when wrap long line
set sc sm nosmd        " showcmd showmatch noshowmode
set conceallevel=0     " do not hide anything
set switchbuf+=usetab,newtab
set title titlestring=%<%F titlelen=0
set ph=15

" Statusline
"   self-define color scheme
hi mod cterm=bold ctermfg=Black ctermbg=DarkRed
hi totalL cterm=bold ctermfg=White ctermbg=Blue
hi fileType cterm=bold ctermfg=Red ctermbg=Blue
hi posBar ctermfg=Black ctermbg=Blue
hi c1 ctermfg=Black ctermbg=DarkCyan
hi Hiraishin ctermfg=Yellow ctermbg=21
hi ModColor cterm=bold ctermfg=white ctermbg=68
hi sleepWindow ctermbg=DarkGray

let g:asyncCnt = 0
fu! ActStl(isActive)
    if &filetype == 'qf' && a:isActive == 1 | retu " QuickFix List %l/%L %P" | en
    if a:isActive == 0
        retu "%#error#%r%#mod#%m%#sleepWindow# %t %y %= ln:%l/%L %P "
    en
    let stl=""
    let stl.="%#error#%r%#mod#%m"
    let stl.="%#ModColor#%{(mode()=='n')?'  '.g:jumpModeNames[g:jumpMode].' ':''}%{(mode()=='t')?'  TERM ':''}"
    let stl.="%<%#c1# %w%{filereadable(expand('%p'))?RelPath(expand('%:p'),getcwd()):expand('%:p')}"

    let stl.="%=" " left/right separator
    " virtual column number and byte index number
    let stl.="%#posBar#%  %v[%c] %P %#totalL#%L% "
    let stl.=" %#fileType#% %y %{strlen(&fenc)?&fenc:'none'}/%{strlen(&ff)?&ff:''} "
    retu stl
endf

set stl=%!ActStl(1)
au WinNew,WinEnter,BufWinEnter * setl stl=%!ActStl(1) cuc cul
au WinLeave * setl stl=%!ActStl(0) nocuc nocul

" Non-text display
set lcs=eol:$,tab:>-,lead:∙,space:•,trail:●
hi nontext ctermfg=10

" High-light colors
"   see more high-light groups using :h highlight-groups
hi Search cterm=underline ctermfg=red ctermbg=none
hi IncSearch cterm=bold ctermfg=black ctermbg=white
hi Folded ctermfg=lightblue ctermbg=236
hi Pmenu ctermfg=white ctermbg=239
hi Visual ctermfg=black ctermbg=lightblue
hi VertSplit cterm=bold ctermfg=white ctermbg=none
hi CursorLine cterm=none ctermbg=DarkGray
hi LineNrAbove ctermfg=blue
hi CursorLineNr cterm=bold ctermfg=white
au InsertEnter * hi CursorLine cterm=bold ctermbg=52|if v:insertmode=='r'|hi CursorLine ctermbg=54|en
au InsertLeave * hi CursorLine cterm=NONE ctermbg=DarkGray

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
nn <silent> <F3> :sil cal SignMarks()\|ContextToggle<CR>
com! -nargs=* DMarks :sil exe len(<q-args>)==0?'delm a-z':':delm '.expand(<f-args>)|cal SignMarks()
au WinEnter,BufReadPost <buffer> cal SignMarks()

" Colorful (ExtMark, AttachColor)
let g:extmk = nvim_create_namespace('MyExtMarks')
fu SetExMark(bn, ln, hl, ...)
    let [ln, txt] = [line('.')-1, a:000]
    cal nvim_buf_set_extmark(a:bn, g:extmk, a:ln, 0, { "virt_text":[[' '.join(txt, ' '), a:hl]], })
endf
fu DelLineExtMark()
    for mkInfo in nvim_buf_get_extmarks(bufnr(''), g:extmk, [line('.')-1,0], [line('.')-1,0], {})
        cal nvim_buf_del_extmark(bufnr(''), g:extmk, mkInfo[0])
    endfor
endf

let g:ColorAttachs='{}' " key: sha256(ft.pat.border); val: [pat,color,border]
fu AttachColor(pattern, color, border, saveFlag)
    let pat = a:border ? '/\<'.a:pattern.'\>/' : '/'.a:pattern.'/'
    exe printf('syntax match pat_%s %s%s', sha256(a:pattern), pat, (&ft==''?'':' containedin=ALL'))
    exe printf('hi pat_%s ctermfg=%d', sha256(a:pattern), a:color)
    if a:saveFlag " update global
        exe 'let _ca = ' . g:ColorAttachs
        let _ca[sha256(&ft.a:pattern.a:border)] = [a:pattern, a:color, a:border]
        let g:ColorAttachs = string(_ca)
    endif
endf
fu RecoverGAttach()
    exe 'let _ca = ' . g:ColorAttachs
    for [sha, pcb] in items(_ca)
        let [pat, col, border] = pcb
        if sha256(&ft.pat.border) == sha
            cal AttachColor(pat, col, border, 0)
        endif
    endfor
endf
fu GDelAttach(pattern)
    exe 'let _ca = ' . g:ColorAttachs
    if has_key(_ca, sha256(&ft.a:pattern.'0')) | unlet _ca[sha256(&ft.a:pattern.'0')] | endif
    if has_key(_ca, sha256(&ft.a:pattern.'0')) | unlet _ca[sha256(&ft.a:pattern.'1')] | endif
    let g:ColorAttachs = string(_ca) " save to global
    exe printf('syntax clear pat_%s', sha256(a:pattern))
endf
au SessionLoadPost,BufWinEnter * cal RecoverGAttach()
let MColors = {'': 196, 'red':196, 'green':118, 'blue':33, 'yellow':220, 'purple':135, 'white':255, 'aqua':45}
for color in keys(MColors)
    exe printf('hi MVText%s cterm=bold ctermfg=%d', color, MColors[color])
    exe printf('com! -nargs=* SEMark%s :cal SetExMark(bufnr(""), line(".")-1, "MVText%s", <f-args>)', color, color)
    exe printf('com! -bang -range -nargs=0 Attach%s :cal AttachColor(Selected(), %d, <bang>0, 0)', color, MColors[color])
    exe printf('com! -bang -range -nargs=0 GAttach%s : cal AttachColor(Selected(), %d, <bang>0, 1)', color, MColors[color])
endfor
com! -nargs=0 DEMarks :cal DelLineExtMark()
com! -range -nargs=0 DAttach :exe printf('syntax clear pat_%s', sha256(Selected()))
com! -range -nargs=0 GDAttach :cal GDelAttach(Selected())

" Vertical Quick Scope
let g:vertLineMark = nvim_create_namespace('vertLineMark')
fu! RenderVerticalScope(start, dense)
    cal ClearVirtualTxt()
    let offset = a:start
    while offset <= winheight(0)
        let [txt, hl] = [string(offset), 'QuickScopePrimary']
        cal VirtualMarkWrapper(line('.')-offset-1, virtcol('.')-1, txt, hl)
        cal VirtualMarkWrapper(line('.')+offset-1, virtcol('.')-1, txt, hl)
        let offset += a:dense
    endwhile
endf
fu! ClearVirtualTxt()
    for ns_id in [g:vertLineMark, g:transVisual]
        for mkInfo in nvim_buf_get_extmarks(0, ns_id, 0, -1, {})
            cal nvim_buf_del_extmark(0, ns_id, mkInfo[0])
        endfor
    endfor
endf
fu! IsBlankLine()
    let ln = getline(line('.'))
    retu len(substitute(ln, '\s', '', 'g')) == 0
endf
nn <silent> d :let b:reg_name = IsBlankLine() ? '_' : v:register<cr>:cal RenderVerticalScope(1,1)<cr>@=('"'.b:reg_name.'d')<cr>
nn <silent> y :let b:reg_name = v:register<cr>:cal RenderVerticalScope(1,1)<cr>@=('"'.b:reg_name.'y')<cr>
nn <silent> c :let b:reg_name = IsBlankLine() ? '_' : v:register<cr>:cal RenderVerticalScope(1,1)<cr>@=('"'.b:reg_name.'c')<cr>
nn = :cal RenderVerticalScope(1,1)<cr>=
nn zf :cal RenderVerticalScope(1,1)<cr>zf
nn V :cal RenderVerticalScope(1,1)<cr>V
nn <c-v> :cal RenderVerticalScope(1,1)<cr><c-v>
au CursorMoved * if index(['V','v',"\<C-V>"], mode())>=0|sil cal RenderVerticalScope(1,1)|en
au CursorMoved,TextChanged,InsertEnter,TextYankPost * if index(['V','v',"\<C-V>"], mode())<0|sil cal ClearVirtualTxt()|en

" Diff
hi DiffText ctermbg=88
hi DiffChange ctermbg=none
hi DiffDelete ctermbg=245
hi DiffAdd ctermbg=86 ctermfg=black
fun! Diffboth()
    let curr = win_getid()
    let wins = gettabinfo(tabpagenr())[0]['windows']
    for winId in wins
        cal win_gotoid(winId)
        diffthis
    endfor
    cal win_gotoid(curr)
endf
com! -nargs=0 Dfboth :cal Diffboth()
" }}}
" => Automatic -------------------- {{{
set wmnu wim=list:longest,full
set fic wic
" set nrformats+=octal " let CTRL-A/CTRL-X support octal number
"   auto check time
au WinEnter,CursorHold,FocusGained * if expand('%')!="[Command Line]"|checktime

"   add dictionaries here. tip: add outside candidates through dictionary file
set dict+=/usr/share/dict/en
set dict+=/usr/share/dict/esp

set cot=menu,menuone,noselect
set ssop+=globals

"   auto completion
fu! InvokeCompletion()
    if !pumvisible() && (v:char =~ '[0-9A-Za-z.\\]')
        if &omnifunc != ''
            cal nvim_feedkeys("\<C-x>\<C-o>", "i", 1)
        elseif v:char !~ '[j.]'
            cal nvim_feedkeys("\<C-n>", "i", 1)
        en
    en
endf
au InsertCharPre *.la,*.gr,*.txt,*.py,*.vim,*.tex sil cal InvokeCompletion()
"   <tab> for select candidate
ino <silent><expr> <tab> pumvisible() ? "\<Down>" : "\<tab>"
ino <silent><expr> <s-tab> pumvisible() ? "\<Up>" : "\<tab>"
"   FZF integration
ino <expr> <c-x><c-k> fzf#vim#complete('cat /usr/share/dict/en /usr/share/dict/esp /usr/share/dict/ngerman', {}, 0)
ino <expr> <c-x><c-l> fzf#vim#complete#line({}, 1)
ino <expr> <c-x><c-h> fzf#vim#complete#buffer_line({}, 1)
nn <F1> :Helptags!<CR>
"   Consumable Autocmd
let g:cmdToConsume = []
fun! ConsumeCmd()
    for cmd in g:cmdToConsume
        cal execute(cmd)
    endfor
    let g:cmdToConsume = [] " clear cmd list
endf
au BufWinEnter *.* sil cal ConsumeCmd()|cal SignMarks()

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
nn <a-o> :cal BufJumpBack()<cr>
let g:jumpMode = 'n'
let g:jumpModeNames = {'n':'Normal','m':'Mark','f':'Fold','s':'Scroll','q':'Quickfix','d':'Diff','w':'Window','c':'Conflict'}
fu! OmniJumpBoot(backNormFlag)
    let jumpMoves = {'nj':'gj','nk':'gk',
                \'mj':"]'", 'mk':"['",
                \'qj':':cn<cr>','qk':':cp<cr>',
                \'fj':'zj','fk':'zk','fh':':setl fdl-=1<CR>','fl':':setl fdl+=1<CR>',
                \'wj':'<c-w>-','wk':'<c-w>+','wh':'<c-w>>','wl':'<c-w><',
                \'sj':'<c-d>','sk':'<c-u>','sh':'60h','sl':'60l',
                \'cj':':let @/="\\m^======="<cr>n','ck':':let @/="\\m^======="<cr>N',
                \'cl':'V?\m^<<<<<<<<cr>d/\m^>>>>>>><cr>dd','ch':'V/\m^>>>>>>><cr>d?\m^<<<<<<<<cr>dd',
                \'dj':'<Plug>(signify-next-hunk)','dk':'<Plug>(signify-prev-hunk)','dh':'<c-w>h','dl':'<c-w>l'}
    let modeChar = 'n'
    echoh MoreMsg | echo join(values(g:jumpModeNames), ' - ') | echoh None
    if a:backNormFlag == 0
        let modeChar = nr2char(getchar()) " wait for a mode char
    en
    if modeChar == 'c' " Conflict
        hi CursorLine cterm=NONE ctermbg=167
    else
        hi CursorLine cterm=NONE ctermbg=DarkGray
    endif
    let g:jumpMode = has_key(g:jumpModeNames, modeChar) ? modeChar : 'n'
    for direct in split('hjkl', '\zs')
        exe printf('nn %s %s', direct, get(jumpMoves, g:jumpMode.direct, direct))
    endfor
endf
nn <leader>j :cal OmniJumpBoot(0)<CR>
nn <leader><leader> :cal OmniJumpBoot(1)<cr>

" Hiraishin  -------------------- {{{
let g:HRSmode=1 " HiRaiShin mode
let g:hda=(exists('g:hda') ? g:hda : {}) " hda for 'hiraishin directory anchors'
nn <leader>H @=(has_key(g:hda,getcwd())==1 ? ':unlet g:hda[getcwd()]' : ':let g:hda[getcwd()]=1')<CR><CR>
nn <silent> <leader>Y :cal fzf#run({'source': keys(g:hda), 'sink': 'lcd','window':{'width':0.9,'height':0.6}})<CR>
nn <silent> <leader>o @=(g:HRSmode==1?':cal HiraishinOpen("", "MEdit")':':Files')<CR><CR>
vn <silent> <leader>o @=(g:HRSmode==1?':cal HiraishinOpen(Selected(), "MEdit")':':Files')<CR><CR>
let g:openExclude = ['"*.class"']
let g:openExcludePath = ['"*/target/*"']
fu! OpenByFile(fn)
    let [paths, e] = ['', empty(g:openExclude) ? '' : ' -not -name '.join(g:openExclude, ' -not -name ')]
    let e .= empty(g:openExcludePath) ? '' : ' -not -ipath '.join(g:openExcludePath, ' -not -ipath ')
    for anchor in keys(extend(copy(g:hda), {getcwd():1})) " include cwd
        let paths .= ' '.RelPath(anchor, getcwd())
    endfor
    retu printf('find %s %s -type f %s', paths, ' -ipath "*'.trim(a:fn).'*"', e)
endf
fu! OpenByTarget(q, t)
    let [agCmds, e] = ['', empty(g:openExclude) ? '' : ' --ignore '.join(g:openExclude, ' --ignore ')]
    let e .= empty(g:openExcludePath) ? '' : ' --ignore '.join(g:openExcludePath, ' --ignore ')
    if trim(a:q) != ''
        let findCmd = OpenByFile(a:q)
        retu printf('%s | xargs ag -l --hidden -F %s "%s"', findCmd, e, a:t)
    endif
    for anchor in keys(extend(copy(g:hda), {getcwd():1})) " include cwd
        let agCmds .= printf('ag -l --hidden -F %s "%s" %s;', e, a:t, anchor)
    endfor
    retu agCmds
endf
fu MEdit(path)
    let cmd = bufnr(a:path) > 0 ? ('b'.bufnr(a:path)) : ('edit'.a:path)
    exe cmd
endf
com! -nargs=1 MEdit :cal MEdit(<f-args>)
fu! HiraishinOpen(query, sink) " query.target
    let queries = split(' '.a:query, '[\./@]')
    let q = a:query=='' ? '' : queries[0]       " query for file
    let t = len(queries) > 1 ? queries[1] : ''  " target for content

    if t != ''
        let findCmds = OpenByTarget(q, t) " target orient
        let @/ = '\<'.t.'\>'
        let g:cmdToConsume = ["norm ggn", 'setl stl=%!ActStl(1) cuc cul']
    el
        let findCmds = OpenByFile(trim(q))   " file name orient
    en
    cal fzf#run({'source':findCmds, 'sink':a:sink, 'options':extend(copy(g:MfzfOpts), ['--query='.trim(q)])})
endf
" }}}

xn <expr> <Up> { 'V':repeat('k', winheight(0)/3) }[mode()]
xn <expr> <Down> { 'V':repeat('j', winheight(0)/3) }[mode()]
xn <silent>x :<C-U>call cursor(line("'}")-1,col("'>"))<CR>`<1v``
" Quick back to normal mode
ino jk <esc>
cno <expr> jk getcmdtype() == ':' ? '<c-u><esc>' : 'jk'
tno jk <c-\><c-n>
xn JK <esc>

" Searching
"   see "h /character-classes for more pattern shortcut
set ic scs hls is nows   " ignorecase smartcase hlsearch incsearch nowrapscan
vn * y/<C-R>"<cr>
vn # y?<C-R>"<cr>
"   QuickFix searching
let g:qfHist = (exists('g:qfHist') ? g:qfHist : {}) " qfSearchHistory
set gp=rg\ --vimgrep\ --ignore-case\ --hidden\ --follow
com! -nargs=* QfSearch :sil exe 'vimgrep /'.(len(<q-args>)==0?Selected():<q-args>).'/j '.join(GetBufFilePath(), " ")
com! -nargs=0 QfJearch :sil exe 'vimgrep /[^\x00-\x7F]/j '.expand('%')|copen|setl cul
nn ,F yiw:QfXearch <c-r>"
vn ,F y:QfXearch <c-r>"
nn ,,F yiw:QfXearch! <c-r>"
vn ,,F y:QfXearch! <c-r>"
com! -bang -nargs=* QfXearch :cal Xearch(<bang>0, <f-args>)
com! -nargs=0 QfAll :cal fzf#run({'source': keys(g:qfHist), 'sink': {inst->setqflist(g:qfHist[inst])},})
com! -nargs=1 QfYank :cal extend(g:qfHist, {<f-args>:getqflist()}) " save search result
com! -nargs=0 QfRemove :cal fzf#run({'source': keys(g:qfHist), 'sink': {inst->execute('unl g:qfHist["'.inst.'"]')},})
fun! QfMark()
    let [_, lnum, cnum, _, _] = getcurpos()
    let qfItem = [{'bufnr':bufnr(), 'lnum':lnum, 'col':cnum, 'text': getline('.')}]
    cal setqflist(extend(getqflist(), qfItem))
    cal SignMarks()
endf
com! -nargs=0 QfMark :cal QfMark()

" Fold
set fdm=manual fdl=99 fdc=auto

" Windows
"   split
fu! SplitOp(sc, query) " run a split cmd first, then operate
    let op = nr2char(getchar())
    let opts = extend(copy(g:MfzfOpts), ['--query='.a:query])
    if (op == 'o') " Open File
        cal HiraishinOpen(a:query, a:sc.'MEdit')
    elseif (op == 'b') " Buffer
        cal ClearNoName()
        let sorted = fzf#vim#_buflisted_sorted()
        cal fzf#run({'source':map(sorted, {_,bn->bn.' '.bufname(bn)}),
                    \'sink':{bn->execute(a:sc.'b'.matchstr(bn, '^[0-9]*'))}, 'options':opts,})
    elseif (op == 't') " Tag
        cal GoToTag(a:sc.'e', GetDefault(a:query, expand("<cword>")))
    elseif (op == 'q') " QuickFix
        cal fzf#run({'source': GetQfFzfList(),
                    \'sink': {pi->execute(a:sc.'cc'.split(pi,' ')[0])}, 'options':opts,})
    el
        exe a:sc."|norm \<C-L>"
    en
endf
nn ,s :cal SplitOp('bo vsplit\|', '')<CR>
nn ,S :cal SplitOp('bo split\|', '')<CR>
vn ,s :cal SplitOp('bo vsplit\|', Selected())<CR>
vn ,S :cal SplitOp('bo split\|', Selected())<CR>
"   window navigation from any mode
for direct in split('hjkl', '\zs')
    exe printf('tno <a-%s> <c-\><c-n><c-w>%s', direct, direct)
    exe printf('nn <a-%s> <c-w>%s', direct, direct)
endfor

" Tab (ngt to go go n-th tab)
set stal=2
hi TabLine cterm=none ctermfg=black ctermbg=247
hi Title cterm=bold ctermfg=red
hi Git ctermfg=Black ctermbg=185
hi Trans ctermfg=227 ctermbg=31
hi Obss ctermfg=Black ctermbg=118
nn ,t :cal SplitOp('tabe \|', '')<CR>
vn ,t :cal SplitOp('tabe \|', Selected())<CR>
nn t gt
nn T gT
fu! Shortf(fname)
    retu fnamemodify(a:fname, ':p:t')
endf
fu! ActTal()
    let [tal, curr] = ['', tabpagenr()]
    hi cc ctermfg=black ctermbg=lightgreen
    for tn in range(1, tabpagenr('$'))
        let bg = 244-(tn % 6)
        exe printf('hi c%s ctermfg=white ctermbg=%s', bg, bg)
        exe printf('hi ct%s ctermfg=lightred ctermbg=%s', bg, bg)
        let winIds = gettabinfo(tn)[0]['windows']
        let bufnrs = uniq(map(winIds, {_,wi -> getwininfo(wi)[0]['bufnr']}))
        let fname = map(bufnrs, {_,bn -> Shortf(bufname(bn))})
        let tal .= (tn==curr?'':'%#ct'.bg.'#%  '.tn).'%#c'.(tn==curr?'c':bg).'#%  '.join(fname,'|').' '
    endfor
    let tal .= "%#TabLine#%="
    " running indicators
    let tal .= "%#error#%{g:asyncCnt > 0 ? '  '.g:asyncCnt.' ':''}"
    let tal .= "%{gutentags#statusline() == '' ? '' : ' 󱈢 '}"
    let tal .= "%#Git#%{FugitiveStatusline()}"
    let tal .= "%#Trans#%{g:TransMode}"
    let tal .= "%#Obss#%{ObsessionStatus()}"
    let tal .= "%#Hiraishin#%{(g:HRSmode==1)  ?'   ':''}"
    retu tal
endfu
set tal=%!ActTal()

" Buffers
nn ,b :cal ClearNoName()\|cal fzf#vim#buffers({}, 1)<CR>
vn ,b :cal ClearNoName()\|cal fzf#vim#buffers(Selected(), {}, 1)<CR>

" Shortcuts
"   execute current line as bash cmd ('e' for 'execute')
nn ,e :.w !bash<CR>
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
nn ,w :update<CR>
"   surround operations ('s' for surround, 'S' for remove surround)
nn s :set opfunc=SurroundOp<cr>g@
vn s :<c-u>cal SurroundOp(visualmode())<cr>
nn S :cal DeSurroundOp()<cr>
"   change current letter by its next (for quick fix misspell)
nn <expr> <BS> col(".") == (col("$")-1) ? 'xP' : 'xhP'
"   replace content
nn ,r r
nn <silent> r :let b:reg_name = v:register<cr>:set opfunc=ReplaceOp<cr>g@
nm <silent> rr Vr
vn ,r r
vn r :<c-u>let b:reg_name = v:register<cr>:cal ReplaceOp(visualmode())<cr>
"   fzf commands
nn ,c :Commands!<cr>
"   compensate for Visual Edition
nn D Dh
"   quick to command, line macro need of visual selection
vn ,q :norm! @
"   leave current window open
nn <leader>n :only<CR>
nn <leader>N :tabonly<CR>
"   quick for register
map - "_
nn x "_x
nn <silent> K @=(index(['ark','text'],&ft)>=0?':cal Wiki(expand("<cword>"))':(&ft=='vim'?'K':':cal Google(&ft." ".expand("<cword>"))'))<CR><CR>
nn gl :cal LspAction()<CR>
fu! LspAction()
    let prefix = 'vim.lsp.buf.'
    let actTable = {
                \ 'a':'code_action',
                \ 'd':'definition',
                \ 'k':'hover',
                \ 'i':'implementation',
                \ 'r':'references',
                \ 'n':'rename',
                \}
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
fun! GoToTag(edit, query)
    let tagExp = '\v(^'.a:query.'$)' "use strict match
    let tags = taglist(tagExp)
    let entries = map(tags, {_,tag -> TagRender(a:edit, tag)})
    cal fzf#run({'source':entries, 'sink':function('execute'), 'options':g:MfzfOpts})
endfu
" Toggle
nn <expr> <f2> &list==1 ? ':setl nolist<cr>':':setl list<cr>'

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
ca jis e ++enc=sjis
ca dos e ++ff=dos
ca jdos e ++enc=sjis ++ff=dos
" }}}
" => plugins --------------------------- {{{
cal plug#begin('~/.vim/plugged')

    " Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
    Plug 'SirVer/ultisnips'
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

cal plug#end()
" }}}
" => Plugin-configs -------------------- {{{
" commentary
au VimEnter * if exists('*commentary')|unmap gcc|en
nn gc :cal RenderVerticalScope(1,1)<cr><Plug>Commentary
" emmet
let g:user_emmet_install_global = 0
let g:user_emmet_leader_key = '<c-y>'
" fzf.vim
let $FZF_DEFAULT_OPTS='--no-preview -0'
let g:fzf_preview_window = []
hi Purple ctermfg=135 ctermbg=none
let g:fzf_colors = {'hl':['fg', 'Purple'], 'hl+':['fg', 'Purple']}
let g:MfzfOpts = ['-1', '-m', '-i', '--reverse',]
" ultisnips
fun! UltiExpand(fromVisual)
    let [snips, query] = [UltiSnips#SnippetsInCurrentScope(1), '']
    if a:fromVisual == 1
        let Sink = {snip -> execute('norm! gv"_c'.split(snip, "	")[0]."\<c-r>=UltiSnips#ExpandSnippet()\<cr>\<esc>gvkoj=")}
    el
        let query = expand("<cword>")
        let Sink = {snip -> execute('norm! "_ciw'.split(snip, "	")[0]."\<c-r>=UltiSnips#ExpandSnippet()\<cr>")}
    en
    cal fzf#run({'source': values(map(snips, {k,v -> k."	".v})), 'sink': Sink,
                \'window':{'width':0.7,'height':0.6}, 'options':['-1', '-i', '--query='.query]})
endf
let g:UltiSnipsExpandTrigger="<c-x><c-j>"
ino <a-j> <esc>:cal UltiExpand(0)<cr>
let g:UltiSnipsSnippetDirectories=["UltiSnips", "mycoolsnippets"]
let g:UltiSnipsEditSplit="context"
vn <a-j> :cal UltiSnips#SaveLastVisualSelection()<cr>:cal UltiExpand(1)<cr>
nn <silent> <f4> :UltiSnipsEdit<cr>
nn <silent> ,<f4> :to vsplit \|e /usr/share/nvim/runtime/mycoolsnippets/all.snippets<cr>
" leap.nvim
nn ,f :lua require('leap').leap{ target_windows = { vim.fn.win_getid() } }<cr>
" quick-scope
let g:qs_highlight_on_keys = ['f', 'F', 't', 'T']
highlight QuickScopePrimary ctermfg=red
highlight QuickScopeSecondary ctermfg=92
" vim-matchup
let g:matchup_matchparen_offscreen = {}
let g:matchup_matchparen_enabled   = 0
" context.vim
let g:context_enabled = 0
" fugitive
let g:fugitive_no_maps = 1
ca gi Git
ca gl tab Git log -n 500 --pretty=tformat:"commit %H%d%nparent %P%nauthor %an <%ae> %ci%n%n%B" --author-date-order --abbrev=40
ca glg tab Git log -n 100 --graph --pretty='%H %s %d %ad %ae' --date=short --author-date-order
ca glga tab Git log -n 100 --graph --pretty='%H %s %d %ad %ae' --date=short --all --author-date-order
ca glp tab Git log -p -- %
ca gb tab Git branch
ca gc Git commit
ca gca Git commit --amend
ca gco Git checkout
ca gps Git push
ca gm Git merge
" vim-easy-align
xn g= <Plug>(EasyAlign)
nn g= :cal RenderVerticalScope(1,1)<cr><Plug>(EasyAlign)
let g:easy_align_delimiters = {
            \ '>': { 'pattern': '>>\|=>\|>' },
            \ '/': { 'pattern': '//\+\|/\*\|\*/', 'delimiter_align': 'l', 'ignore_groups':   ['!Comment'] },
            \}
" wilder.nvim
call wilder#setup({'modes': [':']})
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
    nmap <buffer> k <plug>UndotreeNextState
    nmap <buffer> j <plug>UndotreePreviousState
    nmap <buffer> K <plug>UndotreeNextSavedState
    nmap <buffer> J <plug>UndotreePreviousSavedState
    nmap <buffer> <c-k> <plug>UndotreeRedo
    nmap <buffer> <c-j> <plug>UndotreeUndo

    nmap <buffer> h <plug>UndotreeTimestampToggle
    nmap <buffer> l <plug>UndotreeFocusTarget
endf
nn <leader>u :UndotreeToggle<cr>
" devicons
let g:webdevicons_enable_nerdtree = 1
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
    au FileType javascript setl ts=2 sw=2
    au FileType vim setl tw=0
    au FileType html,javascript,css,xml :EmmetInstall
    au FileType sql setl ofu=
    au FileType python,vim,c,javascript,java setl ofu=v:lua.vim.lsp.omnifunc
    au FileType git setl fdm=syntax fdl=0
    " au BufWritePre * :sil! ClearTailBlank
    " auto save file to OneDrive
    au BufWritePost init.vim sil exe ':!cp ~/.config/nvim/init.vim ~/OneDrive'
aug END
" }}}
" => Functions -------------------- {{{
com! -nargs=0 ClearTailBlank :%s/\s\+$//
com! -nargs=0 Ztool :e ~/desktop/tool.ztool
com! -nargs=0 Zawk :e ~/desktop/my-awk.awk

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
fu! GetBufFilePath() " return a list
    retu map(filter(range(0,bufnr('$')), 'buflisted(v:val)'), 'fnamemodify(bufname(v:val), "")')
endf
fu! GetDefault(v, default)
    if empty(a:v) | retu a:default
    el | retu a:v
    en
endf
fu! QuickRun()
    if &ft == 'vim' | so %
    en
endf
nn <silent> <f5> :cal QuickRun()<cr>
fu! ClearNoName() abort
    for buf in getbufinfo()
        if bufname(buf.bufnr) == '' && buflisted(buf.bufnr) == 1 | sil exe 'bd'.buf.bufnr | en
    endfor
endf
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

" ----------------- Operator Functions -----------------
" Replace-Operator
fu! ReplaceOp(type)
    echom a:type
    if a:type ==# 'v'
        exe printf('norm! `<v`>"_d"%sP', b:reg_name)
    elseif a:type ==# 'char'
        exe 'norm! mz'
        exe printf('norm! `[v`]"_d"%sP', b:reg_name)
        sil exe 'norm! `z'
        sil cal execute('DMarks z')
    elseif a:type ==# 'V'
        exe printf('norm! `<V`>"_d"%sP', b:reg_name)
    elseif a:type ==# 'line'
        exe printf('norm! `]$v`[0"_d"%sP', b:reg_name)
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
        exe printf("norm! `[v`]\"sc%s%s\<esc>\"sP", start, end)
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
        retu substitute(converted, '_\([a-z]\)', '\u\1', 'g')
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
fu! WebSearch(content, url, escapeMap)
    let resultTarget = ''
    for ch in split(a:content, '\zs')
        let resultTarget .= get(a:escapeMap, ch, ch)
    endfor
    exe 'sil !msedge.exe '. a:url . resultTarget . ' &' | redraw!
endf

let g:WikiTag = ''
fu! Wiki(word, ...)
    let esMap = {'ā':'a','ē':'e','ī':'i','ū':'u','ō':'o','ᾱ':'α','ῡ':'υ','ῑ':'ι','ȳ':'y'}
    cal WebSearch(get(a:, 1, a:word) . g:WikiTag, 'https://en.wiktionary.org/wiki/', esMap)
endf
fu! Google(content, ...)
    let esMap = {' ':'\ '}
    let q = len(a:000) == 0 ? a:content : join(a:000, ' ')
    cal WebSearch(q, 'https://www.google.com/search\?q=', esMap)
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
let g:transVisual = nvim_create_namespace('transVisual')
let g:transCache = ''
let g:TransMode = ''
fu! TranslitMode()
    hi CursorLine ctermbg=31 | redraw | let ch = getchar()
    if ch == 27 || (g:transCache[-1:-1] == 'j' && ch == 107) " ESC
        hi CursorLine cterm=NONE ctermbg=DarkGray
        cal ClearVirtualTxt() | let g:transCache = '' | retu
    elseif ch == "\<BS>" && len(g:transCache) > 0            " backward
        let g:transCache = g:transCache[:-2]
    elseif nr2char(ch) == "\<CR>"                            " complete
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
" -------------------- Calc Misc -----------------------
fu! NumTrans(fmt, num)
    let fmtMap = {'x': '0x%X', 'b': '0b%08b', 'd': '%d'}
    retu printf(get(fmtMap, a:fmt, ''), a:num)
endf
vn <silent> <tab>nx c<C-R>=OmniTranslit('NumTrans', ['x'], '<C-R>-')<CR><ESC>
vn <silent> <tab>nb c<C-R>=OmniTranslit('NumTrans', ['b'], '<C-R>-')<CR><ESC>
vn <silent> <tab>nd c<C-R>=OmniTranslit('NumTrans', ['d'], '<C-R>-')<CR><ESC>
" ------------------- Windows Misc -----------------------
fu WinPath(mntPath) " convert wsl mnt path to windows path
    retu substitute(a:mntPath, '/mnt/\([a-zA-Z]\)', '\1:', '')
endf
com! -nargs=0 WSLview exe 'sil !wslview %'
com! -nargs=0 Notepad exe 'sil !subl.exe -a '.WinPath(expand('%')).':'.line('.')
let g:EclipsePath = '/mnt/c/Users/ziyan/desktop/sas/jee-2021-062/eclipse' " eclipse needs relative path for eclipse.exe
com! -nargs=0 Eclipse exe 'sil !' . g:EclipsePath . '/eclipse.exe '.RelPath(expand('%'), g:EclipsePath)
com! -nargs=0 Directory exe 'sil !explorer.exe ' . substitute(WinPath(expand('%:p:h')), '/', '\\\\', 'g')
" ------------------- Async Misc -----------------------
"  qfSearchCmd { qfEntry : [jobId list] }
"  qfListTobe { jobId : [qfResult] }
"  let one qfEntry in qfSearchCmd hold multiple jobId
let [g:qfSearchCmd, g:qfListTobe] = [{}, {}]
let g:AutoPop = 1
function! s:OnGetRst(jobId, data, event) dict " parse rg result line by line
    for ln in a:data
        let posInfo = matchstr(trim(ln), '^.*:\d*:\d*:')
        let blc = split(posInfo, ':') " Buf Ln Col
        let showTxt = substitute(trim(ln), posInfo, '', '')
        if (len(blc) > 0)
            let qfItem = [{'bufnr':bufnr(blc[0], 1), 'lnum':blc[1], 'col':blc[2], 'text': showTxt}]
            sil cal extend(g:qfListTobe[a:jobId], qfItem)
        endif
    endfo
endfunction
fu! ComparePos(pl, pr)
    if a:pl['bufnr'] != a:pr['bufnr']
        return a:pl['bufnr'] > a:pr['bufnr']
    elseif a:pl['lnum'] != a:pr['lnum']
        return a:pl['lnum'] > a:pr['lnum']
    elseif a:pl['col'] != a:pr['col']
        return a:pl['col'] < a:pr['col'] " for result in same line, let cursor move right to left
    endif
    return 0
endf
fu! s:OnExit(jobId, data, event) abort " merge multiple rg result by qfEntry
    for [entry, jobIdLst] in items(g:qfSearchCmd) " search qfEntry by a:jobId
        if index(jobIdLst, a:jobId) >= 0
            let qfEntry = entry | break
        endif
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
    if g:asyncCnt == 0 && g:AutoPop == 1 | copen | endif
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
    endif
    if match(toSearch, '[^\x00-\x7F]') >= 0 " no-ASCII char
        cal AsyncSearch(toSearch, extend(args, ['--encoding=sjis']), qfEntry)
    endif
endf
" }}}

" => LSP -------------------- {{{
lua << EOF
require("nvim-lsp-installer").setup {}
local lspconfig = require('lspconfig')
lspconfig.pyright.setup{}
lspconfig.tsserver.setup{}
lspconfig.html.setup{}
lspconfig.cssls.setup{}
lspconfig.vimls.setup{}
lspconfig.clangd.setup{}
lspconfig.texlab.setup{}
EOF
" }}}
