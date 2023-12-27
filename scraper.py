"""
    Simple web scraper app to get the current price (in AUD) of each edition of Escape from Tarkov
        features to add:
            automatically send email alert if price below certain amount
            write prices to a csv file, checking current vs most recent price on each scrape, printing the difference per edition
"""
import json
import re
import requests

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


class Scraper:
    def __init__(self, site):
        self.site = site


    def print_results(self, results):
        """
        Prints the price for each edition of Escape from Tarkov
        :param results: dict of edition(key): price(value) pairs
        :return: prints each edition and price to the terminal
        """
        print("\nEscape from Tarkov current pricing:\n(prices in AUD before tax and other fees)\n")
        for edition, amount in results.items():
            print(f"{edition}: {amount}")


    def exchange_currency(self, base_price):
        """
        Converts Tarkov's USD pricing to AUD.
        :param base_price: int price in USD
        :return: string representation of AUD pricing
        """
        response = requests.get("https://v6.exchangerate-api.com/v6/33381b5c19298ba6a2fc1d62/latest/USD")
        json_response = json.loads(response.content)
        aud_rate = json_response['conversion_rates']['AUD']
        aud_price = base_price * aud_rate
        return f"${round(aud_price, 2)}"


    def scrape(self):
        """
        Check Escape from Tarkov's website for the price of each edition of the game.
        """
        req = Request(url=self.site, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        parser = BeautifulSoup(webpage, "html.parser")

        # create a list storing each edition of the game
        editions = []
        for keyword in parser.find_all("span", {"itemprop":"keywords"}):
            edition = re.findall("(?<=\\>).* Edition", str(keyword), re.IGNORECASE)
            editions.append(edition[0])
            
        # create a list storing the price (in AUD) of each edition
        costs = []
        for price in parser.find_all("span", {"itemprop":"price"}):
            cost = re.findall("\\d*\\$", str(price))
            costs.append(self.exchange_currency(int(cost[0].replace("$", ""))))
            
        # combine editions and costs lists into a prices dict, containing each edition(key): cost(value) pair
        prices = {}
        for i in range(len(editions)):
            prices[str(editions[i])] = str(costs[i])
            
        self.print_results(prices)


tarkov = "https://www.escapefromtarkov.com/preorder-page"
Scraper(tarkov).scrape()