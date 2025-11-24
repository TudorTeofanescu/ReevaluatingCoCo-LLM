# CoCo Analysis: eafifknfjiicecckgdkcpklnppidfhen

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eafifknfjiicecckgdkcpklnppidfhen/opgen_generated_files/bg.js
Line 727	    var storage_sync_get_source = {
        'key': 'value'
    };

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eafifknfjiicecckgdkcpklnppidfhen/opgen_generated_files/bg.js
Line 1024	            sendResponse(data.targetLang);
	data.targetLang
```

**Code:**

```javascript
// Background script - Lines 970-1031
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    // ... other handlers ...

    if (request.action == "getTargetLang") {
        chrome.storage.sync.get("targetLang", (data) => {
            sendResponse(data.targetLang); // ← Storage data sent to external caller
        });
    }

    if (request.action == "saveTargetLang") {
        chrome.storage.sync.set({ targetLang: request.lang }); // ← External input written to storage
    }

    return true;
});
```

**Manifest externally_connectable:**
```json
"externally_connectable": {
    "matches": ["https://mail.google.com/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://mail.google.com/*)
// Step 1: Write arbitrary data to storage
chrome.runtime.sendMessage(
    'eafifknfjiicecckgdkcpklnppidfhen',
    { action: 'saveTargetLang', lang: 'attacker-controlled-value' }
);

// Step 2: Read the stored data back
chrome.runtime.sendMessage(
    'eafifknfjiicecckgdkcpklnppidfhen',
    { action: 'getTargetLang' },
    (response) => {
        console.log('Retrieved from storage:', response); // 'attacker-controlled-value'
    }
);
```

**Impact:** Complete storage exploitation chain. An external attacker (from mail.google.com or any compromised whitelisted domain) can both poison the extension's storage with arbitrary data and retrieve that data back. While the extension restricts external messages to mail.google.com, per the methodology, we ignore manifest.json restrictions - if even ONE domain can exploit it, it's a TRUE POSITIVE. This enables persistent data storage and retrieval under attacker control.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eafifknfjiicecckgdkcpklnppidfhen/opgen_generated_files/bg.js
Line 1028	        chrome.storage.sync.set({ targetLang: request.lang });
	request.lang
```

**Classification:** TRUE POSITIVE (covered in Sink 1 analysis)

**Reason:** This is the write portion of the complete storage exploitation chain analyzed in Sink 1. The attacker can write arbitrary data via `saveTargetLang` action and retrieve it via `getTargetLang` action, forming a complete bidirectional storage manipulation vulnerability.

---
