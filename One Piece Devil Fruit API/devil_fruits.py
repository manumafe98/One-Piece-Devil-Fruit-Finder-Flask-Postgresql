import time
import selenium.common.exceptions
from model import db, FruitsDb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

PARAMECIA_DIV = "/html/body/div[4]/div[3]/div[2]/main/div[3]/div[2]/div/div[2]"
ZOAN_DIV = "/html/body/div[4]/div[3]/div[2]/main/div[3]/div[2]/div/div[4]"
LOGIA_DIV = "/html/body/div[4]/div[3]/div[2]/main/div[3]/div[2]/div/div[6]"


class DevilFruits:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def get_fruits(self, div):
        self.driver.get("https://onepiece.fandom.com/wiki/Devil_Fruit")
        time.sleep(1)
        div_element = self.driver.find_element(By.XPATH, div)
        time.sleep(1)
        span_elements = div_element.find_elements(By.TAG_NAME, "span")
        time.sleep(1)
        excluded_links = ["https://onepiece.fandom.com/wiki/Vegapunk", "https://onepiece.fandom.com/wiki/Caesar_Clown",
                          "https://onepiece.fandom.com/wiki/MADS"]
        href_list = [span.find_element(By.CSS_SELECTOR, "div > a").get_attribute("href") for span in span_elements if
                     span.find_element(By.CSS_SELECTOR, "div > a").get_attribute("href") not in excluded_links]
        return href_list

    def get_fruit_info(self, array):
        href_list = array
        for link in href_list:
            self.driver.get(link)
            time.sleep(1)
            self.driver.maximize_window()
            time.sleep(1)
            primary_anchor_tag = self.driver.find_element(
                By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[2]/div[1]/div[1]/div/a[1]").text
            secondary_anchor_tag = self.driver.find_element(
                By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[2]/div[1]/div[1]/div/a[2]").text
            if "Non-Canon" in primary_anchor_tag or "Non-Canon" in secondary_anchor_tag:
                continue
            try:
                fruit_name = self.driver.find_element(
                    By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]"
                              "/div[2]/div/aside/section/div[2]/div").text.split("\n")[0]
            except selenium.common.exceptions.NoSuchElementException:
                try:
                    fruit_name = self.driver.find_element(
                        By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]"
                                  "/div[2]/div/aside/section/div[3]/div").text.split("\n")[0]
                except selenium.common.exceptions.NoSuchElementException:
                    fruit_name = self.driver.find_element(
                        By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]"
                                  "/div[1]/div/aside/section/div[2]/div").text.split("\n")[0]

            if "(" in fruit_name:
                fruit_name = fruit_name.split("(")[0]
            elif "[" in fruit_name:
                fruit_name = fruit_name.split("[")[0]

            try:
                current_user = self.driver.find_element(
                    By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]"
                              "/div[2]/div/aside/section/div[8]/div").text.split("[")[0]
            except selenium.common.exceptions.NoSuchElementException:
                try:
                    current_user = self.driver.find_element(
                        By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]"
                                  "/div[2]/div/aside/section/div[7]/div").text.split("[")[0]
                except selenium.common.exceptions.NoSuchElementException:
                    current_user = self.driver.find_element(
                        By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]"
                                  "/div[1]/div/aside/section/div[7]/div").text.split("[")[0]

            if "\n" in current_user:
                current_user = current_user.split("\n")[0]

            try:
                fruit_type_elem = self.driver.find_element(
                    By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]/div[2]/div/aside/section/div[6]/div")
                for fruit_type in fruit_type_elem.find_elements(By.CSS_SELECTOR, "div > a"):
                    if "Chapter" in fruit_type.text:
                        fruit_type_elem = self.driver.find_element(
                            By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]/div[2]/div/aside/section/div[7]/div")
            except selenium.common.exceptions.NoSuchElementException:
                fruit_type_elem = self.driver.find_element(
                    By.XPATH, "/html/body/div[4]/div[3]/div[2]/main/div[3]/div[1]/div/aside/section/div[6]/div")

            types = [fruit_type.text for fruit_type in fruit_type_elem.find_elements(By.CSS_SELECTOR, "div > a")]

            if len(types) > 1:
                fruit_type = ", ".join(types)
                new_fruit = FruitsDb(fruit_name=fruit_name,
                                     fruit_type=fruit_type,
                                     current_user=current_user)
                db.session.add(new_fruit)
                db.session.commit()
            else:
                new_fruit = FruitsDb(fruit_name=fruit_name,
                                     fruit_type=types[0],
                                     current_user=current_user)
                db.session.add(new_fruit)
                db.session.commit()
        self.driver.quit()

    def scrape_devil_fruits(self):
        paramecia_list = self.get_fruits(PARAMECIA_DIV)
        zoan_list = self.get_fruits(ZOAN_DIV)
        logia_list = self.get_fruits(LOGIA_DIV)

        final_list = paramecia_list + zoan_list + logia_list
        final_list = list(dict.fromkeys(final_list))

        self.get_fruit_info(final_list)
