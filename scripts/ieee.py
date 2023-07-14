import requests
from bs4 import BeautifulSoup
import openpyxl

# set up the search URL
url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
params = {"queryText": "AI", "newsearch": "true"}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# send the search request and get the results page
response = requests.get(url, params=params, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# check if there are search results
results_qty = soup.find("span", {"class": "results-qty"})
if results_qty is None:
    print("No search results found.")
    total_results = 0
else:
    total_results = int(results_qty.text.strip().split()[0])

# create a workbook and add a worksheet
workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.title = "Search Results"

# write the header row to the worksheet
worksheet.append(["Title", "Abstract", "Authors", "Year", "Month", "Keywords"])

# loop through all search result pages
for i in range(1, (total_results // 25) + 2):
    # send the search request and get the results page
    params = {"queryText": "AI", "newsearch": "true", "pageNumber": i}
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # loop through all search results on the current page
    for article in soup.select(".List-results-items"):
        # get the HTML link for the current article and send a request to get the article page
        article_link = "https://ieeexplore.ieee.org" + article.select_one(".title a").get("href")
        article_response = requests.get(article_link, headers=headers)
        article_soup = BeautifulSoup(article_response.text, "html.parser")

        # extract the information for the current article and write it to the worksheet
        title = article.select_one(".title a").text.strip()
        abstract = article.select_one(".description span").text.strip()
        authors = ", ".join([author.text.strip() for author in article.select(".authors .ng-star-inserted")])
        year = article.select_one(".publisher-info .year").text.strip()
        month = article.select_one(".publisher-info .month").text.strip()
        keywords = ", ".join([keyword.text.strip() for keyword in article_soup.select(".art-keywords-list li")])

        worksheet.append([title, abstract, authors, year, month, keywords])

# save the workbook
workbook.save("IEEE_Results_2023.xlsx")
