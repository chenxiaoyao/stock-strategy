#!/bin/bash

traverse() {
    prefix=$1
    tailMax=$2
    tailLen=$3

    tail=0
    while (( tail < $tailMax ))
    do
        code=$(printf "%s%0${tailLen}d" $prefix $tail)
        url=$(printf "http://stock.jrj.com.cn/share,%s,sdgd.shtml" $code)
        curl -s $url -o temp1.txt
        iconv -f GB2312 -t UTF-8 temp1.txt > temp2.txt
        found=$(grep -nor "前海进化论.*" temp2.txt)
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

rm temp1.txt temp2.txt
