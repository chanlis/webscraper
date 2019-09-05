# Web Scraper

Parses fund holdings from [EDGAR](https://www.sec.gov/edgar/searchedgar/companysearch.html) given a ticker or CIK and writes the holding's name and value to a file.

To get started, run the following command in the project folder with a CIK and filename for the output.
```
scrapy crawl edgar -a cik=[cik] -o [filename].csv
```

Some example CIK:
- Gates Foundation | `0001166559`
- Caledonia | `0001166559`
- Peak6 Investments LLC | `0001756111`
- Kemnay Advisory Services Inc. | `0001555283`
- HHR Asset Management, LLC | `0001397545`
- Benefit Street Partners LLC | `0001543160`
- Okumus Fund Management Ltd. | `0001496147`
- PROSHARE ADVISORS LLC | `0001357955`
- TOSCAFUND ASSET MANAGEMENT LLP | `0001439289`
- Black Rock | `0001086364`
