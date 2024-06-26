# Art analyzer, v0.1
Автор: Раев Андрей

#### Описание:
Проект Art Analyzer предназначен для анализа изображений путём создания различных картинок на основе цветовой информации, а также других характеристик изображения.

#### Константы:
1. `aa_scale_cof`: Коэффициент масштабирования, применяемый в рендере изображения с гистограммами и прочими. Это значение уменьшает "ступенчатый" эффект при рендеринге изображений, но может незначительно влиять на время исполнения.
2. `font_name`: Название файла шрифта, который используется для подписей на изображениях.
3. `palette_depth`: Глубина палитры, указывает на количество цветов, которые будут отображаться на палитре (для `analys.png`).
4. `palette_color_expand`: Чувствительность палитры, регулирует, насколько два цвета могут отличаться, чтобы считаться разными цветами при формировании палитры (для `analys.png`).
5. `bg_color`: Цвет заднего фона в изображении с цветовым анализом (`analys.png`).
6. `bw_threshold`: Порог черного и белого для создания карты черных и белых областей. Значение указывает, какие области считать черно-белыми на изображении (для `white_black_holes.png`).

#### Инструкции по использованию:
0. Установите необходимое окружение: Python3.X + Pillow
1. Запустите скрипт `art_analyzer.py`.
2. Введите путь к файлу изображения (желательно формата `.png`).
3. Программа выполнит анализ изображения и создаст несколько файлов.

#### Вывод программы:
   - `original.png`: оригинал изображения.
   - `original_flipped.png`: оригинал изображения, отраженный по горизонтали.
   - `white_black_holes.png`: карта белых и чёрных областей (места, где цвет изображения почти белый или почти черный).
   - `warm_cold.png`: температурная карта изображения.
   - `hue_and_grey.png`: карта цвета и оттенков серого.
   - `analys.png`: файл с аналитикой изображения.

#### Быстрый старт:
1. Скачайте и запустите файл `Image Analyzer v1.0.exe` (Может потребоваться отключение антивируса, так как файл не подписан).
2. Введите путь к изображению.
3. Дождитесь завершения анализа.
4. После выполнения анализа вы найдете результаты в созданных папках (имя папки = имя изображения) с соответствующими изображениями.
