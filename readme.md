# 🛒 Zepto Bank & Card Offers Scraper

> A Playwright-based automation project that extracts **Bank and Credit/Debit Card offers** from the Zepto checkout/payment offers section.

---

## 📌 Project Overview

This project automates the Zepto checkout flow using **Playwright** and extracts the payment offers displayed to the user.

The scraper focuses specifically on:

- 🏦 Bank Offers
- 💳 Credit/Debit Card Offers
- 💰 Discount / Cashback Details
- 📋 Offer Terms and Relevant Details

Non-payment offers such as generic coupons, delivery discounts, wallets, and unrelated promotions are filtered from the final output.

---

## 🎯 Objective

The main objective of this assessment is to automate the process of navigating to the Zepto checkout/payment section and extracting the **currently visible Bank and Card offers** in a structured and readable format.

### Workflow

```text
Zepto Website
      ↓
Open Checkout
      ↓
Open Payment Offers
      ↓
Read Visible Offers
      ↓
Filter Bank/Card Offers
      ↓
Extract Offer Details
      ↓
Display Final Results