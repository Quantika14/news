import requests, json
import modules.key as KEY

def scaleserp_NEWS(target):
    key = KEY.scaleserp
    url = f"https://api.scaleserp.com/search?api_key={key}&q={target}&num=100&search_type=news"
    _JSON = requests.get(url)

    links_dates = {}

    if "news_results" in _JSON.text:
        print("BINGO!")

        news_results = json.loads(_JSON.text)["news_results"]
        
        for news in news_results:
            link = news["link"]
            if "date_utc" in news:
                date = news["date_utc"]
            else:
                date = "None"
            f = open("news.txt", "a+")
            f.write(f"{date}, {link} \n")
            f.close()
            print(f"{date} > {link}")
    else:
        print("No found.")


def main():

    target = input("Insert target: ")
    scaleserp_NEWS(target)


main()