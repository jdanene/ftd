
# AlphaAdvantage API
- https://www.alphavantage.co/documentation/

# TdAmeritrade API

## Are there anything else I should know about when interacting with tokens?
Once you have created your first refresh token, the response will provide you with the number of seconds for when a refresh token will expire (translates to 90 days).  The only time you should create another refresh token is around the time when your previous refresh token will expire.   The same will apply for access tokens which is valid for 30 minutes.  Excessive creation of refresh and access tokens is something that we do monitor and is something we will proactively prevent when we notice unusual activity.

## Are requests to the Post Access Token API throttled?
Yes. All non-order based requests by personal use non-commercial applications are throttled to 120 per minute. Exceeding this throttle limit will provide a response with a 429 error code to inform you that the throttle limit has been exceeded. There is no need for excessive systematic creation of access and refresh tokens. The above calls to create a token should only be used when your access token is no longer valid or when your refresh token is about to expire.

Must setup sellnium for chrome
- https://selenium-python.readthedocs.io/installation.html ()

- https://github.com/alexgolec/tda-api
- https://tda-api.readthedocs.io/en/stable/
- https://medium.com/swlh/printing-money-with-td-ameritrades-api-a5cccf6a538c
- https://developer.tdameritrade.com/content/simple-auth-local-apps
- https://developer.tdameritrade.com/content/getting-started
- https://www.reddit.com/r/algotrading/comments/c81vzq/td_ameritrade_api_access_2019_guide/

