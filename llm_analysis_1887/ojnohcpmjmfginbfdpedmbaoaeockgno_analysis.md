# CoCo Analysis: ojnohcpmjmfginbfdpedmbaoaeockgno

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ojnohcpmjmfginbfdpedmbaoaeockgno/opgen_generated_files/cs_0.js
Line 503: window.addEventListener("message", (event) => {
Line 505: if (event.source !== window || !event.data.type || event.data.type !== "ext" || !event.data.key) return;
Line 508: chrome.runtime.sendMessage({ type: "ext", key: event.data.key , value: event.data.value , call: event.data.call });

**Code:**

```javascript
// Content script (c.js) - Lines 503-510
window.addEventListener("message", (event) => {
    if (event.source !== window || !event.data.type || event.data.type !== "ext" || !event.data.key) return;

    // Forward the message to the service worker
    chrome.runtime.sendMessage({
        type: "ext",
        key: event.data.key,    // ← attacker-controlled
        value: event.data.value, // ← attacker-controlled
        call: event.data.call    // ← attacker-controlled
    });
});

// Background script (s.js) - Lines 1011-1012
chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.type === 'ext' && message.key && message.value && message.command) {
        chrome.storage.sync.set({ [message.key]: message.value }); // ← storage poisoning
        setTimeout(() => {
            updateBlockingList(message.command, true);
        }, 500);
    }
    // ... other handlers
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from any webpage

**Attack:**

```javascript
// On any webpage (content script runs on *:///*/*)
window.postMessage({
    type: "ext",
    key: "maliciousKey",
    value: "maliciousValue",
    command: "someCommand"
}, "*");

// This poisons chrome.storage.sync with arbitrary key-value pairs
// The extension uses storage for blocking lists and configuration
```

**Impact:** Malicious webpages can poison extension storage with arbitrary data. Although the code checks for a "command" field (Line 1011), an attacker can supply any value. This allows storage manipulation that affects extension behavior including blocking list updates via updateBlockingList().
