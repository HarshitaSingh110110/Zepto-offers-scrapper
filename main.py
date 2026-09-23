
import re
import json
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


PROFILE_DIR = "zepto_profile"
OUTPUT_FILE = "offers.json"
SCREENSHOT_FILE = "payment_offers.png"


def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def is_bank_or_card_offer(title):
    text = title.lower()

    card_terms = [
        "credit card",
        "credit cards",
        "debit card",
        "debit cards"
    ]

    bank_terms = [
        "sbi",
        "state bank",
        "icici",
        "axis bank",
        "hdfc",
        "indian bank",
        "indusind bank",
        "rbl bank",
        "idfc",
        "hsbc",
        "punjab national bank",
        "pnb",
        "federal bank",
        "yes bank",
        "dbs bank",
        "idbi bank",
        "jana bank",
        "indian overseas bank",
        "au ",
        "novio",
        "visa",
        "rupay",
        "mastercard"
    ]

    return (
        any(term in text for term in card_terms)
        or any(term in text for term in bank_terms)
    )


def is_rupay_upi_offer(title, nearby_text):
    title_lower = title.lower()
    nearby_lower = nearby_text.lower()

    if "rupay" not in title_lower:
        return False

    unwanted_terms = [
        "upi",
        "bhim",
        "paytm",
        "amazon pay upi",
        "mobikwik upi",
        "jupiter upi",
        "bajaj pay"
    ]

    return any(term in nearby_lower for term in unwanted_terms)


def extract_discount(text):
    patterns = [
        r"\b\d+%\s+(?:off\s+)?(?:up\s+to|upto)\s+₹[\d,]+",
        r"\b\d+%\s+off\s+up\s+to\s+₹[\d,]+",
        r"\b\d+%\s+off\b",
        r"\bflat\s+₹[\d,]+\s+(?:off|cashback)\b",
        r"₹[\d,]+\s+off\b",
        r"₹[\d,]+\s+cashback\b",
        r"\b(?:up\s+to|upto)\s+₹[\d,]+\s+cashback\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return normalize_spaces(match.group(0))

    return ""


def extract_minimum_order(text):
    patterns = [
        r"orders?\s+above\s+₹[\d,]+",
        r"transactions?\s+above\s+₹[\d,]+",
        r"minimum\s+order\s+(?:value\s+)?(?:of\s+)?₹[\d,]+",
        r"orders?\s+of\s+₹[\d,]+\s+and\s+above"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return normalize_spaces(match.group(0))

    return ""


def extract_promo_code(text):
    patterns = [
        r"\bZEP[A-Z0-9]{4,}\b",
        r"\bVISA[A-Z0-9]{4,}\b",
        r"\bSBI[A-Z0-9]{4,}\b",
        r"\bNOVIO[A-Z0-9]{3,}\b",
        r"\bINDIANBANK[A-Z0-9]{3,}\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0).upper()

    return ""


def extract_bank_or_card(title):
    text = title.lower()

    mappings = [
        ("indian overseas bank", "Indian Overseas Bank"),
        ("punjab national bank", "Punjab National Bank"),
        ("federal bank", "Federal Bank"),
        ("idfc first", "IDFC FIRST Bank"),
        ("idbi bank", "IDBI Bank"),
        ("indusind bank", "IndusInd Bank"),
        ("indian bank", "Indian Bank"),
        ("yes bank", "YES Bank"),
        ("rbl bank", "RBL Bank"),
        ("dbs bank", "DBS Bank"),
        ("jana bank", "Jana Bank"),
        ("hsbc bank", "HSBC Bank"),
        ("axis bank", "Axis Bank"),
        ("icici bank", "ICICI Bank"),
        ("sbi", "SBI"),
        ("state bank", "SBI"),
        ("hdfc", "HDFC"),
        ("novio", "Novio Credit Card"),
        ("visa", "Visa"),
        ("rupay", "RuPay"),
        ("mastercard", "Mastercard"),
        ("au ", "AU Bank")
    ]

    for keyword, name in mappings:
        if keyword in text:
            return name

    if "credit card" in text:
        return "Credit Card"

    if "debit card" in text:
        return "Debit Card"

    return ""


def find_offer_starts(text):
    pattern = re.compile(r"(?i)(?=(?:save\b|flat\b|get\b))")
    starts = []

    for match in pattern.finditer(text):
        position = match.start()

        if not starts:
            starts.append(position)
        elif position - starts[-1] > 12:
            starts.append(position)

    return starts


def extract_offer_candidates(raw_text):
    text = normalize_spaces(raw_text)
    starts = find_offer_starts(text)
    candidates = []

    for index, start in enumerate(starts):
        if index + 1 < len(starts):
            end = starts[index + 1]
        else:
            end = len(text)

        block = normalize_spaces(text[start:end])

        if len(block) < 15:
            continue

        card_match = re.search(
            r"(?i)^(.*?\b(?:credit cards?|debit cards?)\b)",
            block
        )

        if not card_match:
            continue

        title = normalize_spaces(card_match.group(1))
        title = title.strip(" -:|")

        if not is_bank_or_card_offer(title):
            continue

        after_title = block[len(card_match.group(1)):]
        immediate_text = after_title[:350]

        if is_rupay_upi_offer(title, immediate_text):
            continue

        candidates.append({
            "title": title,
            "block": block,
            "after_title": after_title
        })

    return candidates


def remove_duplicates(offers):
    unique_offers = []
    seen = set()

    for offer in offers:
        key = normalize_spaces(offer["title"]).lower()

        if key in seen:
            continue

        seen.add(key)
        unique_offers.append(offer)

    return unique_offers


def create_final_offer(offer):
    title = offer["title"]
    block = offer["block"]
    after_title = offer["after_title"]

    discount = extract_discount(title)

    if not discount:
        discount = extract_discount(block[:300])

    minimum_order = extract_minimum_order(block[:500])

    promo_code = extract_promo_code(
        title + " " + after_title[:300]
    )

    bank_or_card = extract_bank_or_card(title)

    return {
        "offer_title": title,
        "bank_or_card": bank_or_card,
        "discount": discount,
        "minimum_order": minimum_order,
        "promo_code": promo_code
    }


def main():
    with sync_playwright() as p:
        print("\nOpening Zepto...")

        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={
                "width": 1400,
                "height": 900
            }
        )

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        try:
            page.goto(
                "https://www.zepto.com/?cart=open",
                wait_until="domcontentloaded",
                timeout=60000
            )

            print("Waiting for Zepto page...")
            page.wait_for_timeout(5000)

            print("Looking for Payment Offers...")

            payment_button = page.get_by_text(
                "View payment offers",
                exact=False
            )

            try:
                payment_button.first.wait_for(
                    state="visible",
                    timeout=15000
                )

                payment_button.first.click()

            except PlaywrightTimeoutError:
                print("Payment Offers button not found automatically.")
                print("Please open Payment Offers manually.")
                page.wait_for_timeout(30000)

            page.wait_for_timeout(4000)

            print("Payment Offers opened.")

            page.screenshot(
                path=SCREENSHOT_FILE,
                full_page=True
            )

            body_text = page.locator("body").inner_text()
            body_text = normalize_spaces(body_text)

            offers = extract_offer_candidates(body_text)
            offers = remove_duplicates(offers)

            final_offers = []

            for offer in offers:
                formatted = create_final_offer(offer)

                if not formatted["offer_title"]:
                    continue

                if not is_bank_or_card_offer(
                    formatted["offer_title"]
                ):
                    continue

                final_offers.append(formatted)

            result = {
                "total_offers": len(final_offers),
                "offers": final_offers
            }

            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    result,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            print("\n" + "=" * 70)
            print("FINAL BANK / CARD OFFERS")
            print("=" * 70)

            print(
                f"\nTotal valid offers: {len(final_offers)}\n"
            )

            for number, offer in enumerate(
                final_offers,
                1
            ):
                print(
                    f"{number}. {offer['offer_title']}"
                )

                print(
                    f"   Bank/Card: "
                    f"{offer['bank_or_card'] or 'N/A'}"
                )

                print(
                    f"   Discount: "
                    f"{offer['discount'] or 'N/A'}"
                )

                if offer["minimum_order"]:
                    print(
                        f"   Minimum Order: "
                        f"{offer['minimum_order']}"
                    )

                if offer["promo_code"]:
                    print(
                        f"   Promo Code: "
                        f"{offer['promo_code']}"
                    )

                print()

            print("=" * 70)
            print(f"JSON saved to: {OUTPUT_FILE}")
            print(f"Screenshot saved to: {SCREENSHOT_FILE}")
            print("=" * 70)

            print(
                "\nBrowser will remain open for 10 minutes..."
            )

            time.sleep(600)

        finally:
            context.close()


if __name__ == "__main__":
    main()