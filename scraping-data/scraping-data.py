import csv
import time
import re
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def get_driver():
    options = uc.ChromeOptions()
    options.headless = False  # Ganti ke True kalau tidak mau buka jendela
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return uc.Chrome(options=options)

def get_links_from_search_page(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h6.title > a:first-child'))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, 'h6.title > a:first-child')
        links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]
        print(f"✅ Found {len(links)} drama links on {url}")
        return links
    except Exception as e:
        print(f"❌ Error loading {url}: {e}")
        return []

def get_genres_and_title(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.film-title"))
        )

        raw_title = driver.find_element(By.CSS_SELECTOR, "h1.film-title").text.strip()
        clean_title = re.sub(r"\s\(\d{4}(–\d{4})?\)$", "", raw_title)

        genre_elements = driver.find_elements(By.CSS_SELECTOR, 'li.show-genres a.text-primary')
        genres = [g.text.strip() for g in genre_elements]

        watch_elements = driver.find_elements(By.CSS_SELECTOR, '.box-body.wts a.text-primary b')
        platform = watch_elements[0].text.strip() if watch_elements else ""

        return clean_title, genres, platform
    except Exception as e:
        print(f"❌ Gagal scrape {url}: {e}")
        return None, [], ""

def save_to_csv(file_path, data):
    file_exists = os.path.exists(file_path)
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "genres", "where_to_watch"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def split_genres_to_rows(input_file="kdrama_genres.csv", output_file="flat_dramas.csv"):
    with open(input_file, newline="", encoding="utf-8") as infile, \
         open(output_file, mode="w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        writer.writerow(["title", "genre"])

        for row in reader:
            title = row["title"]
            genres = row["genres"].split(", ")
            for genre in genres:
                writer.writerow([title, genre])

def main():
    output_file = "kdrama_genres.csv"
    scraped_titles = set()

    if os.path.exists(output_file):
        with open(output_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            scraped_titles = {row["title"] for row in reader}

    driver = get_driver()

    try:
        base_url = "https://mydramalist.com/search?adv=titles&ty=68&co=3&re=2015,2023&rt=1,10&st=3&so=top&page={}"
        for page in range(1, 95):
            url = base_url.format(page)
            drama_links = get_links_from_search_page(driver, url)
            if not drama_links:
                continue

            for drama_url in drama_links:
                print(f"Scraping {drama_url}...")
                title, genres, platform = get_genres_and_title(driver, drama_url)
                if title and title not in scraped_titles:
                    data = {
                        "title": title,
                        "genres": ", ".join(genres),
                        "where_to_watch": platform
                    }
                    save_to_csv(output_file, data)
                    scraped_titles.add(title)

                    # Delay acak antara 1–3 detik
                    time.sleep(random.uniform(1.5, 3.5))

        print("✅ Semua data selesai diambil dan disimpan.")
        print("🔄 Memproses menjadi format flat...")
        split_genres_to_rows()
        print("✅ File flat_dramas.csv selesai dibuat.")
    finally:
        print("🔚 Menutup browser...")
        try:
            driver.quit()
            driver.service.process = None
        except Exception as e:
            print("❗ Gagal tutup browser dengan sempurna:", e)

if __name__ == "__main__":
    main()