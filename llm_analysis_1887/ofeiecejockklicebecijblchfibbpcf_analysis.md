# CoCo Analysis: ofeiecejockklicebecijblchfibbpcf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_body_innerText → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ofeiecejockklicebecijblchfibbpcf/opgen_generated_files/cs_0.js
Line 470: `barcodeRegex.exec(document.body.innerText)` → `productBarcode[0]`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ofeiecejockklicebecijblchfibbpcf/opgen_generated_files/bg.js
Line 972: Barcode flows to fetch URL construction

**Code:**

```javascript
// Content script - extracts barcode from page content
function extractProductData() {
  const barcodeRegex = /\b\d{13}\b/; // Matches 13-digit barcodes
  const productBarcode = barcodeRegex.exec(document.body.innerText); // ← page content

  if (productBarcode) {
    console.log("Extracted Product Barcode:", productBarcode[0]);
    return productBarcode[0]; // ← attacker can control via page content
  }
  return null;
}

// Content script sends to background
const barcode = extractProductData();
if (barcode) {
  chrome.runtime.sendMessage({ action: "checkProduct", barcode }, (response) => {
    // Handle response
  });
}

// Background script - fetches from hardcoded API
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'checkProduct' && message.barcode) {
    const barcode = message.barcode; // ← attacker-controlled barcode

    // Hardcoded trusted API endpoint
    const apiUrl = `https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/healthref-europe-rapex-en/records?select=product_name%2C%20product_description%2C%20alert_level%2C%20alert_country%2C%20risk_legal_provision%2C%20rapex_url&where=product_barcode%20%3D%20${barcode}&limit=1`;

    fetch(apiUrl) // Fetch to hardcoded trusted API
      .then(response => response.json())
      .then(data => {
        sendResponse({ matches: data.results });
      });
  }
  return true;
});
```

**Classification:** FALSE POSITIVE

**Reason:** Data TO hardcoded backend URL (trusted infrastructure). While webpage content (barcode from document.body.innerText) flows to a fetch() call, the destination is a hardcoded, trusted public API (https://public.opendatasoft.com). The attacker only controls a query parameter value used to look up product safety information. This is legitimate extension functionality, not a vulnerability.
