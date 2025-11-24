# CoCo Analysis: eogoblegiobdnfdcikffkdepdgcepkmf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_body_innerText → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eogoblegiobdnfdcikffkdepdgcepkmf/opgen_generated_files/cs_0.js
Line 29: Document_element.prototype.innerText = new Object();

**Note:** CoCo only detected this flow in framework code (Line 29 is in the CoCo mock implementation). The actual extension code begins at line 465 after the third "// original" marker.

**Code:**

```javascript
// Content script (cs_0.js) - Line 467 (actual extension code)
(function() {
  const htmlText = document.body.innerText; // Read webpage text
  const url = window.location.href; // Current page URL

  chrome.runtime.sendMessage({ htmlText: htmlText, url: url }, (response) => {
    console.log(response.status);
  });
})();

// Background script (bg.js) - Line 1003
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.htmlText && request.url) {
    console.log('URL da aba ativa:', request.url);

    // Stores the extracted HTML text and URL
    chrome.storage.local.set({
      extractedHTML: request.htmlText, // Store webpage text
      activeTabUrl: request.url
    });

    sendResponse({ status: 'Dados recebidos com sucesso' });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. The extension reads `document.body.innerText` from webpages and stores it to `chrome.storage.local`, but there is no path for an attacker to retrieve this stored data. The flow is: webpage content → storage.set, with no storage.get → attacker-accessible output (no sendResponse with storage data, no postMessage back to webpage, no fetch to attacker-controlled URL). Storage poisoning alone without a retrieval path is not exploitable according to the methodology. The extension is designed to catalog webpage content for the user's own side panel, not to send it to attackers.
