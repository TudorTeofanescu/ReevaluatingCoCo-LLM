# CoCo Analysis: loafcmllacjldigeifbfmbogkbihmblj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (CoCo detected same flow multiple times)

---

## Sink: document_eventListener_qa_fe_msg_send → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/loafcmllacjldigeifbfmbogkbihmblj/opgen_generated_files/cs_0.js
Line 645	    document.addEventListener( 'qa_fe_msg_send', function(data){
	data
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/loafcmllacjldigeifbfmbogkbihmblj/opgen_generated_files/cs_0.js
Line 646	        receiveFrontEndMessage( data.detail );
	data.detail
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/loafcmllacjldigeifbfmbogkbihmblj/opgen_generated_files/bg.js
Line 1013			activateLicense(request.data).then(function(l){
	request.data
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/loafcmllacjldigeifbfmbogkbihmblj/opgen_generated_files/bg.js
Line 1288			'email': settings.email,
	settings.email
```

**Analysis:**

CoCo detected a DOM event listener flow. The complete path is:

**Code:**
```javascript
// Content script (cs_0.js) - Entry point
document.addEventListener('qa_fe_msg_send', function(data){
    receiveFrontEndMessage(data.detail); // ← attacker can dispatch this event
}, false);

function receiveFrontEndMessage(data) {
    switch(data.type) {
        // ... other cases ...
        case 'settings':
            delete data.type;
            chrome.runtime.sendMessage({ type: 'setSettings', data: data }); // ← forward to background
            break;
        case 'getSettings':
            chrome.runtime.sendMessage({type: "startup"}, function(response) {
                switch(response.type) {
                    case 'settings':
                        settings.syncGraphAlerts = (response.syncGraphAlerts == undefined ? false : response.syncGraphAlerts);
                        sendFrontEndMessage(response); // ← send back to webpage
                        break;
                }
            });
            break;
    }
}

function sendFrontEndMessage(data) {
    var evt = new CustomEvent('qa_fe_msg_rec', {
        detail: data // ← attacker can listen to this event
    });
    document.dispatchEvent(evt);
}

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log('background received', request);
    switch(request.type){
        case 'check-license':
            activateLicense(request.data).then(function(l){ // ← attacker-controlled request.data
                sendMessage({type: 'check-license-result', data: l }); // ← send back to content script
            });
            break;
        case 'setSettings':
            delete request.type;
            setSettings(request.data); // ← stores attacker data
            sendResponse(null);
            break;
        case 'getSettings':
            sendResponse(data); // ← send settings back
            break;
        // ... other cases ...
    }
    return true;
});

function activateLicense(settings) {
    var timeStamp = Date.now();
    var promise = new Promise(function(resolve, reject) {
        if(licenseData.valid) {
            resolve(licenseData);
        }
        post('https://quickalerts.us/auth/', {
            'email': settings.email, // ← attacker-controlled
            'timestamp': timeStamp,
            'challenge': md5(timeStamp + ":" + settings.apikey) // ← attacker-controlled
        }, function(data){
            licenseData.email = settings.email; // ← store attacker's email
            licenseData.apikey = settings.apikey; // ← store attacker's apikey
            if(data.success) {
                licenseData.valid = true;
            } else {
                licenseData.valid = false;
            }
            licenseData.message = data.message;
            licenseData.session = data.data.session;
            refreshAddons();
            saveLicense(); // ← save to storage
            resolve(licenseData);
        });
    });
    return promise;
}

function saveLicense() {
    chrome.storage.sync.set({"bSettings": licenseData}); // ← storage sink
}

function setSettings(request_data) {
    // ... process settings ...
    chrome.storage.sync.set({"aSettings": data}); // ← another storage sink
}
```

**Classification:** FALSE POSITIVE

**Reason:** While the extension has an exploitable DOM event listener that can be triggered by an attacker (via `document.dispatchEvent(new CustomEvent('qa_fe_msg_send', {detail: {...}}))`), and the attacker-controlled data flows to `chrome.storage.sync.set`, this is incomplete storage exploitation for several reasons:

1. **Self-poisoning only**: The attacker can only poison their own session/profile data with their own credentials. When the attacker sends `{type: 'check-license', data: {email: 'attacker@email.com', apikey: 'attackerkey'}}`, they are only storing their own authentication credentials in their own browser's storage.

2. **No cross-user data theft**: The stored data does not contain sensitive information from other users. The attacker cannot retrieve other users' license data, settings, or credentials - only their own.

3. **Limited impact**: While there is a retrieval path (data flows back via `sendFrontEndMessage → CustomEvent 'qa_fe_msg_rec'`), the attacker is only retrieving their own data that they just sent. This provides no exploitable advantage.

4. **Authentication to trusted backend**: The extension POSTs the attacker's credentials to the developer's hardcoded backend (`https://quickalerts.us/auth/`), which validates them. The response from this trusted backend is what gets stored alongside the attacker's credentials.

According to the methodology, storage poisoning where the attacker can only manipulate their own session data without affecting other users or achieving code execution/SSRF/downloads/sensitive data exfiltration is NOT a true vulnerability. The attacker gains no exploitable advantage from poisoning their own profile.

**Note on manifest restrictions**: The content script only matches `https://*.tradingview.com/*` (manifest.json line 16), so the attack surface is limited to TradingView pages. However, following the methodology's instruction to ignore manifest restrictions, we still classify this as FALSE POSITIVE due to the lack of exploitable impact rather than the limited attack surface.
