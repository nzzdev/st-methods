import pandas as pd
import os
from collections import Counter
from HanTa import HanoverTagger as ht
import nltk
from nltk.corpus import stopwords
import openpyxl
import json

# set working directory
os.chdir(os.path.dirname(__file__))

# probabilistic morphology model for German lemmatization
tagger = ht.HanoverTagger('morphmodel_ger.pgz')

# read Union election platform 2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
with open('data/2021_cdu.txt', 'r') as file:
    lines = file.read().replace('\n', ' ')
text = nltk.word_tokenize(lines, language='german')

with open('output/cdu_2021.json', 'w', encoding='utf-8') as file:
    json.dump(text, file, ensure_ascii=False, indent=4)

txt_file = open('output/cdu_2021.json', 'r')

txt_words = json.load(txt_file)

txt_words_lemma = []
for txt_word in txt_words:
    lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(txt_word.split())]
    txt_words_lemma.append(' '.join(lemma))

with open('output/cdu_lemma_2021.json', 'w', encoding='utf-8') as file:
    json.dump(txt_words_lemma, file, ensure_ascii=False, indent=4)

filtered_words = [
    word for word in txt_words_lemma if word not in stopwords.words('german')]
c = Counter(filtered_words)
l_cdu = c.most_common(500)

# read FDP election platform 2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
with open('data/2021_fdp.txt', 'r') as file:
    lines = file.read().replace('\n', ' ')
text = nltk.word_tokenize(lines, language='german')

with open('output/fdp_2021.json', 'w', encoding='utf-8') as file:
    json.dump(text, file, ensure_ascii=False, indent=4)

txt_file = open('output/fdp_2021.json', 'r')

txt_words = json.load(txt_file)

txt_words_lemma = []
for txt_word in txt_words:
    lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(txt_word.split())]
    txt_words_lemma.append(' '.join(lemma))

with open('output/fdp_lemma_2021.json', 'w', encoding='utf-8') as file:
    json.dump(txt_words_lemma, file, ensure_ascii=False, indent=4)

filtered_words = [
    word for word in txt_words_lemma if word not in stopwords.words('german')]
c = Counter(filtered_words)
l_fdp = c.most_common(500)

# read SPD election platform 2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
with open('data/2021_spd.txt', 'r') as file:
    lines = file.read().replace('\n', ' ')
text = nltk.word_tokenize(lines, language='german')

with open('output/spd_2021.json', 'w', encoding='utf-8') as file:
    json.dump(text, file, ensure_ascii=False, indent=4)

txt_file = open('output/spd_2021.json', 'r')

txt_words = json.load(txt_file)

txt_words_lemma = []
for txt_word in txt_words:
    lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(txt_word.split())]
    txt_words_lemma.append(' '.join(lemma))

with open('output/spd_lemma_2021.json', 'w', encoding='utf-8') as file:
    json.dump(txt_words_lemma, file, ensure_ascii=False, indent=4)

filtered_words = [
    word for word in txt_words_lemma if word not in stopwords.words('german')]
c = Counter(filtered_words)
l_spd = c.most_common(500)

# read Linke election platform 2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
with open('data/2021_linke.txt', 'r') as file:
    lines = file.read().replace('\n', ' ')
text = nltk.word_tokenize(lines, language='german')

with open('output/linke_2021.json', 'w', encoding='utf-8') as file:
    json.dump(text, file, ensure_ascii=False, indent=4)

txt_file = open('output/linke_2021.json', 'r')

txt_words = json.load(txt_file)

txt_words_lemma = []
for txt_word in txt_words:
    lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(txt_word.split())]
    txt_words_lemma.append(' '.join(lemma))

with open('output/linke_lemma_2021.json', 'w', encoding='utf-8') as file:
    json.dump(txt_words_lemma, file, ensure_ascii=False, indent=4)

filtered_words = [
    word for word in txt_words_lemma if word not in stopwords.words('german')]
c = Counter(filtered_words)
l_linke = c.most_common(500)

# read AfD election platform 2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
with open('data/2021_afd.txt', 'r') as file:
    lines = file.read().replace('\n', ' ')
text = nltk.word_tokenize(lines, language='german')

with open('output/afd_2021.json', 'w', encoding='utf-8') as file:
    json.dump(text, file, ensure_ascii=False, indent=4)

txt_file = open('output/afd_2021.json', 'r')

txt_words = json.load(txt_file)

txt_words_lemma = []
for txt_word in txt_words:
    lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(txt_word.split())]
    txt_words_lemma.append(' '.join(lemma))

with open('output/afd_lemma_2021.json', 'w', encoding='utf-8') as file:
    json.dump(txt_words_lemma, file, ensure_ascii=False, indent=4)

filtered_words = [
    word for word in txt_words_lemma if word not in stopwords.words('german')]
c = Counter(filtered_words)
l_afd = c.most_common(500)

# read Freie Wähler election platform 2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
with open('data/2021_fw.txt', 'r') as file:
    lines = file.read().replace('\n', ' ')
text = nltk.word_tokenize(lines, language='german')

with open('output/fw_2021.json', 'w', encoding='utf-8') as file:
    json.dump(text, file, ensure_ascii=False, indent=4)

txt_file = open('output/fw_2021.json', 'r')

txt_words = json.load(txt_file)

txt_words_lemma = []
for txt_word in txt_words:
    lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(txt_word.split())]
    txt_words_lemma.append(' '.join(lemma))

with open('output/fw_lemma_2021.json', 'w', encoding='utf-8') as file:
    json.dump(txt_words_lemma, file, ensure_ascii=False, indent=4)

filtered_words = [
    word for word in txt_words_lemma if word not in stopwords.words('german')]
c = Counter(filtered_words)
l_fw = c.most_common(500)

# read Grüne election platform 2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
with open('data/2021_gruene.txt', 'r') as file:
    lines = file.read().replace('\n', ' ')
text = nltk.word_tokenize(lines, language='german')

with open('output/gruene_2021.json', 'w', encoding='utf-8') as file:
    json.dump(text, file, ensure_ascii=False, indent=4)

txt_file = open('output/gruene_2021.json', 'r')

txt_words = json.load(txt_file)

txt_words_lemma = []
for txt_word in txt_words:
    lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(txt_word.split())]
    txt_words_lemma.append(' '.join(lemma))

with open('output/gruene_lemma_2021.json', 'w', encoding='utf-8') as file:
    json.dump(txt_words_lemma, file, ensure_ascii=False, indent=4)

filtered_words = [
    word for word in txt_words_lemma if word not in stopwords.words('german')]
c = Counter(filtered_words)
l_gruene = c.most_common(500)

# create data frames for each party
df_cdu = pd.DataFrame(l_cdu, columns=['Wort', 'Zahl'])
df_spd = pd.DataFrame(l_spd, columns=['Wort', 'Zahl'])
df_fdp = pd.DataFrame(l_fdp, columns=['Wort', 'Zahl'])
df_gruene = pd.DataFrame(l_gruene, columns=['Wort', 'Zahl'])
df_linke = pd.DataFrame(l_linke, columns=['Wort', 'Zahl'])
df_afd = pd.DataFrame(l_afd, columns=['Wort', 'Zahl'])
df_fw = pd.DataFrame(l_fw, columns=['Wort', 'Zahl'])

# save results to excel file
writer = pd.ExcelWriter('result_most_common_2021.xlsx', engine='openpyxl')
df_cdu.to_excel(writer, sheet_name='Union', index=False)
df_spd.to_excel(writer, sheet_name='SPD', index=False)
df_fdp.to_excel(writer, sheet_name='FDP', index=False)
df_gruene.to_excel(writer, sheet_name='Grüne', index=False)
df_linke.to_excel(writer, sheet_name='Linke', index=False)
df_afd.to_excel(writer, sheet_name='AfD', index=False)
df_fw.to_excel(writer, sheet_name='Freie Wähler', index=False)
writer.save()
