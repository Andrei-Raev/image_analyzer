# Art analyzer v0.1
# Автор: Raev Andrei
#####################
# --==[ IMPORTS ] ==--
import colorsys
import os
import shutil
from math import sin, cos, pi

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

# --== [DEFINES] ==--
aa_scale_cof = 8  # Коэффициент масштабирования, применяемый в рендере изображения с гистограммами и пр. Убирает "ступенчатый" эффект
font_name = "font.otf"  # Файл шрифта, которым будут сделаны подписи на изображениях
palette_depth = 15  # глубина палитры
palette_color_expand = 50  # Чувствительность палитры (не рекомендуется сильно понижать)
bg_color = (90, 90, 90)  # Цвет заднего фона в изображении с цветовым анализом
bw_threshold = 3  # Порог черного и белого для одноименной карты (больше число - больше область)

# --== [INPUTS] ==--
path = input("Введите путь к файлу (желательно .png)\n")  # Изображение, которое будет проанализировано


# --== [FUNCTIONS] ==--
def sl_grad(x_l: int, y_l: int, size_l, grid=False) -> bool:  # Создает эффект полосочек и шашечек
    if grid:
        return sin(x_l * size_l) * sin(y_l * size_l) >= 0
    else:
        return sin((x_l + y_l) * size_l) >= 0


# --== [SCRIPT] ==--
if not path.count(".") == 1:  # Проверка введенного имени файла
    print("Error! Недопустимое имя файла!")
    input()
    exit(1)

img = Image.open(path).convert("RGBA")  # Загрузка изображения
size = width, height = img.size  # определение размеров

dir_path = path.split(".")[0]  # Создание конечной папки с конечными изображениями
try:
    os.mkdir(dir_path)
except FileExistsError:
    shutil.rmtree(dir_path, ignore_errors=True)
    os.mkdir(dir_path)

img.save(dir_path + "/original.png")  # Сохранение оригинального изображения
img.transpose(Image.FLIP_LEFT_RIGHT).save(
    dir_path + "/original_flipped.png")  # Сохранение оригинального изображения, отраженного по горизонтали

pixels = img.load()  # Загрузка изображения попиксельно

# Создание изображения для черных и белых дыр
white_black_holes = ImageEnhance.Contrast(img).enhance(.25)
white_black_holes_mask = Image.new("RGBA", size, (0, 0, 0, 0))
white_black_holes_mask_pix = white_black_holes_mask.load()

# Создание темпиратурной карты
warm_cold = ImageEnhance.Contrast(img).enhance(.35)
warm_cold_mask = Image.new("RGBA", size, (0, 0, 0, 0))
warm_cold_mask_pix = warm_cold_mask.load()

# Создание карты для цвета (hue) и оттенков серого
hue_and_grey = Image.new("RGBA", size, (0, 0, 0, 0))
hue_and_grey_pix = hue_and_grey.load()

r_mid, g_mid, b_mid = 0, 0, 0  # создание счетчика среднего значения
hue_wheel = [0 for _ in range(360)]  # создания "гистограммы" цвета
sat_wheel = [0 for _ in range(256)]  # создание "гистограммы" насыщенности
val_wheel = [0 for _ in range(256)]  # создание гистограммы
grey_wheel = [0 for _ in range(256)]  # создание ч/б гистограммы

same_matrix = []
all_colors = {}

# Анализ изображения
for y in range(height):
    if y % 250 == 0:
        print(f"{round(y / height * 100, 2)}%")

    for x in range(width):
        r, g, b, a = pixels[x, y]
        r_mid += r
        g_mid += g
        b_mid += b

        t = '%02x%02x%02x' % (r, g, b)
        if t in all_colors.keys():
            all_colors[t] += 1
        else:
            all_colors.update({t: 1})

        if sum((r, g, b)) <= bw_threshold:
            white_black_holes_mask_pix[x, y] = (28, 28, 128, 256) if sl_grad(x, y, .5) else (3, 3, 250, 255)
        elif sum((r, g, b)) >= 255 * bw_threshold:
            white_black_holes_mask_pix[x, y] = (250, 3, 3, 255) if sl_grad(x, y, .5) else (118, 28, 28, 256)

        h, s, v = colorsys.rgb_to_hsv(r, g, b)

        if r == g and r == g and g == b:
            grey_wheel[int(v)] += 1

            if r > 128:
                hue_and_grey_pix[x, y] = tuple([r, g, b]) if sl_grad(x, y, .5, grid=True) else tuple(
                    [r - 25, g - 25, b - 25])
            else:
                hue_and_grey_pix[x, y] = tuple([r, g, b]) if sl_grad(x, y, .5, grid=True) else tuple(
                    [r + 25, g + 25, b + 25])

        else:
            hue_wheel[int(h * 360)] += 1
            sat_wheel[int(s * 255)] += 1
            val_wheel[int(v)] += 1

            if 330 / 360 > h > 80 / 360:
                warm_cold_mask_pix[x, y] = (30, 90, 170, 256 // 3) if sl_grad(x, y, .5, grid=True) else (
                    5, 65, 145, 256 // 3)
            else:
                warm_cold_mask_pix[x, y] = (226, 116, 86, 256 // 3) if sl_grad(x, y, .5, grid=True) else (
                    201, 91, 61, 256 // 3)

            hue_and_grey_pix[x, y] = tuple([int(jj * 255) for jj in colorsys.hsv_to_rgb(h, .95, .9)])

# Вычисление среднего цвета
r_mid /= width * height
g_mid /= width * height
b_mid /= width * height

print("Saving images...")

# Сохранение карты черных и белых дыр
white_black_holes.alpha_composite(white_black_holes_mask, (0, 0))
white_black_holes.save(dir_path + "/white_black_holes.png")

# Сохранение тепло-холодной карты
warm_cold.alpha_composite(warm_cold_mask, (0, 0))
warm_cold.save(dir_path + "/warm_cold.png")

# Сохранение карты цветов и оттенков серого
hue_and_grey.save(dir_path + "/hue_and_grey.png")

# Сохранение изображения с графиками
analys = Image.new("RGB", (2048 * aa_scale_cof, 1024 * aa_scale_cof), bg_color)

draw = ImageDraw.Draw(analys)

max_hue = max(hue_wheel)
color_limit = 550
for i in list(enumerate(hue_wheel)):
    if (i[1] >= color_limit or (hue_wheel[(i[0] + 1) % len(hue_wheel)] < color_limit and hue_wheel[
        (i[0] - 1) % len(hue_wheel)] < color_limit)):
        if i[1] >= color_limit:
            tmp = .5 + i[1] / max_hue / 2
        else:
            tmp = 0

        draw.polygon((
            aa_scale_cof * (366 + (220 - 210 * i[1] / max_hue) * cos(2 * pi * (i[0] / 360) - pi / 4)),
            aa_scale_cof * (366 + (220 - 210 * i[1] / max_hue) * sin(2 * pi * (i[0] / 360) - pi / 4)),
            aa_scale_cof * (366 + 256 * cos(2 * pi * (i[0] / 360) - pi / 4)),
            aa_scale_cof * (366 + 256 * sin(2 * pi * (i[0] / 360) - pi / 4)),
            aa_scale_cof * (366 + 256 * cos(2 * pi * (i[0] / 360 + 1 / 360) - pi / 4)),
            aa_scale_cof * (366 + 256 * sin(2 * pi * (i[0] / 360 + 1 / 360) - pi / 4)),
            aa_scale_cof * (366 + (220 - 210 * i[1] / max_hue) * cos(2 * pi * (i[0] / 360 + 1 / 360) - pi / 4)),
            aa_scale_cof * (366 + (220 - 210 * i[1] / max_hue) * sin(2 * pi * (i[0] / 360 + 1 / 360) - pi / 4))),
            fill=tuple([int(i * 255) for i in colorsys.hsv_to_rgb(i[0] / 360, .8, min(tmp, 1))]))

    else:
        qual_steps = 10
        for j in range(qual_steps):
            if (hue_wheel[(i[0] + 1) % len(hue_wheel)] >= color_limit and hue_wheel[
                (i[0] - 1) % len(hue_wheel)] >= color_limit):
                tmp = .5 + hue_wheel[(i[0] + 1) % len(hue_wheel)] * (j / qual_steps) / max_hue / 2 + hue_wheel[
                    (i[0] - 1) % len(hue_wheel)] * (1 - j / qual_steps) / max_hue / 2
            elif hue_wheel[(i[0] + 1) % len(hue_wheel)] >= color_limit:
                tmp = j / qual_steps * .5 + hue_wheel[(i[0] + 1) % len(hue_wheel)] / max_hue / 2
            else:
                tmp = (.5 + hue_wheel[(i[0] - 1) % len(hue_wheel)] / max_hue / 2) - j / qual_steps * .5 + hue_wheel[
                    (i[0] - 1) % len(hue_wheel)] / max_hue / 2

            draw.polygon((
                aa_scale_cof * (366 + 220 * cos(2 * pi * (i[0] / 360 + j / qual_steps / 360) - pi / 4)),
                aa_scale_cof * (366 + 220 * sin(2 * pi * (i[0] / 360 + j / qual_steps / 360) - pi / 4)),
                aa_scale_cof * (366 + 256 * cos(2 * pi * (i[0] / 360 + j / qual_steps / 360) - pi / 4)),
                aa_scale_cof * (366 + 256 * sin(2 * pi * (i[0] / 360 + j / qual_steps / 360) - pi / 4)),
                aa_scale_cof * (366 + 256 * cos(2 * pi * (i[0] / 360 + (j + 1) / qual_steps / 360) - pi / 4)),
                aa_scale_cof * (366 + 256 * sin(2 * pi * (i[0] / 360 + (j + 1) / qual_steps / 360) - pi / 4)),
                aa_scale_cof * (366 + 220 * cos(2 * pi * (i[0] / 360 + (j + 1) / qual_steps / 360) - pi / 4)),
                aa_scale_cof * (366 + 220 * sin(2 * pi * (i[0] / 360 + (j + 1) / qual_steps / 360) - pi / 4))),
                fill=tuple([int(i * 255) for i in colorsys.hsv_to_rgb(i[0] / 360, .8, min(tmp, 1))]))

max_val = max(val_wheel)
for i in list(enumerate(val_wheel)):
    draw.polygon((
        768 * aa_scale_cof, (128 + i[0] * 2) * aa_scale_cof,
        (768 + 36) * aa_scale_cof, (128 + (i[0]) * 2) * aa_scale_cof,
        (768 + 36) * aa_scale_cof, (128 + (i[0] + 1) * 2) * aa_scale_cof,
        (768) * aa_scale_cof, (128 + (i[0] + 1) * 2) * aa_scale_cof),
        tuple([int(256 - (((i[0] / 256) ** (1 / 2.2)) * 256)) for _ in range(3)]))

    draw.line(((768 + 36 + 14) * aa_scale_cof, (128 + 512 - i[0] * 2 + 1) * aa_scale_cof,
               (768 + 36 + 14 + 316 * (i[1] / max_val)) * aa_scale_cof, (128 + 512 - i[0] * 2 + 1) * aa_scale_cof),
              fill=(30, 30, 30), width=aa_scale_cof * 2)

max_sat = max(sat_wheel)
for i in list(enumerate(sat_wheel)):
    col_sell_sat = colorsys.rgb_to_hsv(r_mid / 256, g_mid / 256, b_mid / 256)
    col_sell_sat = colorsys.hsv_to_rgb(col_sell_sat[0], 1 - i[0] / 256, col_sell_sat[2])
    # print(col_sell_sat)
    draw.polygon((
        1154 * aa_scale_cof, (128 + i[0] * 2) * aa_scale_cof,
        (1154 + 36) * aa_scale_cof, (128 + (i[0]) * 2) * aa_scale_cof,
        (1154 + 36) * aa_scale_cof, (128 + (i[0] + 1) * 2) * aa_scale_cof,
        (1154) * aa_scale_cof, (128 + (i[0] + 1) * 2) * aa_scale_cof), tuple([int(jj * 255) for jj in col_sell_sat]))

    draw.line(((1140 + 36 + 28) * aa_scale_cof, (128 + 512 - i[0] * 2 + 1) * aa_scale_cof,
               (1140 + 36 + 28 + 316 * (i[1] / max_sat)) * aa_scale_cof, (128 + 512 - i[0] * 2 + 1) * aa_scale_cof),
              fill=(30, 30, 30), width=aa_scale_cof * 2)

draw.rectangle(
    (128 * aa_scale_cof, (64 + 512 + 128) * aa_scale_cof, (128 + 256) * aa_scale_cof, (1024 - 64) * aa_scale_cof),
    (int(r_mid), int(g_mid), int(b_mid)))

# Работа с палитрой
all_colors = list(map(lambda y: tuple(int(y[0][j:j + 2], 16) for j in (0, 2, 4)),
                      sorted(list(all_colors.items()), key=lambda x: x[1], reverse=True)))
res_cols = []
while all_colors:
    tt = all_colors[0]
    res_cols.append(tt)
    del all_colors[0]
    del_ofs = 0
    for i in list(enumerate(all_colors)):
        if abs(i[1][0] - tt[0]) <= palette_color_expand and abs(i[1][1] - tt[1]) <= palette_color_expand and abs(
                i[1][2] - tt[2]) <= palette_color_expand:
            del all_colors[i[0] - del_ofs]
            del_ofs += 1

for i in range(palette_depth):
    x_offset = int(512 + 1008 * (i / palette_depth))
    try:
        draw.rectangle(
            (x_offset * aa_scale_cof, (64 + 512 + 128) * aa_scale_cof,
             (x_offset + 256) * aa_scale_cof, (1024 - 64) * aa_scale_cof),
            res_cols[i])
    except IndexError:
        break

# h_font = ImageFont.truetype(font_name, 32 * aa_scale_cof)

# draw.text((128 * aa_scale_cof, 32 * aa_scale_cof), f"Аналитика {path}", font=h_font, fill=(0, 0, 0, 255))

analys = analys.resize((analys.width // aa_scale_cof, analys.height // aa_scale_cof), resample=Image.LANCZOS)
analys.save(dir_path + "/analys.png")

print('DONE!')
input()
