# CoCo Analysis: bphkomkkkmllmoofmdaiknnjiinmmbie

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bphkomkkkmllmoofmdaiknnjiinmmbie/opgen_generated_files/bg.js
Line 965	chrome.runtime.onMessageExternal.addListener((e,t,r)=>(chrome.storage.local.get("isLogin",o=>{o.isLogin==="true"?e.token?e.token==="logout"?chrome.storage.local.remove(["token","isLogin"],()=>{chrome.runtime.lastError?r({status:"Error",error:chrome.runtime.lastError.message}):r({status:"Success",message:"Token and login status removed"})}):chrome.storage.local.set({token:e.token},()=>{chrome.runtime.lastError?r({status:"Error",error:chrome.runtime.lastError.message}):r({status:"Success"})}):e.action==="open_extension"||r({status:"Error",error:"No token provided"}):r({status:"Error",error:"User not logged in"})}),!0));

**Code:**

```javascript
// Background script - bg.js Line 965
chrome.runtime.onMessageExternal.addListener((e,t,r)=>(
  chrome.storage.local.get("isLogin",o=>{
    o.isLogin==="true"?
      e.token?  // ← attacker-controlled from external message
        e.token==="logout"?
          chrome.storage.local.remove(["token","isLogin"],()=>{
            chrome.runtime.lastError?
              r({status:"Error",error:chrome.runtime.lastError.message}):
              r({status:"Success",message:"Token and login status removed"})
          }):
          chrome.storage.local.set({token:e.token},()=>{  // ← sink: attacker-controlled token written to storage
            chrome.runtime.lastError?
              r({status:"Error",error:chrome.runtime.lastError.message}):
              r({status:"Success"})
          }):
        e.action==="open_extension"||r({status:"Error",error:"No token provided"}):
      r({status:"Error",error:"User not logged in"})
  }),
  !0
));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted domain (localhost, mcro.ai, or tikko.io):
// Send malicious token to the extension
chrome.runtime.sendMessage(
  "bphkomkkkmllmoofmdaiknnjiinmmbie",  // Extension ID
  {token: "malicious_token_value"},
  function(response) {
    console.log("Storage poisoned:", response);
  }
);
```

**Impact:** Storage poisoning vulnerability. Although the manifest.json restricts externally_connectable to localhost, mcro.ai, and tikko.io domains, any of these domains (or an attacker controlling them) can send arbitrary external messages to poison the extension's local storage with a malicious token. The extension trusts the isLogin flag already in storage and will write any token value provided by the external message. This could lead to authentication bypass or session hijacking if the extension uses this stored token for privileged operations. While the initial check requires isLogin==="true", an attacker could potentially set that first, then poison the token value.
