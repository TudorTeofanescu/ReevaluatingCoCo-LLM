# CoCo Analysis: bgpadfnpdioelkliedjlecnnlpegpkap

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 12 (all duplicates of the same flow pattern)

---

## Sink: fetch_source → fetch_resource_sink (All 12 detections)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgpadfnpdioelkliedjlecnnlpegpkap/opgen_generated_files/bg.js
Line 265    var responseText = 'data_from_fetch';

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgpadfnpdioelkliedjlecnnlpegpkap/opgen_generated_files/cs_0.js
Line 502    const page = new DOMParser().parseFromString(html, 'text/html').body;
Line 673    var items = page.querySelectorAll('.games-list-item');
Line 677    const element = items[i];
Line 511    gameItem.href = gameItem.href.replace('dekudeals', 'eshop-prices').replace('www.', '');
```

**Code:**

```javascript
// Content script (cs_0.js line 481)
function loadEshopPricesPage() {
    chrome.runtime.sendMessage(
        { contentScriptQuery: 'queryEshopPrice', title: encodedTitle, currency: currency },
        response => parseEshopPricesPage(response)); // ← HTML from backend
}

// Background script (bg.js line 965)
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        if (request.contentScriptQuery === "queryEshopPrice") {
            const baseSearchUrl = "https://eshop-prices.com/games?q={0}&currency={1}" // ← Hardcoded backend
            const url = baseSearchUrl.replace('{0}', request.title).replace('{1}', request.currency);

            fetch(url) // ← Fetch to hardcoded backend URL
                .then(response => response.text())
                .then(text => sendResponse(text)) // ← Returns HTML from eshop-prices.com
                .catch(error => console.error(error))
            return true;
        }
        // ... other handlers
    });

// Content script (cs_0.js line 501)
function parseEshopPricesPage(html) {
    const page = new DOMParser().parseFromString(html, 'text/html').body; // ← Parse HTML from backend

    const gameItem = parseGameItems(page);
    if (!gameItem) {
        console.log('CANNOT FIND GAME AT ESHOP-PRICES.COM');
        return;
    }

    let divWrapper = createAndAppendDivWrapper();
    gameItem.href = gameItem.href.replace('dekudeals', 'eshop-prices').replace('www.', ''); // ← Line 511

    loadTop3Prices(gameItem.href); // ← Uses href from eshop-prices.com response

    // ... rest of DOM manipulation
}

// Content script (cs_0.js line 672)
function parseGameItems(page) {
    var items = page.querySelectorAll('.games-list-item'); // ← Line 673: Query parsed HTML
    const normalizedSearchTitle = NormalizeTitle(title);

    for (let i = 0; i < items.length; i++) {
        const element = items[i]; // ← Line 677: Iterate over items
        gameTitleEl = element.querySelector(".games-list-item-title > h5");
        if (!gameTitleEl) {
            continue;
        }

        if (NormalizeTitle(gameTitleEl.innerText) === normalizedSearchTitle) {
            return element; // ← Returns element with href attribute
        }
    }
    // ... additional search logic
}

// Content script (cs_0.js line 487)
function loadTop3Prices(url) {
    chrome.runtime.sendMessage(
        { contentScriptQuery: 'queryEshopGamePage', url: url }, // ← URL from eshop-prices.com
        null,
        parseTop3Prices);
}

// Background script (bg.js line 985)
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        // ...
        else if (request.contentScriptQuery === "queryEshopGamePage") {
            fetch(request.url) // ← Fetch sink: uses URL from eshop-prices.com response
                .then(response => response.text())
                .then(text => sendResponse({text, url : request.url}))
                .catch(error => console.error(error))
            return true;
        }
    });
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (Trusted Infrastructure). The entire data flow originates from a hardcoded backend URL (`https://eshop-prices.com`):

1. Extension fetches game search results from `https://eshop-prices.com/games?q=...` (hardcoded)
2. Parses HTML response from eshop-prices.com
3. Extracts `href` attributes from game items in the response
4. Uses those hrefs to make subsequent fetch requests back to eshop-prices.com

While CoCo correctly traces data flow from fetch response → DOM parsing → href extraction → subsequent fetch, this is NOT a vulnerability because:

- The initial fetch is to a hardcoded trusted backend (`eshop-prices.com`)
- The extracted URLs are from HTML content served by the developer's own backend
- Any manipulation of these URLs would require compromising the eshop-prices.com backend
- Per methodology: "Compromising developer infrastructure is separate from extension vulnerabilities"

This is the classic "data FROM hardcoded backend → processing → request TO backend" pattern, which is explicitly marked as FALSE POSITIVE in the methodology (Section "False Positive Patterns" - X. Hardcoded Backend URLs).

There is no external attacker entry point - the content script only runs on `https://www.dekudeals.com/items/*` (per manifest.json), and all data flows through the extension's own trusted backend at eshop-prices.com.
