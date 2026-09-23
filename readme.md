# Zepto Bank & Card Offers Scraper

A Python automation project built with **Playwright** to collect Bank and Credit/Debit Card offers shown on the Zepto payment page.

## What it does

The script:

* Opens the Zepto checkout page
* Opens the Payment Offers section
* Reads the offers visible on the page
* Finds Bank and Card related offers
* Extracts useful details like discount, minimum order and promo code
* Saves the final results in JSON format

## Workflow

```text
Zepto
  ↓
Checkout
  ↓
Payment Offers
  ↓
Read Offers
  ↓
Filter Bank/Card Offers
  ↓
Extract Details
  ↓
Save Results
```

## Tech Stack

* Python
* Playwright
* Regular Expressions
* JSON

## Project Structure

```text
zepto-offers-scrapper/
│
├── main.py
├── offers.json
├── payment_offers.json
├── payment_offers.txt
├── requirements.txt
├── .gitignore
└── readme.md
```

## Why Playwright?

The payment offers on Zepto are loaded dynamically on the website. Playwright helps automate the browser and read the content that is actually displayed on the page.

It also allows the script to maintain a browser session using a persistent profile.

## Offer Details

The scraper tries to collect information such as:

* Bank name
* Card type
* Discount / cashback
* Minimum order value
* Promo code
* Offer description

## Setup

Clone the repository and open the project folder:

```bash
git clone https://github.com/HarshitaSingh110110/Zepto-offers-scrapper.git
cd Zepto-offers-scrapper
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Install Playwright browser:

```bash
playwright install chromium
```

## Run

```bash
python main.py
```

The browser will open and the script will navigate to the Zepto checkout/payment offers section.

The extracted offers are saved in:

```text
offers.json
```

## Output

Example structure:

```json
{
  "bank": "Example Bank",
  "card": "Credit Card",
  "discount": "₹150",
  "minimum_order": "₹999",
  "promo_code": "EXAMPLE150"
}
```

The actual offers may change because they depend on the offers currently displayed on Zepto.

