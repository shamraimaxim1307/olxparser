import bs4
import requests
import time
from pytz import timezone
from datetime import datetime

import asyncio
from aiogram import Bot, Dispatcher

API_TOKEN = '6965844134:AAHAetpAZe8_C9w_JmuhMyd2icXNYn8aDn0'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def start_bot():
    ukraine_time = timezone("Europe/Kiev")
    time_for_bot = datetime.now(ukraine_time).strftime("%H:%M")

    print('Bot is working!')
    await olxparser(time_for_bot)


async def olxparser(newest_date):
    search_words = 'iphone'
    price = '1500'
    # search%5Border%5D=created_at:desc - newer one
    # search%5Border%5D=filter_float_price:asc - cheaper one
    # search%5Border%5D=filter_float_price:desc - expensive one
    # search%5Border%5D=relevance:desc - recommended
    sort = 'search%5Border%5D=created_at:desc'

    page = requests.get(f'https://www.olx.ua/uk/elektronika/telefony-i-aksesuary/mobilnye-telefony-smartfony/q-{search_words}/'
                        f'?currency=UAH&search%5Bfilter_float_price%3Ato%5D={price}&{sort}',
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
                    f"Назва товару: {product_info_name}\nЦіна: {product_info_price}\nПосилання:"
                    f" https://www.olx.ua/{product_info_link}\nДата публікації: {product_info_date}\n")

    # Condition to show the newest goods
    if product_dates:
        if newest_date != max(product_dates).strftime("%H:%M"):
            newest_date = max(product_dates).strftime("%H:%M")
            for product in products_arr:
                if newest_date in product:
                    await bot.send_message(-1002008015106, f"Знайдено новий товар:\n{product}")
            time.sleep(60)
            await olxparser(newest_date)
        else:
            print("2")
            time.sleep(60)
            await olxparser(newest_date)
    else:
        print(product_dates)
        print("Error")


if __name__ == '__main__':
    asyncio.run(start_bot())
