let g:db_path = '~/.config/nvim/temp.db'
let g:db_script = '~/.config/nvim/my-db.sql'

let g:db_rst_mode = 0 " 0 : quickfix; 1 : tab-temp

com! -nargs=0 InitDb :cal system('rm '.g:db_path)
ca edb tabe \| e +1;norm\ zt <c-r>=g:db_script<cr>

fu! RunDb()
    let opts = { 'cwd':fnamemodify(g:db_script, ':h'), 'strip':1, 'save':1, 'silent':1}
    cal asyncrun#run(0, opts, printf('sqlite3 %s ".read %s"', g:db_path, fnamemodify(g:db_script, ':t')))
endf

fu! ShowDbResult()
    if empty(getqflist()) == 1
        return
    elseif g:db_rst_mode == 0 " quickfix
        copen
    elseif g:db_rst_mode > 0 && match(g:asyncrun_info, '^sqlite3') >= 0 && g:asyncrun_status == 'success'
        let [qflist, tempfile] = [getqflist(), tempname()]

        execute 'redir! > ' . tempfile
        for entry in qflist
            echo entry.text
        endfor
        redir END
        execute 'tabe ' . tempfile
    endif
endf

au User AsyncRunStop :cal ShowDbResult()
