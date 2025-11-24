# CoCo Analysis: gmhnihjeppeoenbgcpckjkmjjggleiam

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 7

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gmhnihjeppeoenbgcpckjkmjjggleiam/opgen_generated_files/bg.js
Line 1375: `let url=request.url;`
Line 1388: `let decrypted = CryptoJSAesJson.decrypt(request.token, password);`
Line 1390: `request.usuario=decrypted[0];`
Line 1391: `request.senha=decrypted[1];`
Line 1392: `request.escritorio=decrypted[2];`
Line 1312: `if (request.fc=="goprocesso" || request.fc=="extracao" || request.fc=="goprocessoandgetlastdespacho")`

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal listener (bg.js:1309-1325)
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        let r;
        if (request.fc=="goprocesso" || request.fc=="extracao" || request.fc=="goprocessoandgetlastdespacho") {
            r=extracao(request); // Calls extracao() which stores request properties
        }
        // ...
        sendResponse({situacao: "Chegou ", request: request, resultado: r});
});

// extracao function (bg.js:1370-1434)
function extracao(request){
    // ... validation ...
    let url=request.url; // ← CoCo flagged: attacker-controlled

    let password = 'arriStg818'
    let decrypted = CryptoJSAesJson.decrypt(request.token, password); // ← CoCo flagged
    request.usuario=decrypted[0]; // ← CoCo flagged
    request.senha=decrypted[1]; // ← CoCo flagged
    request.escritorio=decrypted[2]; // ← CoCo flagged

    if (request.escritorio) {
        chrome.storage.local.set({escritorio: request.escritorio}); // Storage write
    }

    saveRequest(request); // Calls saveRequest which writes to storage
    // ...
}

// saveRequest function (bg.js:1530-1532)
function saveRequest(request){
    chrome.storage.local.set({ "lastRequest": request }, function(){}); // Storage write
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While external websites from the `externally_connectable` whitelist (e.g., https://*.sijur.com.br/*, various court websites) can send messages via chrome.runtime.onMessageExternal to poison storage with attacker-controlled data (request.url, request.token, request.fc, etc.), there is no retrieval path that sends the poisoned data back to the attacker. The stored data in chrome.storage.local.set() is not read and sent back via sendResponse, postMessage, or used in any attacker-accessible operation. Storage poisoning alone without a retrieval mechanism is not exploitable under the methodology.

---
