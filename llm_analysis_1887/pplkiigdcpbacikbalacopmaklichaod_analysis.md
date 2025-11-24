# CoCo Analysis: pplkiigdcpbacikbalacopmaklichaod

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pplkiigdcpbacikbalacopmaklichaod/opgen_generated_files/bg.js
Line 965  chrome.runtime.onMessageExternal.addListener(((e,o,t)=>{o&&o.url&&o.url.startsWith("https://app.getprog.ai")?e.authTokens&&(chrome.tabs.query({currentWindow:!0},(o=>{o.forEach((o=>{chrome.tabs.sendMessage(o.id,{type:"AUTH_TOKENS",authTokens:e.authTokens})}))})),chrome.storage.local.set({authTokens:e.authTokens},(()=>{console.log("Data saved to local storage"),t({status:"tokens sent to content script"})}))):console.log("Unauthorized sender:",o)}))
         e.authTokens
```

**Code:**

```javascript
// Background script bg.js (Line 965)
chrome.runtime.onMessageExternal.addListener(((e,o,t)=>{
  o&&o.url&&o.url.startsWith("https://app.getprog.ai") ?
    e.authTokens && (
      chrome.tabs.query({currentWindow:!0},(o=>{
        o.forEach((o=>{
          chrome.tabs.sendMessage(o.id,{type:"AUTH_TOKENS",authTokens:e.authTokens}) // ← Sent to tabs
        }))
      })),
      chrome.storage.local.set({authTokens:e.authTokens},(()=>{ // ← Storage poisoning
        console.log("Data saved to local storage"),
        t({status:"tokens sent to content script"}) // ← Only status sent back, not the tokens
      }))
    )
  : console.log("Unauthorized sender:",o)
}))
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. The external sender can store authTokens via chrome.runtime.onMessageExternal, but the stored tokens are not sent back to the attacker. The sendResponse (t) only returns a status message, while the actual authTokens are forwarded to content scripts via chrome.tabs.sendMessage. There is no retrieval path where the attacker can obtain the stored data back through sendResponse, postMessage, or any attacker-accessible output.
