package main

import (
    "fmt"
    "os"
)

func nthRune(s string, n int) string {
    runes := []rune(s)
    if n < len(runes) {
        return string(runes[n])
    }
    return ""
}

func contains(arr []string, target string) bool {
    for _, val := range arr {
        if val == target {
            return true
        }
    }
    return false
}

func hasKey(m map[string]string, target string) bool {
    _, ok := m[target]
    if ok {
        return true
    } else {
        return false
    }
}

func main() {
    var VOWELS = []string{"a", "i", "u", "e", "o"}

    var HIRAKANA = map[string]string{
        "q": "っ", "ltu": "っ",
        "la": "ぁ", "a": "あ", "li": "ぃ", "i": "い", "lu": "ぅ", "u": "う", "le": "ぇ", "e": "え", "lo": "ぉ", "o": "お",
        "ka": "か", "ga": "が", "ki": "き", "gi": "ぎ", "ku": "く", "gu": "ぐ", "ke": "け", "ge": "げ", "ko": "こ", "go": "ご",
        "sa": "さ", "za": "ざ", "shi": "し", "ji": "じ", "su": "す", "zu": "ず", "se": "せ", "ze": "ぜ", "so": "そ", "zo": "ぞ",
        "ta": "た", "da": "だ", "chi": "ち", "di": "ぢ", "tu": "つ", "du": "づ", "te": "て", "de": "で", "to": "と", "do": "ど",
        "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
        "ha": "は", "ba": "ば", "pa": "ぱ", "hi": "ひ", "bi": "び", "pi": "ぴ", "fu": "ふ", "bu": "ぶ", "pu": "ぷ", "he": "へ", "be": "べ", "pe": "ぺ", "ho": "ほ", "bo": "ぼ", "po": "ぽ",
        "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
        "lya": "ゃ", "ya": "や", "lyu": "ゅ", "yu": "ゆ", "lyo": "ょ", "yo": "よ",
        "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
        "lwa": "ゎ", "wa": "わ", "wo": "を", "n": "ん", "lka": "ゕ", "lke": "ゖ",
        "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",
        "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",
        "sha": "しゃ", "shu": "しゅ", "sho": "しょ",
        "ja": "じゃ", "ju": "じゅ", "jo": "じょ",
        "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",
        "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",
        "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",
        "mya": "みゃ", "myu": "みゅ", "myo": "みょ",
        "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",
        "-": "ー",
    }

    romaji := os.Args[1]
    var kana_buf string
    var romaji_buf string

    for _, ch := range romaji {
        if contains(VOWELS, string(ch)) {
            romaji_buf = romaji_buf + string(ch)
            if len(romaji_buf) > 2 && !contains(VOWELS, nthRune(romaji_buf, 0)) && nthRune(romaji_buf, 0) == nthRune(romaji_buf, 1) {
                if nthRune(romaji_buf, 0) == "n" {
                    kana_buf = kana_buf + HIRAKANA["n"]
                    romaji_buf = romaji_buf[2:]
                } else { // add っ
                    kana_buf = kana_buf + HIRAKANA["q"]
                    romaji_buf = romaji_buf[1:]
                }
            }
            if hasKey(HIRAKANA, romaji_buf) {
                kana_buf = kana_buf + HIRAKANA[romaji_buf]
                romaji_buf = ""
            } else if len(romaji_buf) == 3 && nthRune(romaji_buf, 0) == "n" && hasKey(HIRAKANA, romaji_buf[1:]) {
                kana_buf = kana_buf + HIRAKANA["n"]
                kana_buf = kana_buf + HIRAKANA[romaji_buf[1:]]
                romaji_buf = ""
            }
        }
        if string(ch) == "-" {
            kana_buf = kana_buf + "ー"
            romaji_buf = ""
            continue
        }
        if !contains(VOWELS, string(ch)){
            romaji_buf = romaji_buf + string(ch)
        }
    }
    if len(romaji_buf) > 0 {
        if romaji_buf == "nn" {
            kana_buf = kana_buf + HIRAKANA["n"]
        }
    }

    fmt.Println(kana_buf)
}
