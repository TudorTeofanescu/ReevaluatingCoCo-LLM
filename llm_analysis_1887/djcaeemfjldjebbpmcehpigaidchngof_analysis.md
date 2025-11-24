# CoCo Analysis: djcaeemfjldjebbpmcehpigaidchngof

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/djcaeemfjldjebbpmcehpigaidchngof/opgen_generated_files/cs_1.js
Line 480	  window.addEventListener("message", function(e) {
Line 485	    var data = e.data;
Line 487	        if(data.method=="PipiAuthTokenLogin" && data.token){

**Code:**

```javascript
// Content script on pipileads.com (cs_1.js / pipiScript.js):
function PipiAuthTokenLogin(token){
    chrome.runtime.sendMessage({
        data: token, method: 'PipiAuthTokenLogin'  // ← Attacker-controlled token
    });
}

window.addEventListener("message", function(e) {  // ← Entry point
    if (e.source != window) {
        return;
    }

    var data = e.data;  // ← Attacker-controlled data
    if (data.type && (data.type == "PipiAuthTokenOperation")) {
        if(data.method=="PipiAuthTokenLogin" && data.token){
            PipiAuthTokenLogin(data.token);  // ← Token sent to background
        }else if(data.method=="PipiAuthTokenLogout"){
            PipiAuthTokenLogout();
        }
    }
});

// Background script (bg.js / sw.js):
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.method == "PipiAuthTokenLogin"){
        if(request.data){
            chrome.storage.local.set({auth_token:request.data,});  // ← Storage write
        }
    }
});

// Token is later retrieved and used:
chrome.storage.local.get(['auth_token'],function(request){
    var headers={
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-fetch-mode": "cors",
    }
    if(request.auth_token!=undefined){
        headers["authorization"]='Token '+request.auth_token;  // ← Token used
    }
    fetch(MainHost()+'/check-data/', {  // ← Sent to hardcoded backend
        "headers": headers,
        "referrerPolicy": "strict-origin-when-cross-origin",
        // ...
    });
});

// From commonusecase.js:
function MainHost() {
    return('https://pipileads.com');  // ← Hardcoded backend URL
}
```

**Classification:** FALSE POSITIVE

**Reason:** While there is a complete attack path where an attacker can send a postMessage with a malicious token to the pipileads.com webpage, which gets stored in chrome.storage.local, this constitutes an incomplete storage exploitation chain. The stored auth_token is later retrieved from storage and used in Authorization headers for fetch requests, but these requests are sent exclusively to the hardcoded backend URL `https://pipileads.com` (via MainHost() function). According to the threat model, hardcoded backend URLs are trusted infrastructure. The pattern `storage.get → fetch(hardcodedBackendURL)` is explicitly classified as FALSE POSITIVE (Pattern Y) because the developer trusts their own infrastructure. The attacker can poison the storage but cannot retrieve the data back or redirect it to an attacker-controlled destination - it only goes to the trusted backend.
