# CoCo Analysis: pfomiledcpfnldnldlffdebbpjnhkbbl

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (5+ instances of same pattern)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pfomiledcpfnldnldlffdebbpjnhkbbl/opgen_generated_files/cs_0.js
Line 467	window.addEventListener("message",(function(e){...

**Code:**

```javascript
// Content script - window.postMessage listener (content-script.js)
window.addEventListener("message",(function(e){
    // Storage write - attacker-controlled data
    if(e.data.groupsInfoTwoInject){
        let t=e.data.groupsInfoTwoInject;  // ← Attacker-controlled
        chrome.runtime.sendMessage({groupsInfoTwoInject:t}),
        chrome.storage.local.set({groupsInfoTwoInject:t,businessFlag:e.data.businessFlag})  // ← Storage sink
    }
    if(e.data.contactsInfoTwoInject){
        let t=e.data.contactsInfoTwoInject;  // ← Attacker-controlled
        chrome.runtime.sendMessage({contactsInfoTwoInject:t}),
        chrome.storage.local.set({contactsInfoTwoInject:t})  // ← Storage sink
    }
    if(e.data.chatsInfoTwoInject){
        let t=e.data.chatsInfoTwoInject;  // ← Attacker-controlled
        chrome.runtime.sendMessage({chatsInfoTwoInject:t}),
        chrome.storage.local.set({chatsInfoTwoInject:t})  // ← Storage sink
    }
    if(e.data.communityInfoTwoInject){
        let t=e.data.communityInfoTwoInject;  // ← Attacker-controlled
        chrome.runtime.sendMessage({communityInfoTwoInject:t}),
        chrome.storage.local.set({communityInfoTwoInject:t})  // ← Storage sink
    }
}),!1);

// Storage read - but different key
chrome.runtime.onMessage.addListener((async function(e,t,o){
    e.groupsInfoTwo&&chrome.storage.local.get(["userNumber"],(function(e){
        window.postMessage({groupsInfoTwo:!0,num:e.userNumber},"*")  // ← Sends back different data
    }))
}));
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning alone without retrieval path to attacker. The attacker can write to storage keys (`groupsInfoTwoInject`, `contactsInfoTwoInject`, etc.) via window.postMessage, but there is no code path that retrieves and sends these same poisoned values back to the attacker. The storage.get operation reads `userNumber`, which is a different key from what the attacker poisoned. The methodology states: "Storage poisoning alone (storage.set without retrieval) is NOT exploitable. For TRUE POSITIVE, stored data MUST flow back to attacker."
