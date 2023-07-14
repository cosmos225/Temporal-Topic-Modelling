from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('stopwords')

from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}

questionlist = []

for n in range(23, 24):
    current_url = f"https://www.jmlr.org/papers/v{n}/"
    source_url_get = requests.get(current_url).text
    soup_url = BeautifulSoup(source_url_get, 'lxml')
    abstractURL_list = []
    jmlr_abstract_URL_list = []

    current_volume_table = soup_url.find("div", id="content")
    current_volume_aTag = current_volume_table.find_all("a")
    for i in range(len(current_volume_aTag)):
        if ("[abs]" in str(current_volume_aTag[i])) or (">abs<" in str(current_volume_aTag[i])):
            string1 = str(current_volume_aTag[i])
            string1 = string1.split('"')
            if ("v1/" in current_url) or ("v2/" in current_url) or ("v3/" in current_url):
                string1 = (current_url+string1[1]).replace(" ", '')
            elif("v4/" in current_url) or ("v5/" in current_url):
                string1 = (string1[1]).replace(" ", '')
            else:
                string1 = "http://www.jmlr.org"+((string1[1]).replace(" ", ''))
            abstractURL_list.append(string1)
    jmlr_abstract_URL_list.append(abstractURL_list)

    for x in range(len(jmlr_abstract_URL_list)):
        for y in range(len(jmlr_abstract_URL_list[x])):
            current_url = jmlr_abstract_URL_list[x][y]

            source_url_get = requests.get(current_url).text
            soup_url = BeautifulSoup(source_url_get, 'lxml')
            current_volume_abstract_list = []

            current_volume_table = soup_url.find("div", id="content")
            current_volume_h3Tag = current_volume_table.find_all("h3")

            r = requests.get(current_url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')

            questions = soup.find_all('div', id="content")

            string1 = str(current_volume_table).split("</h3>")
            string1 = str(string1[1]).split("<p>")
            string1 = string1[0].strip()
            # month = string1.split()[-1]

            current_volume_authors_list = []

            for item in questions:
                abstract = item.find('p', {'class': 'abstract'}).text
                tokenized_words = nltk.word_tokenize(abstract.lower())
                filtered_words = [word for word in tokenized_words if word not in stop_words]
                keywords = "; ".join(filtered_words)
                question = {
                    'Title': item.find('h2').text,
                    'Abstract': abstract,
                    'Authors': item.find('i').text,
                    'Year': f"20{n-1}",
                    'Month': '',
                    'Keywords': keywords
                }
                questionlist.append(question)

df = pd.DataFrame(questionlist)
df.to_excel('jmlr.xlsx', index=False)
print('Fin')
