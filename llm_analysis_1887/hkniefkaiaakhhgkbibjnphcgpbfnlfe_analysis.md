# CoCo Analysis: hkniefkaiaakhhgkbibjnphcgpbfnlfe

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkniefkaiaakhhgkbibjnphcgpbfnlfe/opgen_generated_files/cs_0.js
Line 467: window.addEventListener("message",function(a){a.source==window&&a.data.type&&"FROM_PAGE"==a.data.type&&chrome.runtime.sendMessage({type:"auth-token",value:a.data.token,firstName:a.data.firstName})});
- a.data.token

**Code:**

```javascript
// Content script - cs_0.js Line 467
window.addEventListener("message",function(a){
  a.source==window&&a.data.type&&"FROM_PAGE"==a.data.type&&
  chrome.runtime.sendMessage({
    type:"auth-token",
    value:a.data.token,           // ← attacker-controlled
    firstName:a.data.firstName    // ← attacker-controlled
  })
});

// Background script - bg.js Line 969
chrome.runtime.onMessage.addListener(function(a,e,d){
  if("auth-token"===a.type&&null!=a.value){
    console.log("auth-token recieved");
    chrome.storage.local.set({
      authToken:a.value,           // ← attacker data stored
      firstName:a.firstName        // ← attacker data stored
    });
    chrome.action.setBadgeText({text:"ON"});
    chrome.runtime.sendMessage({type:"login_successful"});
    chrome.action.setPopup({popup:"pages/polish.html"});
  }
  // ... other handlers
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// On https://google.emailpolisher.com/auth/google/success
// (where content script is injected per manifest)
window.postMessage({
  type: "FROM_PAGE",
  token: "attacker_malicious_token",
  firstName: "AttackerName"
}, "*");
```

**Impact:** Storage poisoning vulnerability. An attacker on the specific domain where the content script runs (https://google.emailpolisher.com/auth/google/success) can inject malicious data into chrome.storage.local, poisoning the authToken and firstName values. While this is storage.set without immediate retrieval, the poisoned authToken is later used in Line 969 to authenticate API requests to the backend ("Authorization: Bearer " + b.authToken). This could allow an attacker to hijack the user's session or inject malicious credentials.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkniefkaiaakhhgkbibjnphcgpbfnlfe/opgen_generated_files/cs_0.js
Line 467: a.data.firstName

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, different field (firstName instead of token). Both flow through the same attack path.
