from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from ebooklib import epub
from selenium.common.exceptions import StaleElementReferenceException
import time
from selenium.common.exceptions import TimeoutException

# можно заставить авторизироваться при входе или автоматически входить на страницу для аворизации вводить логин и пароль, затем перезодить на книгу.

driver = webdriver.Chrome()
url = 'https://ranobelib.me/full-dive-eternal-phantasy/v1/c7?bid=5086&ui=2012294'
driver.get(url)
time.sleep(30)

# Ждем, пока кнопка загрузится и кликаем по ней _ это если с инфо о книге начинать
# start_reading_button = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.CLASS_NAME, 'button_primary'))
# )
# driver.delete_all_cookies()
# start_reading_button.click()

# Создание новой книги EPUB
book = epub.EpubBook()
book.set_identifier('1')
book.set_title('Название')
book.set_language('ru')

# URL первой главы
# current_chapter = 0
# max_chapters = 1  # Максимальное количество глав для загрузки

while True:
# for i in range(1):
    try:
        time.sleep(1)  # Подождем, чтобы страница загрузилась полностью
        # Получение HTML-кода текущей главы
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Извлечение названия и содержимого текущей главы
        chapter_title_element = soup.find('a', {'class': 'reader-header-action'})
        chapter_title = chapter_title_element.find('div', {'data-media-down': 'md'}).text.strip()
        chapter_content = driver.find_element(By.CLASS_NAME, 'reader-container').get_attribute('innerHTML')

        print("Chapter Title:", chapter_title)
        # print("Chapter Content:", chapter_content)

        # Если данные найдены, создаем объект главы в формате EPUB
        c = epub.EpubHtml(title=chapter_title, file_name=f'{chapter_title}.xhtml', lang='ru')
        c.content = chapter_title + chapter_content

        # c.content = "<p>Арарарар</p><p>бабабабабаб</p>"
        # Добавление главы в книгу
        book.add_item(c)
        book.spine.append(c)

        try:
            next_chapter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'button_label_right'))
            )

            href_attribute = next_chapter_button.get_attribute("href")

            if href_attribute == "#":
                # Выход из цикла, так как href равен "#"
                break
            else:
                # Ваш код для перехода к следующей главе
                next_chapter_button.click()

        except TimeoutException:
            # Обработка исключения TimeoutException
            print("Главы закончились, формирую книгу...")
            break

    except StaleElementReferenceException:
        # Если элемент не найден, ожидание нового состояния страницы
        continue

# Генерация файла EPUB
epub.write_epub('Польное погрудение.epub', book, {})
driver.quit()
print("Книга сформирована!")
