import csv  # Importing the CSV module for reading and writing CSV files
from pkgutil import get_data  # Importing get_data function from pkgutil module
import requests  # Importing the requests module for making HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for HTML parsing
import re  # Importing the re module for regular expressions
import os  # Importing the os module for interacting with the operating system
import time  # Importing the time module for adding delays

def convert_to_price(byte_data):
    """
    Converts byte data (containing price) to a price string without currency symbol.

    Args:
        byte_data: The byte data representing the price information.

    Returns:
        The price as a string without currency symbol (e.g., "12495") or "Not Available".
    """
    if isinstance(byte_data, bytes):  # Checking if the input is a byte string
        try:
            # Decode assuming UTF-8 encoding (adjust if needed)
            text_data = byte_data.decode('utf-8')  # Decoding byte data to text
            # Extract price portion (assuming specific format)
            price_part = text_data.split(":")[-1].strip()  # Extracting price from text
            # Remove currency symbol (assuming it's the first character)
            price_without_currency = price_part[1:].replace(",", "")  # Removing currency symbol and commas
            return price_without_currency  # Returning the price as a string
        except (UnicodeDecodeError, IndexError):
            pass  # Handle decoding errors or invalid format
    return "Not Available"  # Returning "Not Available" if price cannot be extracted

def extract_product_details_and_info(url):
    """
    Extracts product details and information from the provided URL.

    Args:
        url (str): The URL of the product page.

    Returns:
        Tuple containing product details: (product_name, asin, original_price, discounted_price, product_rating).
    """
    try:
        time.sleep(2)  # Adding a delay to avoid blocking by amazon
        # Sending an HTTP GET request to the URL with a custom user-agent header
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})
        soup = BeautifulSoup(response.content, 'html.parser')  # Parsing the HTML content

        asin_match = re.search(r'/dp/([A-Z0-9]+)', url)  # Searching for ASIN in the URL
        if asin_match:
            asin = asin_match.group(1)  # Extracting ASIN from the URL
        else:
            asin = None

        product_name = url.split('/')[3].replace("-", " ")  # Extracting product name from the URL

        original_price_element = soup.find('span', {'class': 'a-size-small aok-offscreen'})  # Finding original price element
        original_price =( original_price_element.string.strip().encode('utf-8') if original_price_element else 'Not Available')  # Extracting original price
        original_price=convert_to_price(original_price)  # Converting original price to string

        discounted_price_element = soup.find('span', {'class': 'a-price-whole'})  # Finding discounted price element
        discounted_price = discounted_price_element.text.strip() if discounted_price_element else 'Not Available'  # Extracting discounted price

        product_rating_element = soup.find('span', {'class': 'a-icon-alt'})  # Finding product rating element
        product_rating = product_rating_element.text.strip() if product_rating_element else 'Not Available'  # Extracting product rating

        return product_name, asin, original_price, discounted_price, product_rating  # Returning product details
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")  # Printing error message if an exception occurs
        return None, None, None, None, None  # Returning None for all product details if an exception occurs

def read_urls_from_csv(csv_file):
    """
    Reads URLs from a CSV file.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        List of URLs extracted from the CSV file.
    """
    urls = []  # Initializing an empty list to store URLs
    with open(csv_file, 'r') as file:  # Opening the CSV file in read mode
        reader = csv.DictReader(file)  # Creating a CSV reader object
        for row in reader:
            urls.append(row['URL'])  # Appending URLs from the 'URL' column to the list
    return urls  # Returning the list of URLs

def get_unique_output_file(output_csv_file):
    """
    Generates a unique output file name to avoid overwriting existing files.

    Args:
        output_csv_file (str): Name of the output CSV file.

    Returns:
        Unique output file name.
    """
    base_name, ext = os.path.splitext(output_csv_file)  # Splitting the file name and extension
    count = 1  # Initializing a counter for generating unique file names
    while os.path.exists(output_csv_file):  # Checking if the file already exists
        output_csv_file = f"{base_name}_{count}{ext}"  # Modifying the file name to make it unique
        count += 1  # Incrementing the counter
    return output_csv_file  # Returning the unique output file name

def main():
    """
    Main function to execute the scraping process.
    """
    try:
        input_csv_path = input("Enter the path to the CSV file containing Amazon product URLs: ")  # Asking user to input the path to the CSV file
        input_csv_path = input_csv_path.strip('"')  # Stripping double quotes from the file path if present

        if not os.path.isfile(input_csv_path):  # Checking if the input file exists
            print(f"Error: File '{input_csv_path}' does not exist.")  # Printing error message if the file does not exist
            return

        output_csv_file = 'output_details.csv'  # Setting the default output CSV file name

        if os.path.exists(output_csv_file):  # Checking if the default output file already exists
            choice = input(f"'{output_csv_file}' already exists. Do you want to overwrite it? (y/n): ").lower()  # Asking user for confirmation
            if choice != 'y':  # Checking user's choice
                output_csv_file = get_unique_output_file(output_csv_file)  # Generating a unique output file name

        urls = read_urls_from_csv(input_csv_path)  # Reading URLs from the input CSV file

        with open(output_csv_file, 'w', newline='') as outfile:  # Opening the output CSV file in write mode
            writer = csv.writer(outfile)  # Creating a CSV writer object
            writer.writerow(['URL', 'Product Name', 'ASIN', 'Original Price', 'Discounted Price', 'Product Rating'])  # Writing header row

            for url in urls:  # Looping through each URL
                product_name, asin, original_price, discounted_price, product_rating = extract_product_details_and_info(url)  # Extracting product details
                writer.writerow([url, product_name, asin, original_price, discounted_price, product_rating])  # Writing product details to CSV

        print(f"Scraping completed. Results saved in '{output_csv_file}'.")  # Printing success message
    except Exception as e:
        print(f"An error occurred: {e}")  # Printing error message if an exception occurs

if __name__ == '__main__':
    main()  # Calling the main function if the script is executed directly
