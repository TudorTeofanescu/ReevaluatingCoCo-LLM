# CoCo Analysis: egljcmflffpafhbakdpfdebafmlifehj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (urlToEdited, groupId, expCode, token to storage)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/egljcmflffpafhbakdpfdebafmlifehj/opgen_generated_files/bg.js
Line 965:
```javascript
chrome.runtime.onMessageExternal.addListener((e,t,o)=>{
    const r=e.command;
    if("getVersion"===r){
        const e=chrome.runtime.getManifest();
        o({type:"success",version:e.version})
    }
    return"set"===r&&chrome.storage.local.set({
        urlToEdited:e.urlToEdited,  // ← attacker-controlled
        groupId:e.groupId,          // ← attacker-controlled
        expCode:e.expCode,          // ← attacker-controlled
        token:e.token               // ← attacker-controlled
    },function(e){o({type:"success"})}),!0
})
```

**Code:**

```javascript
// Background script (bg.js) - Line 965
// External message handler (allows messages from externally_connectable domains)
chrome.runtime.onMessageExternal.addListener((e,t,o)=>{
    const r=e.command;

    if("getVersion"===r){
        const e=chrome.runtime.getManifest();
        o({type:"success",version:e.version})
    }

    // Storage poisoning: external attacker can write to storage
    return"set"===r&&chrome.storage.local.set({
        urlToEdited:e.urlToEdited,  // ← attacker-controlled
        groupId:e.groupId,          // ← attacker-controlled
        expCode:e.expCode,          // ← attacker-controlled
        token:e.token               // ← attacker-controlled
    },function(e){o({type:"success"})}),!0
})

// Internal message handler (only accessible from extension's own pages/content scripts)
chrome.runtime.onMessage.addListener((e,t,o)=>{
    const r=e.command;

    // Storage retrieval - but only via INTERNAL messages
    return"get"===r?(chrome.storage.local.get(function(e){
        o({type:"success",urlToEdited:e.urlToEdited,expCode:e.expCode,groupId:e.groupId,token:e.token})
    }),!0):"clear"===r?(chrome.storage.local.remove(["urlToEdited","groupId","expCode","token"],function(e){
        o({type:"success"})
    }),!0):void 0
})
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. External attacker can poison storage via "set" command through `chrome.runtime.onMessageExternal`, but cannot retrieve the poisoned data back. The "get" command that retrieves storage data is only accessible via `chrome.runtime.onMessage` (internal messages), not `onMessageExternal`. The attacker can write values to storage but has no path to read them back or observe their effect. According to the methodology, storage poisoning alone without retrieval path to attacker is FALSE POSITIVE (Pattern Y: Incomplete Storage Exploitation).

Note: The manifest has `externally_connectable` restricted to `*://*.wsd.com/*`, but per methodology Rule 1, we ignore manifest restrictions and assume ANY attacker can trigger `onMessageExternal`. However, this still remains FALSE POSITIVE due to lack of retrieval path.
