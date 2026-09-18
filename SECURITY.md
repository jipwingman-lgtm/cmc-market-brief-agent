# Security

## API keys

Do not commit a CoinMarketCap API key.

If a key is used, set it only in the local environment:

    export CMC_API_KEY="..."

The default demo works with CoinMarketCap keyless public endpoints and therefore does not require a secret.

The application never writes the value of CMC_API_KEY into evidence files or normal output.

## Reporting

Do not place API keys, account details, or other secrets in public issues, pull requests, screenshots, demo recordings, or logs.

If a key is accidentally exposed, rotate it immediately in the provider account.
