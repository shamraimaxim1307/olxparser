import bs4
import requests
import time
from pytz import timezone
from datetime import datetime


def olxparser(newest_date):
    page = requests.get(
        'https://www.olx.ua/uk/elektronika/telefony-i-aksesuary/mobilnye-telefony-smartfony/q-iphone/?currency=UAH&search%5Bfilter_float_price%3Ato%5D=1500&search%5Border%5D=created_at%3Adesc',
        timeout=None)

    soup = bs4.BeautifulSoup(page.text, "html.parser")
    section = soup.find_all("div", class_="css-j0t2x2")
    products_arr = []
    product_dates = []

    for products in section:
        product = products.find_all("div", class_="css-1sw7q4x")
        for item in product:
            product_block = item.find("div", class_="css-qfzx1y")
            product_list = product_block.find("div", class_="css-1venxj6")
            product_info_block = product_list.find("div", class_="css-1apmciz")

            # Product name and price
            product_info_section = product_info_block.find("div", class_="css-u2ayx9")
            product_info_name = product_info_section.find("h6", class_="css-16v5mdi er34gjf0").get_text(strip=True)
            product_info_price = product_info_section.find("p", class_="css-tyui9s er34gjf0").get_text(strip=True)
            product_info_link = product_info_section.find("a", class_="css-z3gu2d").get("href")

            # Product date of publication
            product_info_date_section = product_info_block.find("div", class_="css-odp1qd")
            product_info_date = product_info_date_section.find("p", class_="css-1a4brun er34gjf0").get_text().split()

            # Condition to avoid older ad goods
            if product_info_date[-1] == "р.":
                continue
            else:
                # Convert timezone to Europe, Kyiv
                product_info_date = product_info_date[-1].split(":")
                product_info_date[0] = str(int(product_info_date[0]) + 3)
                product_info_date = ":".join(product_info_date)
                product_dates.append(datetime.strptime(product_info_date, '%H:%M'))

                # Output the information
                products_arr.append(
                    f"Назва товару: {product_info_name}\nЦіна: {product_info_price}\nПосилання: https://www.olx.ua/{product_info_link}\nДата публікації: {product_info_date}\n")

    # Condition to show the newest goods
    if product_dates:
        if newest_date != max(product_dates).strftime("%H:%M"):
            newest_date = max(product_dates).strftime("%H:%M")
            for product in products_arr:
                if newest_date in product:
                    print(f"Знайдено новий товар:\n{product}")
            time.sleep(60)
            olxparser(newest_date)
        else:
            time.sleep(60)
            olxparser(newest_date)
    else:
        print(product_dates)
        print("Error")


def main():
    if __name__ == "__main__":
        print("Бота запущено")
        ukraine_time = timezone("Europe/Kiev")
        time = datetime.now(ukraine_time).strftime("%H:%M")
        olxparser(time)


main()