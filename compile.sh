#!/bin/bash

cd ~/.config/nvim
cc anon_expand.c -o anon_expand
echo "anon_expand compiled!"

cc char_width.c char_util.c -o char_width
cc pair_hint.c char_util.c -o pair_hint
echo "pair_hint compiled!"

cc quote_hint.c -o quote_hint
echo "quote_hint compiled!"

cc dynamic-calc-chunk.c -o dy-chunk-calc
cc dynamic-read.c -o dy-read
echo "dynamic-read compiled!"

cp awk-template.awk awk-shadow.awk
