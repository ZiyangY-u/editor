let g:db_path = '~/.config/nvim/temp.db'
let g:db_script = '~/.config/nvim/my-db.sql'

com! -nargs=0 InitDb :cal system('rm '.g:db_path)
ca edb tabe \| e +1;norm\ zt <c-r>=g:db_script<cr>

fu! RunDb()
    let opts = { 'cwd':fnamemodify(g:db_script, ':h'), 'strip':1, 'save':1}
    cal asyncrun#run(0, opts, printf('sqlite3 %s ".read %s"', g:db_path, fnamemodify(g:db_script, ':t')))
endf
