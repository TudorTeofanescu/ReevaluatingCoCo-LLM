# CoCo Analysis: aibadchapcfhkkaofakhbdpemlnkckge

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aibadchapcfhkkaofakhbdpemlnkckge/opgen_generated_files/cs_0.js
Line 467: Minified code containing `window.addEventListener("message",...)`
The flow shows: `t.data.token` → `chrome.storage.local.set({teraToken:t.data.token})`

**Code:**

```javascript
// Content script - Minified (from original js/content_script.js)
window.addEventListener("message",(function(t){
  return e(this,void 0,void 0,(function*(){
    switch(t.data.type){
      // ... other cases
      case"teraTokenUpdate":
        chrome.storage.local.set({teraToken:t.data.token}); // ← attacker can write token
        break;
      // ... other cases
    }
  }))
}));

// Token retrieval and usage (same file)
const a=(a,t,o,r)=>e(void 0,void 0,void 0,(function*(){
  try{
    const e=r||(yield chrome.storage.local.get("teraToken")).teraToken, // ← token retrieved
    n=yield fetch("https://api.tera.chat/v1/crm/"+a,{ // ← sent to hardcoded backend
      method:t,
      headers:{authorization:`Bearer ${e}`,"Content-Type":"application/x-www-form-urlencoded"},
      body:o
    });
    return yield n.json()
  }catch(e){return{error:!0,msg:e.message}}
}))
```

**Classification:** FALSE POSITIVE

**Reason:** While an attacker can poison the storage via `window.postMessage`, the stored token is only sent to a hardcoded backend URL (`https://api.tera.chat`). According to the methodology, data flowing to hardcoded developer backend URLs is considered trusted infrastructure, not an extension vulnerability. Compromising the developer's infrastructure is a separate security concern.
