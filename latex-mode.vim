" pdf page indicator
let g:PdfLoc = 1
fu! GetPdfLoc()
    let cmd = printf('synctex view -i %d:1:%s.tex -o %s.tmp.pdf|rg "Page"|sort -u', line('.'), Tex_path(), Tex_path())
    let _rst = split(trim(system(cmd)), '\n')
    if len(_rst) != 1 | retu 'x' | en
    let rst = substitute(_rst[0],'Page:','','')
    retu rst
endf
com! -nargs=0 Pdf exe 'sil !SumatraPDF.exe -reuse-instance -page ' . g:PdfLoc . ' ' . WinPath(substitute(expand('%:p'), '.tex$', '.pdf', ''))
com! -nargs=0 PdfLoc exe 'sil !SumatraPDF.exe -reuse-instance -page ' . g:PdfLoc . ' ' . WinPath(substitute(expand('%:p'), '.tex$', '.pdf', ''))
com! -nargs=0 EdTexMacros tabe | e ~/.config/nvim/tex/zzmakros.sty
au CursorHold *.tex let g:PdfLoc = GetPdfLoc()
au BufWritePost zzmakros.sty cal system('cp ~/.config/nvim/tex/zzmakros.sty ~/texmf/tex/xelatex/')

fu! Tex_path()
    retu substitute(expand('%:p:r'), 'tex$', '', '')
endf

" tex compile
let g:texCompilePending = 0
let g:texCompileStatus = 0 " 0 : stop; 1 : running
let g:texCompileResult = 0 " -1 : failure; 0 : running; 1 : success

fu! s:TexCompilePost(jobId, data, event)
    let g:texCompileStatus = 0
    if a:data == 0
        let g:texCompileResult = 1
        sil exe printf('!cp %s.tmp.pdf %s.pdf', Tex_path(), Tex_path())
    else
        let g:texCompileResult = -1
    endif
    redrawtabline
endf

fu! CheckTexCompiling(timer)
    if g:texCompileStatus == 0
        cal timer_pause(g:checkTexCompilingTimer, 1)
        if g:texCompilePending == 1 | let g:texCompilePending = 0 | cal CompileTex() | en
    endif
    redrawtabline
endfu

fu! CompileTex()
    if !exists('g:checkTexCompilingTimer')
        let g:checkTexCompilingTimer = timer_start(100, 'CheckTexCompiling', {'repeat': -1})
    else
        cal timer_pause(g:checkTexCompilingTimer, 0)
    endif

    if g:texCompileStatus == 1 " if running set pending
        let g:texCompilePending = 1 | return
    endif
    let g:texCompileStatus = 1 " running

    let cmd = printf('xelatex -synctex=1 --halt-on-error --jobname=%s.tmp --output-directory=%s %s', expand('%:t:r'), expand('%:p:h'), expand('%:p'))
    let opts = {'detach':v:true, 'on_exit' : function('s:TexCompilePost')}
    let g:texCompileJID = jobstart(cmd, opts)
endfu

fu! ShowLog()
    let tmpfile = tempname()
    let cmd = 'texlogsieve '.Tex_path().'.tmp.log > ' . tmpfile
    cal system(cmd)

    retu tmpfile
endf
com! -nargs=0 TexLog :exe 'tabe | e +$;norm\ zz '.ShowLog()

" below is calculation module in latex
let src_path = VimrcPath().'python/latex_calc.py'
py3file `=src_path`
