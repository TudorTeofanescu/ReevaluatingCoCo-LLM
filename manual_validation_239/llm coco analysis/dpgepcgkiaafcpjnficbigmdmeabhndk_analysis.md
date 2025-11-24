# CoCo Analysis: dpgepcgkiaafcpjnficbigmdmeabhndk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dpgepcgkiaafcpjnficbigmdmeabhndk/opgen_generated_files/bg.js
Line 965	[minified code containing chrome.runtime.onMessageExternal]
	e.token

**Analysis:**

The extension code is minified on line 965. Extracting the relevant flow from the minified code:

```javascript
// Line 965 - External message handler (minified, reformatted for clarity)
chrome.runtime.onMessageExternal.addListener((function(e,t,n){
    // e = message, t = sender, n = sendResponse

    // Handler 1: Screenshot
    "WEBVIZIO_GET_SCREENSHOT"==e.type&&setTimeout((function(){
        chrome.tabs.captureVisibleTab().then((function(e){
            n({type:"SCREENSHOT",url:e})
        }))
    }),2e3),

    // Handler 2: Data update
    "WEBVIZIO_DATA"==e.type&&(e.isProject&&e.extensionEnabled?o(!0):o(!1)),

    // Handler 3: Token storage (← Storage poisoning sink)
    "WEBVIZIO_TOKEN"==e.type&&chrome.storage.local.set({token:e.token})
    // ← Attacker-controlled e.token stored to chrome.storage.local
}))
```

The flow detected by CoCo:
1. External message received via `chrome.runtime.onMessageExternal` (line 965)
2. When `e.type == "WEBVIZIO_TOKEN"`, stores `e.token` to `chrome.storage.local.set({token:e.token})`

The manifest.json specifies `externally_connectable` restrictions (lines 54-59):
```json
"externally_connectable": {
    "matches": [
        "https://*.webvizio.com/*",
        "https://*.webvizio.my/*"
    ]
}
```

Per the methodology, we ignore these restrictions and assume any external caller can send messages.

**Code:**

```javascript
// Simplified/deobfuscated version of the flow
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    // ... other handlers ...

    if (message.type == "WEBVIZIO_TOKEN") {
        chrome.storage.local.set({token: message.token}); // ← Storage poisoning
        // ← No retrieval path back to attacker
    }
})

// The token is used internally:
chrome.storage.local.get("token", (result) => {
    if (result.token) {
        // Token used for internal logic only
        // No sendResponseExternal or other way to leak it back to attacker
    }
})
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation - storage poisoning without retrieval. While an external attacker can write arbitrary token data to chrome.storage.local via the "WEBVIZIO_TOKEN" message type, there is no path for the attacker to retrieve the poisoned value back. The methodology (lines 154, 190) explicitly states: "Storage poisoning alone (storage.set without retrieval) is NOT exploitable. The stored value MUST flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation (fetch to attacker URL, executeScript, etc.) to be TRUE POSITIVE."

The stored token is only used internally by the extension for authentication checks and does not flow back to any external caller via `sendResponseExternal`, `postMessage`, or any other attacker-accessible output.
