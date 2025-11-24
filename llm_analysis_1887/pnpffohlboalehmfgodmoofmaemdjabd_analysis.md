# CoCo Analysis: pnpffohlboalehmfgodmoofmaemdjabd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pnpffohlboalehmfgodmoofmaemdjabd/opgen_generated_files/bg.js
Line 965 chrome.runtime.onMessageExternal.addListener handling "saveWiseSessionToken" action

**Code:**

```javascript
// Background script (bg.js line 965)
chrome.runtime.onMessageExternal.addListener((e,o,s)=>{
  switch(console.log("request",e),e.action){
    case"saveWiseSessionToken":
      n(e.token),  // ← attacker-controlled token
      e.token?s({success:!0,message:"Token has been received"}):
              s({success:!1,message:"Token is empty"});
      break
  }
  return!0
});

function n(e){
  console.log("saveWiseSessionToken",e),
  chrome.storage.local.set({wiseSessionToken:e},function(){  // ← stores attacker data
    console.log("Wise session token saved")
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only without retrieval path. While external websites whitelisted in externally_connectable can send messages to store arbitrary data in wiseSessionToken, there is no code path that retrieves this stored value or uses it in any subsequent operation. The token is written to storage but never read back, making it impossible for an attacker to observe or exploit the stored data. Per the CoCo methodology, storage.set without retrieval is not a vulnerability.
