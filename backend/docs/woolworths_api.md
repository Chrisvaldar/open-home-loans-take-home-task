API Overview
The Woolworths Products API provides a robust solution for querying Woolworths extensive product catalog. Users can perform product searches using a simple query input and refine results based on page size and page number, enabling efficient data navigation and retrieval.

Features:
Product Search: Input a keyword to search across Woolworth’s product database.
Pagination: Control the volume of results with parameters for page size (1-20 entries per page) and page number, allowing for scalable data fetching.
Detailed Results: Each product entry in the search result includes:
Barcode: Unique identifier for the product.
Product Name: The full name of the product.
Product Brand: Brand association of the product.
Current Price: Latest price of the product as it appears in the store.
Product Size: The size or quantity of the product package.
URL: A direct link to the product’s page on the Woolworth website for further details.
Output Example:
Query: "Kraft Singles"
Total Results: 77 products found.
Total Pages: 8, indicating the search results span across eight pages.
Current Page: 1, showing results from the first page.
Results array with detailed product information, including barcodes, names, brands, prices, sizes, and URLs.
This API is perfect for developers building applications that require access to retail product data, providing all necessary information to feature Woolworths products comprehensively.

The Woolworths Products API allows you to search for products by name or barcode, returning detailed information including barcode, product name, brand, current price, size, and a URL to the product page. Suitable for retrieving a specific number of product entries per page with pagination support.

# Woolworths RapidAPI

## Endpoints

### Price Changes
curl --request GET \
	--url 'https://woolworths-products-api.p.rapidapi.com/woolworths/price-changes/?page=1&page_size=20' \
	--header 'Content-Type: application/json' \
	--header 'x-rapidapi-host: woolworths-products-api.p.rapidapi.com' \
	--header 'x-rapidapi-key: YOUR_KEY_HERE'

### Barcode Search
curl --request GET \
  --url 'https://woolworths-products-api.p.rapidapi.com/woolworths/barcode-search/9310199012717' \
  --header 'x-rapidapi-host: woolworths-products-api.p.rapidapi.com' \
  --header 'x-rapidapi-key: YOUR_KEY_HERE'

### Product Search
curl --request GET \
	--url 'https://woolworths-products-api.p.rapidapi.com/woolworths/product-search/?query=Full%20Cream%20Milk' \
	--header 'Content-Type: application/json' \
	--header 'x-rapidapi-host: woolworths-products-api.p.rapidapi.com' \
	--header 'x-rapidapi-key: YOUR_KEY_HERE'

Refer to @woolworths_sample_response.json for sample output of Product Search with Full Cream Milk as input