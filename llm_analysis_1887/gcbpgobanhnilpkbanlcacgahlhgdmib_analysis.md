# CoCo Analysis: gcbpgobanhnilpkbanlcacgahlhgdmib

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_hold_draw_size_change → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gcbpgobanhnilpkbanlcacgahlhgdmib/opgen_generated_files/cs_0.js
Line 523	            press_and_draw_size: e.detail,

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 521-527)
document.addEventListener('hold_draw_size_change', debounce(function (e) {
    chrome.storage.sync.set({
        press_and_draw_size: e.detail, // ← attacker-controlled
    });
    chrome.runtime.sendMessage({ hold_draw_size_change: 2 }).catch(e => {})
}, 100));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener - webpage can dispatch custom events

**Attack:**

```javascript
// Malicious webpage dispatches custom event with attacker-controlled data
document.dispatchEvent(new CustomEvent('hold_draw_size_change', {
    detail: {
        malicious: "attacker payload",
        can: "overwrite extension storage"
    }
}));

// Storage is now poisoned with attacker-controlled values
```

**Impact:** Attacker can poison the extension's storage with arbitrary data. The content script runs on all HTTP/HTTPS pages and listens for a custom DOM event 'hold_draw_size_change'. Any webpage can dispatch this event with arbitrary data in the detail property, which gets written directly to chrome.storage.sync. While this is storage poisoning, the extension uses this stored data to control drawing features, potentially allowing an attacker to manipulate the extension's behavior when the user visits their malicious site.

