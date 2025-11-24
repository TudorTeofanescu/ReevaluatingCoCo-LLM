# CoCo Analysis: pgdinhgkmmblmegnadklbleainlaelhj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (same pattern)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgdinhgkmmblmegnadklbleainlaelhj/opgen_generated_files/bg.js
Line 979	chrome.runtime.onMessageExternal.addListener(o=>{...chrome.storage.local.set({token:o.token})...})

**Code:**

```javascript
// Background script - External message handlers (bg.js, line 979)
chrome.runtime.onMessageExternal.addListener(o=>{
    console.log("woah!"),
    o.type==="AUTH_TOKEN"&&o.token&&o.user&&(
        chrome.storage.local.set({token:o.token}),  // ← Attacker-controlled token stored
        chrome.storage.local.set({user:o.user})     // ← Attacker-controlled user stored
    )
});

chrome.runtime.onMessageExternal.addListener(o=>{
    o.type==="REFRESH_MODEL"&&o.user&&chrome.storage.local.set({user:o.user})  // ← Attacker-controlled user stored
});

// Storage retrieval
$=async()=>{
    const o=await chrome.storage.local.get(["token"]);  // ← Reads poisoned token
    return console.log(o),o.token
}

// Token usage - sent to hardcoded backend
ue=async o=>{
    const g=await $();  // ← Gets poisoned token
    return await fetch(B.BackendUrl+"/Vehicle",{  // ← Sent to hardcoded backend
        method:"POST",
        headers:{"Content-Type":"application/json",Authorization:`Bearer ${g.token}`},
        body:JSON.stringify(r)
    })
}
```

**Classification:** FALSE POSITIVE

**Reason:** Although attacker can poison storage via onMessageExternal and the token is retrieved and used, it flows TO the developer's hardcoded backend URL (B.BackendUrl), not back to the attacker. The methodology states: "Data TO hardcoded backend: `attacker-data → fetch("https://api.myextension.com")` = FALSE POSITIVE. Compromising developer infrastructure is separate from extension vulnerabilities." The poisoned token is used in Authorization headers for requests to the trusted backend, which is infrastructure-level trust, not an extension vulnerability.
