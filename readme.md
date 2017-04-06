# Social Link Validation/Discovery Script

## Requirements

python 2.7+

modules: pip install unicodecsv tweepy requests beautifulsoup4

## API keys - bing, twitter, youtube

### bing: https://datamarket.azure.com/dataset/bing/search

### twitter:

https://apps.twitter.com/ https://dev.twitter.com/

consumer key

consumer secret

access token

access token secret

### youtube

https://developers.google.com/youtube/v3/getting-started

create new app, enable youtube data api

https://console.developers.google.com/apis/credentials

new credentials - api key - browser key

## Notes

API keys are listed in order one line per credential, with filename: auth_service.txt e.g. auth_bing.txt

Run all tests and ensure they all pass.

Validator.py is the main script.

All search and subscriber counter requests/results are cached. Delete the contents of the cache folder to reset/update results.

Input filename is `Social Link Validation Data - Sheet1.csv` exported from google sheets as csv, edit the filename in `validator.py`.


###Output 

extendedpresence.csv
completematch.csv
partialmatch.csv
zeromatch.csv
newaccounts.csv

