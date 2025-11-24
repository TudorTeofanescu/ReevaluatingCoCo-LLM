# CoCo Analysis: hbbfimlkfnndaplmlaabapdodpjfplkb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hbbfimlkfnndaplmlaabapdodpjfplkb/opgen_generated_files/bg.js
Line 1086: `if (request.searchEngine) {`

**Code:**

```javascript
// Background script - External message listener
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
    if (request.searchEngine) {
        searchEngine = request.searchEngine; // ← attacker-controlled
        chrome.storage.local.set({ searchEngine: request.searchEngine }); // ← Storage sink
    }
});

// Later usage - Internal message listener
chrome.runtime.onMessage.addListener((msg, sender) => {
    if (msg.message === "urlUpdated" &&
        (searchEngine === undefined || searchEngine === "" || searchEngine)) {
        let result = "";
        const updatedURL = encodeURIComponent(msg.updatedURl);
        const baseQueryURL = "mamma-forced=true";

        // Switch based on searchEngine value (read from storage earlier)
        switch (searchEngine) {
            case undefined:
            case "":
            case "googleChrome":
                result = `https://www.google.com/search?q=${updatedURL}&${baseQueryURL}`;
                break;
            case "bing":
                result = `https://www.bing.com/search?q=${updatedURL}&${baseQueryURL}`;
                break;
            case "yahoo":
                result = `https://search.yahoo.com/search?p=${updatedURL}&${baseQueryURL}`;
                break;
            // ... other hardcoded search engines
        }
    }
});
```

**Manifest Configuration:**
```json
{
  "permissions": ["tabs", "storage", "webNavigation", "management"],
  // NO externally_connectable restrictions
}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While the extension accepts external messages without origin restrictions (no `externally_connectable` in manifest means ANY external website/extension can send messages), the vulnerability is incomplete:

1. **Storage poisoning occurs:** Any external origin can send `{searchEngine: "value"}` via `chrome.runtime.sendMessage()` and poison the storage
2. **No retrieval path to attacker:** The stored `searchEngine` value is never sent back to the attacker. It's only used internally in a switch statement to select between hardcoded search engine URLs (Google, Bing, Yahoo, etc.)
3. **Hardcoded destinations only:** All search URLs in the switch statement are hardcoded trusted search engines. The attacker-controlled `searchEngine` value only selects which hardcoded URL to use, not the URL itself

Per methodology: "Storage poisoning alone (storage.set without retrieval) is NOT a vulnerability. The stored data MUST flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation (fetch to attacker URL, executeScript, etc.) to be exploitable."

The attacker can poison the storage but cannot:
- Retrieve the stored value back
- Control the destination URLs (all hardcoded)
- Execute arbitrary code
- Exfiltrate data to attacker-controlled servers

This is a configuration value that only affects which hardcoded search engine is used, with no exploitable impact.
