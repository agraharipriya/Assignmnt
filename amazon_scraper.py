import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


# Function to scrape product details from a single page
def scrape_product_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []

        # Find all product elements on the page
        product_elements = soup.find_all('div', {'data-asin': True})

        for product in product_elements:
            product_link = product.find('a', {'class': 'a-link-normal'})

            # Check if the product link element exists
            if product_link:
                product_url = f"https://www.amazon.in{product_link['href']}"
            else:
                product_url = 'N/A'

            # Attempt to extract the product name
            product_name_element = product.find('span', {'class': 'a-text-normal'})
            product_name = product_name_element.text if product_name_element else 'N/A'

            # Attempt to extract the product price
            product_price_element = product.find('span', {'class': 'a-price-whole'})
            product_price = product_price_element.text if product_price_element else 'N/A'

            # Attempt to extract the product rating
            product_rating_element = product.find('span', {'class': 'a-icon-alt'})
            product_rating = product_rating_element.text.split(' ')[0] if product_rating_element else 'N/A'

            # Attempt to extract the number of reviews
            num_reviews_element = product.find('span', {'class': 'a-size-base'})
            num_reviews = num_reviews_element.text if num_reviews_element else '0'

            products.append({
                'Product URL': product_url,
                'Product Name': product_name,
                'Product Price': product_price,
                'Rating': product_rating,
                'Number of Reviews': num_reviews
            })

        return products
    else:
        print(f"Failed to retrieve the page: {url}")
        return []


# Function to scrape additional product details from a single product page
def scrape_product_details(product_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(product_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            description = soup.find('div', {'id': 'productDescription'}).text.strip()
        except AttributeError:
            description = 'N/A'

        try:
            asin = soup.find('th', text='ASIN').find_next('td').text.strip()
        except AttributeError:
            asin = 'N/A'

        try:
            product_description = soup.find('th', text='Product Description').find_next('td').text.strip()
        except AttributeError:
            product_description = 'N/A'

        try:
            manufacturer = soup.find('th', text='Manufacturer').find_next('td').text.strip()
        except AttributeError:
            manufacturer = 'N/A'

        return {
            'Description': description,
            'ASIN': asin,
            'Product Description': product_description,
            'Manufacturer': manufacturer
        }
    else:
        print(f"Failed to retrieve the product page: {product_url}")
        return {}


# Main function to scrape Amazon product data
def scrape_amazon_products(base_url, num_pages):
    all_products = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}&page={page}"
        print(f"Scraping page {page}...")

        products_on_page = scrape_product_page(url)
        all_products.extend(products_on_page)

        time.sleep(2)  # Add a delay to avoid being blocked

    product_details = []

    for product in all_products:
        print(f"Scraping details for {product['Product Name']}...")
        details = scrape_product_details(product['Product URL'])
        product_details.append({**product, **details})

        time.sleep(2)  # Add a delay to avoid being blocked

    return product_details


if __name__ == "__main__":
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
    num_pages = 20  # Number of pages to scrape

    product_data = scrape_amazon_products(base_url, num_pages)

    # Create a DataFrame
    df = pd.DataFrame(product_data)

    # Save the DataFrame to a CSV file
    csv_filename = r"C:\Users\Priya Agrahari\OneDrive\Desktop\Assignmnt\amazon_products.csv"

    df.to_csv(csv_filename, index=False)

    print(f"Scraping completed. Data saved to '{csv_filename}'.")