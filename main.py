from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from ebooklib import epub
from selenium.common.exceptions import StaleElementReferenceException
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# регистрация не работает

def main():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    # reg(driver)
    download(driver)
    driver.quit()
    print("Книга сформирована!")


def download(driver):
    time.sleep(5)
    # Вставьте ссылку на первую главу ранобэ
    ranobe_url = 'https://ranobelib.me/ru/24701--the-bears-bear-a-bare-kuma-novel/read/v6/c127'
    driver.get(ranobe_url)

    time.sleep(5)

    # title = driver.find_element(By.CLASS_NAME, 'reader-header-action__text').text
    title = driver.find_element(By.CLASS_NAME, 'qu_qx').text
    print("Начали парсинг книги: " + title)

    # Создание новой книги EPUB
    book = epub.EpubBook()
    book.set_identifier('1')
    book.set_title(title)
    book.set_language('ru')

    # Создаем объект оглавления
    toc = []


    while True:
    # for i in range(6):
        try:
            # Подождем, чтобы страница загрузилась полностью
            time.sleep(3)

            # Получение HTML-кода текущей главы
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Извлечение названия главы (ее номера)
            links_with_chapter = soup.find_all('a', class_="qu_b7 qu_b0")
            chapter_title = links_with_chapter[0].find('div', class_='qu_qy', attrs={"data-media-down": "sm"}).text.strip()

            # Извлечение содержимого главы
            chapter_title = soup.find('h1', class_='jp_bo').text.strip()
            paragraphs = soup.find_all('p', {'data-paragraph-index': True})
            chapter_content = ''.join([str(p) for p in paragraphs])

            print("Добавлена: ", chapter_title)

            # Если данные найдены, создаем объект главы в формате EPUB
            c = epub.EpubHtml(title=chapter_title, file_name=f'{chapter_title}.xhtml', lang='ru')
            c.content = chapter_title + chapter_content
            toc.append(c)

            # Добавление главы в книгу
            book.add_item(c)
            book.spine.append(c)

            try:
                next_chapter_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'qq_a6'))  # Ищем кнопку "Вперед" или "К Тайтлу"
                )

                button_text = next_chapter_button.find_element(By.TAG_NAME, 'span').text

                if button_text == "Вперёд":  # Если кнопка "Вперед"
                    next_chapter_button.click()
                elif button_text == "К Тайтлу":  # Если кнопка "К Тайтлу"
                    # Ваш код для выхода к тайтлу
                    print("Главы закончились, формирую книгу...")
                    break

            except TimeoutException:
                # Обработка исключения TimeoutException
                print("Главы закончились, формирую книгу...")

        except StaleElementReferenceException:
            # Если элемент не найден, ожидание нового состояния страницы
            continue

    # Создаем объект оглавления
    book.toc = tuple(toc)

    # Устанавливаем оглавление в книгу
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Заменяем недопустимые символы в названии файла
    cleaned_title = ''.join(c if c.isalnum() or c.isspace() else '_' for c in title)

    # Формируем имя файла EPUB
    output_filename = f"{cleaned_title}.epub"

    # Генерация файла EPUB
    epub.write_epub(output_filename, book, {})


# Для книг 16+ нужна регистрация
def reg(driver):
    url_login = 'https://ranobelib.me/'
    driver.get(url_login)

    enter_button = driver.find_element(By.XPATH, "//a[contains(@class,'header__sign-in')]")
    enter_button.click()

    # Открываем страницу входа
    # url_login = 'https://lib.social/login'
    # driver.get(url_login)
    time.sleep(5)

    # Находим элемент ввода логина по его имени
    login_input = driver.find_element(By.XPATH, "//input[@name='email']")
    # Вводим текст в поле
    login_input.send_keys("liqror")

    # Находим элемент ввода пароля по его имени
    password_input = driver.find_element(By.XPATH, "//input[@name='password']")
    # Вводим текст в поле
    password_input.send_keys("borg2003")

    # Находим кнопку "Войти" и нажимаем на нее
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")
    login_button.click()


if __name__ == "__main__":
    main()