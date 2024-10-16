# NZZ Storytelling, script for the following article: https://www.nzz.ch/international/freund-und-feind-betrachtet-durch-die-brille-des-weissen-hauses-ld.1349175#subtitle-die-methodik-im-detail
# questions and comments: marie-jose.kolly@nzz.ch


#USA per file, corpus 1 because we also want caps for US (vs. us-pronoun)
cd mypath/data/sotu_corpus1
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" \
&& egrep -o 'americ|Americ' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'our republic|our Republic' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'our union|our Union|federal union|federal Union' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'united states|United States|\<US\>|\<USA\>|\<usa\>' $file | wc -l; done  > mypath/data/datafiles/americUSPerFile.txt

#countries per file
cd mypath/data/sotu_corpus2
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" \
&& grep -o 'afghan' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<aland' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'albania' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'algeria|algerine' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'american samoa' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'andorra' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<angol' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'anguill?a' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'antarctica' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'antigua' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'argentin' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'armenia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'aruba' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'australia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'austria' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'austria-hungary' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'azerbaijan' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'baden' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bahamas' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bahrain' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bangladesh' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'barbados' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bavaria' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'belarus|byelo' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'belgi' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'beliz' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'benin|dahome' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bermuda' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bhutan' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bolivia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'bonaire|eustatius|caribbean netherlands|saba' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'herzegovina|bosnia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'botswana|bechuana' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bouvet' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'brazil' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'british.?indian.?ocean' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'brunei' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'bulgaria' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'burkina|\bfaso|upper.?volta' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'burundi' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<verde' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'cambodia|kampuchea|khmer' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'cameroon' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'canada' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'cayman' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bcentral.africa' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bchad' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bchile' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<china' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'christmas.isl' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\bcocos|keeling' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'colombia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'comoro' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'kinshasa|zaire|l.opoldville|congo' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<cook' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'costa.rica|costarica' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'ivoire|ivory.coast' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'croatia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<cuba' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'bonaire|\bcuracao|\bcuraçao' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'cyprus' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'czechoslovakia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'czech repu|czechia|bohemia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'congo|kinshasa|zaire|l.opoldville|drc|rdc' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'denmark' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'djibouti' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'dominica|dominican' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'dominican.rep|dominican' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'ecuador' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'egypt' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'el.salvador|elsalvador' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'equatorial guine' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'eritrea' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'estonia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'ethiopia|abyssinia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'falkland|malvinas' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'faroe|faeroe' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'german' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'fiji' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'finland' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'martinique|france|french|\bgaul' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'french.guiana' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'french.polynesia|tahiti' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'french.southern' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'gabon' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'gambia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'georgia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'german.democratic.republic|democratic.republic.germany|east.germany|eastern germany' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'german' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'ghana|gold.coast' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'gibraltar' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'greece|hellenic|hellas' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'greenland' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'grenada' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'guadeloupe' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bguam' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'guatemala' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'guernsey' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'guinea' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'bissau|guinea' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'guyana|british.guiana' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'haiti' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'hanover' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'heard|mcdonald' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'hesse' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'hess.grand.ducal' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'holy.see|vatican|papal.st' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'honduras' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'hong.kong' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'hungary' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'iceland' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<india\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'indonesia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\<iran|persia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\<iraq|mesopotamia|\<irak' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'ireland|irish' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'isle of man' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'israel' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'italy' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'jamaica' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'japan' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'jersey' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'jordan' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'kazak' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'kenya|british.east.africa|east.africa.prot' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'kiribati' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'korea' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'north.\bkorea|dprk' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'kosovo' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'kuwait' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'kyrgyz|kirghiz|kirgiz' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\blaos\b' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'latvia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'lebanon' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'lesotho|basuto' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'liberia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'libya' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'liechtenstein' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'lithuania' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'luxem' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'macao|macau' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'madagascar|malagasy' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'malawi|nyasa' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'malaysia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'maldive' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bmali\b' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bmalta' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'marshall.isl' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'martinique' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'mauritania' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'mauritius' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bmayotte' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'mecklenburg.schwerin' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bmexic' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'micronesia|micronesia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'modena' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'monaco' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'mongolia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'montenegro' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'montserrat' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'morocco|\bmaroc|moroccan' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'mozambique' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'myanmar|burma' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'namibia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'nauru' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'nepal' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'netherlands|holand|dutch' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'netherlands.antilles' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'new.caledonia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'new.zealand' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'nicaragua' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bniger\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'nigeria' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<niue' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'norfolk' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'mariana' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'norway' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\boman\>|trucial|omanian' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'pakistan' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'palau' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'palestin|\bgaza|west.bank' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'panama' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'papua|new.guinea' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'paraguay' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'parma' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'peru' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'philippines' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'pitcairn' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'poland' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'portugal' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'puerto.rico' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'qatar' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'south.\bkorea' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'moldov|bessarabia|bassarabia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'NA' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'reunion|réunion' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'romania|rumania|roumania' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\brussia|soviet|u\.?s\.?s\.?r|socialist.?republics' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'rwanda' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'barthelemy|barthélemy' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'helena' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'kitts|\bnevis' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\blucia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<martin\>' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'miquelon' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'vincent' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'samoa' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'san.marino|sanmarino' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\bsao.tome|\bsão.tome|\bsao.tomé|\bsão.tomé' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<saudi' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'saxony' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'senegal' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'serbia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'seychell' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'leone' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'singapore' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'maarten' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<slovak' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'slovenia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'solomon.isl' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'somali' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'south.africa|southafrica' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'south.georgia|sandwich' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\bsouth.sudan' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'spain|spanish' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'sri.lanka|srilanka|ceylon' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'sudan' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'surinam|dutch.guiana' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'svalbard' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'swazi' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'sweden|swedish' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'switz|swiss' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'syria' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'taiwan|taipei|formosa' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'tajik' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'thai|\bsiam' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'macedonia|fyrom' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'NA' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<togo' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'tokelau' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'tonga' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'trinidad|tobago' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'tunisia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\<turkey|turki|turks' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'turkmen' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'caicos' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'tuscany' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'tuvalu' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'two.sicilies' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'uganda' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'ukrain' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'emirates|u\.?a\.?e\.?|united.arab.em' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'united.kingdom|britain|british|\<uk\>|england' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'tanzania' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'united.states|\<usa\>|america' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'minor.outlying.is' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'uruguay' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'uzbek' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'vanuatu|new.hebrides' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'venezuela' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'viet.nam|vietnam' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'virgin.isl' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'virgin.isl' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'futuna|wallis' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'western.sahara' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'wuerttemburg|württemburg' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'yemen' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'yemen' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'yemen' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'yugoslavia' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'zambia|rhodesia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'zanzibar' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'zimbabwe|rhodesia' $file | wc -l; done  > mypath/data/datafiles/countriesPerFileC2.txt

#regions per file
cd mypath/data/sotu_corpus2
for file in $(ls -1 |grep -i .txt ) ; do printf "$file\t" \
&& egrep -o '\<asia\>|in the pacific|pacific ocean|pacific countr|pacific area|on the pacific|of the pacific|atlantic and pacific|pacific coast|pacific railroad|norht pacific' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o '\<europ' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'africa' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'polynesia' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'caribbean' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o '\<south.america|southern.america|latin.america|western.hemisphere' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'north.america|northern america' $file | wc -l | tr -d '\n' && printf "\t" \
&& egrep -o 'middle.east|near.east' $file | wc -l | tr -d '\n' && printf "\t" \
&& grep -o 'south.asia' $file | wc -l; done  > mypath/data/datafiles/regionsPerFileC2.txt

