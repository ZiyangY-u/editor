" pdf page indicator
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

" init tex log buffer
au BufWinEnter *.tex if !exists('g:texInfoBuf') || !bufexists(g:texInfoBuf) | let g:texInfoBuf = bufadd(tempname()) | endif

" tex compile 
let g:texCompileStatus = 0 " 0 : stop; 1 : running
let g:texCompilePending = 0
let g:texCompileSuccess = 0 " -1 : failure; 0 : running; 1 : success

fu! s:TexCompilePost(jobId, data, event)
    if a:data == 0
        let g:texCompileSuccess = 1
        let target_path = fnamemodify(expand('%:p:r'), ':p:r')
        sil exe printf('!mv %s.tmp.pdf %s.pdf', target_path, target_path)
    else
        let g:texCompileSuccess = -1
    endif
endf

fu! CheckTexCompiling(timer)
    if !exists('g:texCompilePID') | let g:texCompileStatus = 0 | en
    let checkRst = trim(system(printf('[ -d "/proc/%d" ] && echo "yes" || echo "no"', g:texCompilePID)))
    if checkRst == 'yes'
        let g:texCompileStatus = 1
    else
        let g:texCompileStatus = 0
        cal timer_pause(g:checkTexCompilingTimer, 1)
        if g:texCompilePending == 1 | let g:texCompilePending = 0 | cal CompileTex() | en
    endif
    redrawtabline
endfu

" package checking
fu! PackageCheck()
    return v:true
endf

fu! CompileTex()
    if !exists('g:checkTexCompilingTimer')
        let g:checkTexCompilingTimer = timer_start(100, 'CheckTexCompiling', {'repeat': -1})
    else
        cal timer_pause(g:checkTexCompilingTimer, 0)
    endif

    if g:texCompileStatus == 1 " set pending
        let g:texCompilePending = 1
        return
    endif
    let g:texCompileSuccess = 0 " running

    let cmd = printf('xelatex --halt-on-error --jobname=%s.tmp %s > %s', expand('%:r'), expand('%:p'), bufname(g:texInfoBuf))
    let opts = {'detach':v:true, 'on_exit' : function('s:TexCompilePost')}
    let g:texCompilePID = jobpid(jobstart(cmd, opts))
endfu
com! -nargs=0 TexLog :exe 'tabe | e +$;norm\ zz '.bufname(g:texInfoBuf)
