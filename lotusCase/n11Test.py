from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import random
import re

class N11SearchUser(HttpUser):
    wait_time = between(1, 3)  # 1-3 saniye arası bekle

    def on_start(self):
        self.client.get("/", headers=self.get_headers())

    @task
    def search_click_and_add_to_cart(self):
        # 1. Telefon araması yap
        with self.client.get("/arama?q=telefon", headers=self.get_headers(), catch_response=True) as response:
            if response.status_code == 200:
                product_links = self.extract_product_links(response.text)
                if product_links:
                    # 2. Ürün detayına git
                    product_link = random.choice(product_links)
                    with self.client.get(product_link, headers=self.get_headers(), catch_response=True) as product_response:
                        if product_response.status_code == 200:
                            # 3. Sepete ekleme simülasyonu yap
                            product_id = self.extract_product_id(product_response.text)
                            if product_id:
                                self.add_to_cart(product_id)
                            else:
                                product_response.failure("Ürün ID bulunamadı, sepete eklenemedi.")
                        else:
                            product_response.failure(f"Ürün sayfası yüklenemedi. Status code: {product_response.status_code}")
                else:
                    response.failure("Arama sonucunda ürün bulunamadı.")
            else:
                response.failure(f"Arama başarısız. Status code: {response.status_code}")

    def extract_product_links(self, html_content):
        # Arama sonucu sayfasından ürün linklerini çek
        soup = BeautifulSoup(html_content, "html.parser")
        product_elements = soup.select("a[href^='/urun/']")
        links = [a["href"] for a in product_elements if a.has_attr('href')]
        return links

    def extract_product_id(self, html_content):
        # Ürün detay sayfasından productId'yi çek
        match = re.search(r'"productId":(\d+)', html_content)
        if match:
            return match.group(1)
        return None

    def add_to_cart(self, product_id):
        # Sepete ekleme simülasyonu (gerçek istek değil, örnek endpoint)
        add_to_cart_url = "/Sepet/AddProductToBasket"
        payload = {
            "productId": product_id,
            "quantity": 1
        }
        headers = self.get_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        with self.client.post(add_to_cart_url, data=payload, headers=headers, catch_response=True) as add_response:
            if add_response.status_code == 200:
                add_response.success()
            else:
                add_response.failure(f"Sepete ekleme başarısız. Status code: {add_response.status_code}")

    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        }
