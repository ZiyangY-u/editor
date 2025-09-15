syntax match LOG_INFO "\<INFO\>"
highlight LOG_INFO ctermfg=lightblue

syntax match LOG_DEBUG "\<DEBUG\>"
highlight LOG_DEBUG ctermfg=130

syntax match LOG_ERROR "\<ERROR\>"
highlight LOG_ERROR ctermfg=red

let light_colors = [ 37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195 ]

for i in range(1, 999)
    let _thread_pat = printf('"\<http-nio-8081-exec-%d\>"', i)
    exe printf('syn match thread-%d %s', i, _thread_pat)
    let _thread_pat = printf('"\<Thread-%d\>"', i)
    exe printf('syn match thread-%d %s', i, _thread_pat)

    exe printf('hi thread-%d ctermfg=%d', i, light_colors[i % len(light_colors)])
endfor
