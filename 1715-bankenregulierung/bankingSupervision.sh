#!/bin/bash

#Marie-José Kolly via NZZ Storytelling, July 2017: How we scraped the publication database of the Basel Committee on Banking Supervision and analyzed their supervisory texts in order to visualize quantity and quality of regulatory text over time
#Feedback welcome by e-mail marie-jose.kolly[at]nzz.ch or twitter [at]mjkolly

#Article presenting results: www.nzz.ch/ld.1304103


#risk per file, corpus 3
cd mypath/data/corpus3
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" && grep -o 'risk' $file | wc -l; done  > /mypath/data/unixResults/riskPerFile_unix.txt

#words per file, corpus 2
cd mypath/data/corpus2
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" && wc -w $file; done  > /mypath/data/unixResults/nWordsPerFile_unix.txt

#word frequency, corpus 3
cd mypath/data/corpus3
cat *.txt > mypath/data/unixResults/allTextC3_unix.txt
cd unixResults
cat allTextC3_unix.txt|tr ' ' '\n'| sort | uniq -c | sort -rn  > mypath/data/unixResults/wordFreqencyC3_unix.txt

#word frequency, corpus 2
cd mypath/data/corpus2
cat *.txt > mypath/data/unixResults/allTextC2_unix.txt
cd unixResults
cat allTextC2_unix.txt|tr ' ' '\n'| sort | uniq -c | sort -rn  > mypath/data/unixResults/wordFreqencyC2_unix.txt

#collocations
cd mypath/data/unixResults
cat allTextC2_unix.txt | sed 's/,//' | sed G | tr ' ' '\n' > tmp.txt
tail -n+2 tmp.txt > tmp2.txt
paste -d ',' tmp.txt tmp2.txt | grep -v -e "^," | grep -v -e ",$" | sort | uniq -c | sort -rn > mypath/data/unixResults/bigramsFrequencyC2_unix.txt

#trigrams
cd mypath/data/unixResults
cat allTextC2_unix.txt | sed 's/,//' | sed G | tr ' ' '\n' > tmp.txt
tail -n+2 tmp.txt > tmp2.txt
tail -n+2 tmp2.txt > tmp3.txt
paste -d ',' tmp.txt tmp2.txt tmp3.txt | grep -v -e "^," | grep -v -e ",$" | grep -v -e ",," | sort | uniq -c | sort -rn > mypath/data/unixResults/trigramsFrequencyC2_unix.txt

#most important risk types per file, corpus 2 
cd mypath/data/corpus2
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" \
&& grep -o '\<credit risk' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<market risk' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<operational risk' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<interest rate risk' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<liquidity risk' $file | wc -l; done  > mypath/data/unixResults/riskTypesPerFileWithUnix_unix.txt

#modal verbs and constructions per file, corpus 2
cd mypath/data/corpus2
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" \
&& grep -o '\<should\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<should not\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<must\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<must not\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<has to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<have to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<does not have to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<do not have to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<shall\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<shall not\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<ought to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<ought not\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<need to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<needs to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<does not need to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<do not need to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<need not\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<is supposed to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<are supposed to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<is not supposed to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<are not supposed to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<is required to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<are required to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<is not required to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<are not required to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<is obliged to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<are obliged to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<is not obliged to\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<are not obliged to\>' $file | wc -l; done  > mypath/data/unixResults/modVerbsPerFileWithUnix_unix.txt

#regulatory instruments per file, corpus 3
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" \
&& grep -o '\<capital requirement' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<risk-weighted asset' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<risk weighted asset' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<supervisory review' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<stress test' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<internal capital adequacy assessment process' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<icaap\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<market discipline' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<disclosure requirement' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<disclosure standard' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<capital conservation buffer' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<leverage ratio' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<lr\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<total loss absorbing capacity' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<total loss absorbing capaciti' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<tlac\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<countercyclical capital buffer' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<countercyclical buffer' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<liquidity coverage ratio' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<lcr\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<high-quality liquid asset' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<hqla\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<net stable funding ratio' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<nsfr\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<available stable funding' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<required stable funding' $file | wc -l; done  > mypath/data/unixResults/instrumentsWithUnix_unix.txt



