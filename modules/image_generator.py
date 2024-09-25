import os
from typing import List
import datetime
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from PIL import Image, ImageFont, ImageDraw

from modules.utils import download_image, convert_to_currency
from modules.config import base_dir
from modules.objects import UserInteractionInfo


assets_path = os.path.join(base_dir, 'assets')


class NotoSans:
    fonts_path = f"{assets_path}/fonts/noto_sans/static"

    @staticmethod
    def regular(size):
        return ImageFont.truetype(
            font=f'{NotoSans.fonts_path}/NotoSans-Regular.ttf',
            size=size
        )

    @staticmethod
    def semibold(size):
        return ImageFont.truetype(
            font=f'{NotoSans.fonts_path}/NotoSans-SemiBold.ttf',
            size=size
        )

    @staticmethod
    def bold(size):
        return ImageFont.truetype(
            font=f'{NotoSans.fonts_path}/NotoSans-Bold.ttf',
            size=size
        )

    @staticmethod
    def extrabold(size):
        return ImageFont.truetype(
            font=f'{NotoSans.fonts_path}/NotoSans-ExtraBold.ttf',
            size=size
        )


def coin_info(user_data: UserInteractionInfo):
    def pt_to_px(pt_size: int):
        return int(pt_size * (4/3))

    def percentage_box(percentage: float) -> Image:
        percentage_box_img_size_x = 280
        percentage_box_img_size_y = 80
        percentage_box_img = Image.new(
            'RGBA',
            (
                percentage_box_img_size_x,
                percentage_box_img_size_y
            ),
            color=(0, 0, 0, 0))
        percentage_box_img_draw = ImageDraw.Draw(percentage_box_img)

        arrow_up = f'{assets_path}/images/arrow_up.png'
        arrow_down = f'{assets_path}/images/arrow_down.png'

        arrow_image: Image
        text_color: str
        if percentage >= 0:
            arrow_image = Image.open(arrow_up)
            text_color = '#008000'
        else:
            arrow_image = Image.open(arrow_down)
            text_color = '#FF0000'

        arrow_image_size = 32
        arrow_image_margin = 28
        arrow_image_x = 0
        arrow_image_y = arrow_image_margin
        arrow_image = arrow_image.resize((arrow_image_size, arrow_image_size))
        percentage_box_img.paste(
            arrow_image,
            (
                arrow_image_x,
                arrow_image_y
            ),
            arrow_image
        )

        percentage_text = str(abs(percentage)) + '%'
        percentage_text_size_pt = 60
        percentage_text_margin_left = 20
        percentage_text_x = arrow_image_x + arrow_image_size + percentage_text_margin_left
        percentage_text_y = 0
        percentage_box_img_draw.text(
            xy=(
                percentage_text_x,
                percentage_text_y
            ),
            text=percentage_text,
            font=NotoSans.semibold(percentage_text_size_pt),
            fill=text_color
        )

        percentage_box_bytes_io = BytesIO()
        percentage_box_img.save(percentage_box_bytes_io, 'png')
        percentage_box_bytes_io.seek(0)
        percentage_box_img = Image.open(percentage_box_bytes_io)

        return percentage_box_img

    def price_chart(charts) -> Image:
        axes = plt.axes()
        axes.spines['top'].set_visible(False)
        axes.spines['right'].set_visible(False)
        axes.spines['bottom'].set_color('white')
        axes.spines['left'].set_color('white')
        axes.yaxis.set_major_locator(MaxNLocator(8))
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')

        dates = []
        prices = []
        for data_point in charts:
            dates.append(datetime.datetime.fromtimestamp(data_point[0]))
            prices.append(data_point[1])

        chart_color: str
        if prices[0] <= prices[-1]:
            text_color = '#008000'
        else:
            text_color = '#FF0000'

        plt.plot(dates, prices, color=text_color)
        plt.grid(linewidth=0.2)
        plt.xticks([])
        plt.locator_params(axis='y', nbins=5)

        figure = plt.gcf()
        chart_bytes_io = BytesIO()
        figure.savefig(chart_bytes_io, transparent=True, dpi=200)
        figure.clear()
        chart_bytes_io.seek(0)
        figure_img = Image.open(chart_bytes_io)

        return figure_img

    img_size_x = 1280
    img_size_y = 1600
    img_padding = 80
    img = Image.new('RGB', (img_size_x, img_size_y), color="#121212")
    img_draw = ImageDraw.Draw(img)

    watermark = Image.open(f'{assets_path}/images/logo.png')
    watermark_size = 768
    watermark = watermark.resize((watermark_size, watermark_size))
    watermark_x = (img_size_x - watermark_size) // 2
    watermark_y = (img_size_y - watermark_size) // 2
    img.paste(
        watermark,
        (
            watermark_x,
            watermark_y
        )
    )

    coin_data = user_data.chosen_coin_data
    coin_charts_data = user_data.chosen_coin_charts_data

    coin_icon_size = 160
    coin_icon_raw = BytesIO(download_image(coin_data['icon']))
    coin_icon = Image.open(coin_icon_raw)
    coin_icon = coin_icon.resize((coin_icon_size, coin_icon_size))
    img.paste(
        coin_icon,
        (
            img_padding,
            img_padding
        ),
        coin_icon
    )

    coin_name = coin_data['name']
    if len(coin_name) > 17:
        coin_name = coin_name[:18] + '...'
    coin_name_size_pt = 120
    coin_name_size_y = pt_to_px(coin_name_size_pt)
    coin_name_margin = 10
    coin_name_x = img_padding
    coin_name_y = img_padding + coin_icon_size + coin_name_margin
    img_draw.text(
        xy=(
            coin_name_x,
            coin_name_y
        ),
        text=coin_name,
        font=NotoSans.extrabold(coin_name_size_pt),
        fill="#FFFFFF",
    )

    coin_symbol = coin_data['symbol']
    coin_symbol_size_pt = 60
    coin_symbol_size_y = pt_to_px(coin_symbol_size_pt)
    coin_symbol_x = img_padding
    coin_symbol_y = coin_name_y + coin_name_size_y
    img_draw.text(
        xy=(
            coin_symbol_x,
            coin_symbol_y
        ),
        text=coin_symbol,
        font=NotoSans.regular(coin_symbol_size_pt),
        fill="#777777",
    )

    coin_price_raw = coin_data['price']
    coin_price = convert_to_currency(coin_price_raw)
    coin_price_size_pt = 120
    coin_price_size_y = pt_to_px(coin_price_size_pt)
    coin_price_x = img_size_x - img_padding
    coin_price_y = img_padding
    img_draw.text(
        xy=(
            coin_price_x,
            coin_price_y
        ),
        text=coin_price,
        font=NotoSans.semibold(coin_price_size_pt),
        fill="#FFFFFF",
        anchor='rt'
    )

    coin_price_btc_raw = coin_data['priceBtc']
    coin_price_btc = convert_to_currency(coin_price_btc_raw, currency='BTC ')
    coin_price_btc_size_pt = 60
    coin_price_btc_size_y = pt_to_px(coin_price_btc_size_pt)
    coin_price_btc_offset_y = 30
    coin_price_btc_x = img_size_x - img_padding
    coin_price_btc_y = coin_price_y + coin_price_size_y - coin_price_btc_offset_y
    img_draw.text(
        xy=(
            coin_price_btc_x,
            coin_price_btc_y
        ),
        text=coin_price_btc,
        font=NotoSans.regular(coin_price_btc_size_pt),
        fill="#777777",
        anchor='rt'
    )

    coin_price_change_1h_text = 'Chg(1h)%'
    coin_price_change_1h = percentage_box(coin_data['priceChange1h'])
    coin_price_change_1d_text = 'Chg(24h)%'
    coin_price_change_1d = percentage_box(coin_data['priceChange1d'])
    coin_price_change_1w_text = 'Chg(7d)%'
    coin_price_change_1w = percentage_box(coin_data['priceChange1w'])

    coin_price_change_size_pt = 60
    coin_price_change_size_x = 280
    coin_price_change_size_y = 80
    coin_price_change_margin_top = 30
    coin_price_change_margin_left = 140

    coin_price_change_x_1h = img_padding
    coin_price_change_x_1d = img_padding + coin_price_change_size_x + coin_price_change_margin_left
    coin_price_change_x_1w = img_padding + 2 * (coin_price_change_size_x + coin_price_change_margin_left)

    coin_price_change_y_text = coin_symbol_y + coin_symbol_size_y + coin_price_change_margin_top
    coin_price_change_y = coin_price_change_y_text + coin_price_change_size_y + coin_price_change_margin_top

    img_draw.text(
        xy=(
            coin_price_change_x_1h,
            coin_price_change_y_text
        ),
        text=coin_price_change_1h_text,
        font=NotoSans.semibold(coin_price_change_size_pt),
        fill="#777777",
    )
    img.paste(
        coin_price_change_1h,
        (
            coin_price_change_x_1h,
            coin_price_change_y
        ),
        coin_price_change_1h
    )
    img_draw.text(
        xy=(
            coin_price_change_x_1d,
            coin_price_change_y_text
        ),
        text=coin_price_change_1d_text,
        font=NotoSans.semibold(coin_price_change_size_pt),
        fill="#777777",
    )
    img.paste(
        coin_price_change_1d,
        (
            coin_price_change_x_1d,
            coin_price_change_y
        ),
        coin_price_change_1d
    )
    img_draw.text(
        xy=(
            coin_price_change_x_1w,
            coin_price_change_y_text
        ),
        text=coin_price_change_1w_text,
        font=NotoSans.semibold(coin_price_change_size_pt),
        fill="#777777",
    )
    img.paste(
        coin_price_change_1w,
        (
            coin_price_change_x_1w,
            coin_price_change_y
        ),
        coin_price_change_1w
    )

    chart = price_chart(coin_charts_data[1])
    chart_x_raw, chart_y_raw = chart.getprojection()
    chart_size_x = len(chart_x_raw)
    chart_size_y = len(chart_y_raw)
    chart_offset_x = 45
    chart_x = img_padding - chart_offset_x
    chart_y = img_size_y - chart_size_y
    img.paste(
        chart,
        (chart_x,
         chart_y),
        chart
    )

    chart_desc = f'Price change for {coin_charts_data[0]} period'
    chart_desc_size_pt = 45
    chart_desc_size_y = pt_to_px(chart_desc_size_pt)
    chart_desc_offset_y = 10
    chart_desc_x = img_size_x / 2
    chart_desc_y = img_size_y - chart_desc_size_y - chart_desc_offset_y
    img_draw.text(
        xy=(
            chart_desc_x,
            chart_desc_y
        ),
        text=chart_desc,
        font=NotoSans.regular(chart_desc_size_pt),
        fill="#BBBBBB",
        anchor='mt'
    )

    img_bytes_io = BytesIO()
    img.save(img_bytes_io, 'png')
    img_bytes_io.seek(0)

    return img_bytes_io.getvalue()

    
