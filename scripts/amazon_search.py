import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Initialize the Selenium driver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Function to search Amazon and get product ASIN and URL
def search_amazon(driver, product_title):
    amazon_url = "https://www.amazon.com/"
    driver.get(amazon_url)
    
    try:
        # Wait for the search box to be visible and clickable using the updated ID
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-bb-search"))
        )
        search_box.clear()
        search_box.send_keys(product_title)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3)  # Wait for the search results to load
        
        # Get the first product link from search results
        first_product = driver.find_element(By.CSS_SELECTOR, 'div.s-main-slot div.sg-col-inner h2 a')
        product_url = first_product.get_attribute('href')
        
        # Extract the ASIN from the product URL
        asin = product_url.split('/dp/')[1].split('/')[0]
        
        return product_url, asin
    except Exception as e:
        print(f"Product not found for {product_title}: {e}")
        return None, None

# Read product data from CSV
def read_csv(file_path):
    # Strip any extra spaces from column names
    return pd.read_csv(file_path).rename(columns=lambda x: x.strip())

# Write results back to CSV
def write_results(file_path, data):
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

# Main function
def main():
    input_file = '../data/products.csv'   # Updated input file path for CSV
    output_file = '../results/amazon_links_asin.csv'  # Updated output file path for CSV

    # Read the provided CSV file
    product_data = read_csv(input_file)

    # Create a list to store results
    results = []

    # Initialize the Selenium driver
    driver = init_driver()

    # Iterate through the product titles and perform search
    for index, row in product_data.iterrows():
        title = row['Product Title']  # Match the exact column name
        price = row['Price']  # Assuming there's a Price column as per the task

        print(f"Searching for product: {title}")
        
        # Perform Amazon search and extract ASIN and URL
        amazon_url, asin = search_amazon(driver, title)

        # Append results (including empty strings if no product found)
        results.append({
            "Product Title": title,
            "Price": price,
            "Amazon URL": amazon_url if amazon_url else "Not Found",
            "ASIN": asin if asin else "Not Found"
        })

    # Write results to CSV
    write_results(output_file, results)

    # Close the Selenium driver
    driver.quit()

if __name__ == "__main__":
    main()
