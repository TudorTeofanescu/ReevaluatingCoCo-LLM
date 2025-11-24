# CoCo Analysis: feonehaohleclbngaobgacjblcpbiaon

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (duplicate detections)

---

## Sink: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/feonehaohleclbngaobgacjblcpbiaon/opgen_generated_files/bg.js
Line 1466: `gapiCall('moveData', [{ docid: items.docid, sheetname: items.sheet, id: message.id }],`
Line 1032: `xhr.send(JSON.stringify(args.body));`

**Code:**

```javascript
// Background script - External message handler (lines 1454-1473)
chrome.runtime.onMessageExternal.addListener(
  function (message, sender, sendResponse) {
    if (message.request == 'getData') {
      chrome.storage.sync.get(['docid', 'sheet'], function (items) {
        gapiCall('getData', [{ docid: items.docid, sheetname: items.sheet }],
          function (result) {
            sendResponse(result);
          });
      });
      return true;
    } else if (message.request == 'removeData') {
      chrome.storage.sync.get(['docid', 'sheet'], function (items) {
        gapiCall('moveData', [
          {
            docid: items.docid,           // ← From storage, not attacker
            sheetname: items.sheet,       // ← From storage, not attacker
            id: message.id                // ← Attacker-controlled ID
          }],
          function (result) {
            sendResponse(result);
          });
      });
      return true;
    }
  });

// The gapiCall function sends to Google APIs (hardcoded backend):
// Line 1032 in api.js: xhr.send(JSON.stringify(args.body));
// This is an XHR POST to Google Sheets/Drive APIs
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages can trigger the flow, the data is sent to Google's hardcoded API endpoints (https://www.googleapis.com/...). The manifest shows this is a Google Sheets integration extension (NoteSheet) with OAuth2 configuration for Google APIs. The attacker-controlled `message.id` is sent to the developer's own Google Sheets backend via Google APIs, which is trusted infrastructure. Per methodology: "Hardcoded backend URLs are still trusted infrastructure: Data TO/FROM developer's own backend servers = FALSE POSITIVE." The extension is designed to allow the connected website (editoy.com per externally_connectable) to interact with the user's Google Sheets data. While an attacker from editoy.com could manipulate the `id` parameter, they can only affect operations on the user's own Google Sheets (which the user has authorized), and the data goes to Google's trusted API infrastructure, not an attacker-controlled destination. This is intended functionality for a Google Sheets integration, not a vulnerability.

---
