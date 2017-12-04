#!/bin/bash

traverse() {
    prefix=$1
    tailMax=$2
    tailLen=$3

    tail=0
    while (( tail < $tailMax ))
    do
        code=$(printf "%s%0${tailLen}d" $prefix $tail)
        url=$(printf "http://quotes.money.163.com/f10/gdfx_%s.html#10e01" $code)
        curl -s $url -o temp.txt
        found=$(grep -m 1 -o "前海进化论[^'\"<>/]*" temp.txt)
        if [[ x$found != x ]]; then
            echo $code: $found
        fi
        found=$(grep -m 1 -o "希瓦[^'\"<>/]*" temp.txt)
        if [[ x$found != x ]]; then
            echo $code: $found
        fi

        let tail+=1
    done
}

traverse '60' 10000 4
traverse '000' 1000 3
traverse '002' 1000 3
traverse '300' 1000 3

rm -f temp.txt
