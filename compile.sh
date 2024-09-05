#!/bin/bash

cd /root/.config/nvim
cc anon_expand.c -o anon_expand
echo "anon_expand compiled!"

cc char_width.c -o char_width
cc pair_hint.c -o pair_hint
echo "pair_hint compiled!"

cc quote_hint.c -o quote_hint
echo "quote_hint compiled!"
