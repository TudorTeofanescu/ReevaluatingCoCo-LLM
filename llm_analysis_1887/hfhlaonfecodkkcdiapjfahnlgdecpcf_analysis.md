# CoCo Analysis: hfhlaonfecodkkcdiapjfahnlgdecpcf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: fetch_source → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hfhlaonfecodkkcdiapjfahnlgdecpcf/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';`

This line is in CoCo's framework code (before the third "// original" marker at line 963). The actual extension code starts at line 963.

**Code:**

```javascript
// Background script (bg.js) - Lines 971-1050
// Intercept PDF requests on LinkedIn
chrome.webRequest.onBeforeRequest.addListener(function(req) {
  chrome.storage.local.get(["pdfRequest"]).then((result) => {
    if (result.pdfRequest) {
      if (!req || !req.url) return;
      if (req.initiator && req.initiator.match(/chrome-extension/gi)) return;
      if (req.type && req.type === 'xmlhttprequest') return;

      if (req.url.match(/pdf/gi)) {
        chrome.storage.local.set({ "pdfRequest": false });
        setActiveBadgeText('...');
        getPdf(req); // Process the PDF
      }
    }
  });
}, {
  urls: ["http://*.linkedin.com/*", "https://*.linkedin.com/*"]
});

function getPdf(request) {
  // Fetch the PDF from LinkedIn
  fetch(request.url) // ← fetch_source
      .then(response => response.arrayBuffer())
      .then(arrayBuffer => {
        const profile = {
          entityTypeId: 1,
          bytes: btoa(ab2str2(arrayBuffer))
        };
        sendPdf(profile); // Send to hardcoded backend for parsing
      })
      .catch(() => {
        chrome.storage.local.set({ "pdfRequest": true });
      });
}

function sendPdf(profile) {
  const parsePdfEndpoint = 'https://app.brightmove.com/ATS/app/converter/profile/parse/bytes/v2'; // ← hardcoded backend
  fetch(parsePdfEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=UTF-8'
    },
    body: JSON.stringify(profile)
  })
      .then(response => response.json())
      .then(parsedProfile => { // ← response from hardcoded backend
        chrome.storage.local.set({ "pdfProfile": parsedProfile }); // ← storage sink
        chrome.storage.local.set({ "pdfRequest": true });
        setActiveBadgeText(':)');
      })
      .catch(() => {
        chrome.storage.local.set({ "pdfRequest": true });
      });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This involves hardcoded backend URLs (trusted infrastructure). The flow is:

1. Extension intercepts PDF requests on LinkedIn via `webRequest.onBeforeRequest`
2. Fetches the PDF content from the LinkedIn URL
3. Sends the PDF to the developer's hardcoded backend (`https://app.brightmove.com/ATS/app/converter/profile/parse/bytes/v2`) for parsing
4. Stores the parsed response FROM the hardcoded backend in `chrome.storage.local`

According to the methodology, "Data FROM hardcoded backend: `fetch('https://api.myextension.com') → response → storage.set`" is classified as FALSE POSITIVE because the developer trusts their own infrastructure. Compromising the developer's backend server is an infrastructure security issue, not an extension vulnerability. The attacker does not control the data being stored - it comes from the extension developer's trusted backend service.
