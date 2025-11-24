# CoCo Analysis: fpcfpmdeagolgbijbhbmaelnenmnlaml

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 5 (all duplicate detections of same flow pattern for different stock symbols)

---

## Sink: fetch_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fpcfpmdeagolgbijbhbmaelnenmnlaml/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch';
Line 1103: const priceMatch = html.match(/<div class="quote__close">Rs\.(\d+\.\d+)<\/div>/);
Line 1104: return priceMatch ? parseFloat(priceMatch[1]) : 'N/A';
Line 1032: const numericPrice = Math.floor(parseFloat(price));
Line 1033: chrome.storage.sync.set({ [stock]: numericPrice.toString() });

**Code:**

```javascript
// bg.js - Lines 1001-1051
function fetchStockData(stocks, showBadge, forceFetch = false) {
  chrome.storage.sync.get(['enabledStocks', ...stocks], function(result) {
    const enabledStocks = result.enabledStocks || stocks;

    stocks.forEach((stock) => {
      if (!enabledStocks.includes(stock)) {
        completed++;
        return;
      }

      fetch(`https://dps.psx.com.pk/company/${stock}`) // ← hardcoded backend URL
        .then((response) => response.text())
        .then((html) => {
          const price = extractPriceFromHTML(html);
          if (price !== 'N/A') {
            const numericPrice = Math.floor(parseFloat(price));
            chrome.storage.sync.set({ [stock]: numericPrice.toString() });
            newPrices.push(numericPrice);
            newStocks.push(stock);
          }
        })
        .catch((error) => {
          console.error(`Error fetching data for ${stock}:`, error);
        });
    });
  });
}

// bg.js - Lines 1102-1105
function extractPriceFromHTML(html) {
  const priceMatch = html.match(/<div class="quote__close">Rs\.(\d+\.\d+)<\/div>/);
  return priceMatch ? parseFloat(priceMatch[1]) : 'N/A';
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows FROM hardcoded backend URL (`https://dps.psx.com.pk/`) which is the Pakistan Stock Exchange's official website. This is a trusted external data source that the extension uses to fetch stock prices. The extension is a stock price tracker that fetches publicly available stock market data from the official Pakistan Stock Exchange website. The `stock` parameter comes from a predefined list of stock symbols, not from attacker input. According to the methodology, data from hardcoded backend URLs (even external ones that are trusted data sources) is considered trusted infrastructure, not an attacker-controllable source.
