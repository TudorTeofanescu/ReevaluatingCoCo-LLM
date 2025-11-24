# CoCo Analysis: ndjjlknbdkahjolicfjkdceldekhbbnk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ndjjlknbdkahjolicfjkdceldekhbbnk/opgen_generated_files/bg.js
Line 966 (within original extension code)

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal listener
chrome.runtime.onMessageExternal.addListener((function(t,r,e){
  var n,o,i;
  "https://hellonft.pro"===r.origin?
    chrome.storage.local.set((n={},o="STORAGE_KEY_USERINFO",i=JSON.stringify(t),o in n?Object.defineProperty(n,o,{value:i,enumerable:!0,configurable:!0,writable:!0}):n[o]=i,n),(function(){e({code:0})}))
    :e({code:1,message:"Permission denied"})
}))
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. The extension accepts external messages from https://hellonft.pro and writes the data to chrome.storage.local, but there is no corresponding storage.get operation that sends the stored data back to the attacker or uses it in any vulnerable operation. This is incomplete storage exploitation.
