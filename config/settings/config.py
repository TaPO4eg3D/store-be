PAYEER_KEY = 'PAYEER_KEY'
PAYEER_ADDITIONAL_OPTIONS_KEY = 'PAYEER_ADDITIONAL_OPTIONS_KEY'
PAYEER_MERCHANT_ID = 'PAYEER_MERCHANT_ID'


CONSTANCE_CONFIG = {
    PAYEER_KEY: (
        '', 'Payeer SecretKey', str,
    ),
    PAYEER_MERCHANT_ID: (
        '', 'Payeer Merchant ID', str,
    ),
    PAYEER_ADDITIONAL_OPTIONS_KEY: (
        '', 'Payeer Additional Options Encription Key', str,
    ),
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
