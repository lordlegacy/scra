import scrapy
import json

class JumiaSpider(scrapy.Spider):
    name = "jumia_spider"
    allowed_domains = ["jumia.co.ke"]

    def __init__(self, *args, **kwargs):
        super(JumiaSpider, self).__init__(*args, **kwargs)
        self.reviews = []
        self.product = {}

    def start_requests(self):
        headers = {
            "User-Agent": "MyBot/1.0 (https://lordlegacy.github.io/; edwinodero70@gmail.com)"
        }
        start_urls = [
            "https://www.jumia.co.ke/generic-guixia-tws-wireless-bluetooth-headsets-earphones-inpods12-148844873.html"
            # Add more product URLs here if needed
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse_product)

    def parse_product(self, response):
        # Extract product details and SKU
        self.extract_product_details(response)
        sku = self.product.get('SKU')
        
        if sku:
            # Build review URL using the extracted SKU
            review_url = f"https://www.jumia.co.ke/catalog/productratingsreviews/sku/{sku.strip(": ")}"
            yield scrapy.Request(url=review_url, headers=response.request.headers, callback=self.parse_reviews)
            print(sku, review_url)

        # Save product information to JSON
        self.save_data(self.product, 'product_data.json')

    def extract_product_details(self, response):
        def extract_xpath_text(xpath_expression):
            return response.xpath(xpath_expression).get(default='').strip()

        # Extract product information
        self.product = {
            'Title': extract_xpath_text('//h1[@class="-fs20 -pts -pbxs"]/text()'),
            'Price': extract_xpath_text('//span[@class="-b -ubpt -tal -fs24 -prxs"]/text()'),
            'Description': ''.join(response.xpath('//div[@class="markup -mhm -pvl -oxa -sc"][.//h2[text()="Description"]]//text()').getall()).strip(),
            'Features': ''.join(response.xpath('//div[@class="markup -mhm -pvl -oxa -sc"][.//h2[text()="Features & details"]]//text()').getall()).strip(),
            'Items': ', '.join(response.xpath('//div[@class="markup -pam"]//text()').getall()).strip(),
            'SKU': extract_xpath_text('//li[@class="-pvxs"]//span[@class="-b"][text()="SKU"]/following-sibling::text()')
        }

    def parse_reviews(self, response):
        reviews = response.xpath('//div[@class="cola -phm -df -d-co"]/article')
        for review in reviews:
            review_data = {
                'Rating': review.xpath('.//div[@class="stars _m _al -mvs"]/text()').get(default='').strip(),
                'Title': review.xpath('.//h3/text()').get(default='').strip(),
                'Body': review.xpath('.//p/text()').get(default='').strip(),
                'Date': review.xpath('.//div[@class="-pvs"]/span[@class="-prs"]/text()').get(default='').strip(),
            }
            self.reviews.append(review_data)

        # Save reviews data to JSON
        self.save_data(self.reviews, 'reviews.json')

    def save_data(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"{filename} saved successfully")

