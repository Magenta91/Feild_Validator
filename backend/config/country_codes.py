COUNTRY_PHONE_RULES = {
    "IN": {
        "name": "India",
        "digits": 10,
        "prefixes": ["6", "7", "8", "9"],
        "prefix_required": True
    },
    "SG": {
        "name": "Singapore",
        "digits": 8,
        "prefixes": ["3", "6", "8", "9"],
        "prefix_required": True
    },
    "US": {
        "name": "United States",
        "digits": 10,
        "prefixes": [],
        "prefix_required": False
    },
    "GB": {
        "name": "United Kingdom",
        "digits": 10,
        "prefixes": [],
        "prefix_required": False
    },
    "AE": {
        "name": "United Arab Emirates",
        "digits": 9,
        "prefixes": ["5"],
        "prefix_required": True
    },
    "AU": {
        "name": "Australia",
        "digits": 9,
        "prefixes": ["4"],
        "prefix_required": True
    },
}

SUPPORTED_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d-%b-%Y",
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
]

REQUIRED_COLUMNS = {
    "order_id": str,
    "product_id": str,
    "payment_mode": str,
}

VALID_PAYMENT_MODES = [
    "credit_card", "debit_card", "upi",
    "net_banking", "cash", "wallet", "emi"
]
