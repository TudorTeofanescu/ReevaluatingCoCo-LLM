# CoCo Analysis: oabiamjbccjoohfkeihoibamjfdhkhdl

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (token)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oabiamjbccjoohfkeihoibamjfdhkhdl/opgen_generated_files/bg.js
Line 1006	            br: msg.token,

**Code:**

```javascript
// Background script - lines 995-1015
chrome.runtime.onMessageExternal.addListener(function(msg, sender, sendResponse) {
      if (msg === 'check') {
        // Checking bearer token validity
        bearerOk().then((isLoggedIn) => {
            sendResponse({
                needToken: isLoggedIn === false  // Only sends boolean, not actual token
            });
            return true
        })
      }
      else if (isObj(msg) && 'token' in msg) {
        chrome.storage.local.set({  // ← Storage poisoning
            br: msg.token,  // ← attacker-controlled token
            br_exp: add_days(2),
            user: msg.login,  // ← attacker-controlled
            level: msg.level,  // ← attacker-controlled
            full: msg.full,  // ← attacker-controlled
        }).then(() => {
            return true
        });
      }
});

// bearerOk function - lines 983-990
const bearerOk = async () => {
    const s = await chrome.storage.local.get(['br', 'br_exp']);  // Gets poisoned data
    if (s.br === null || s.br_exp === null) return false;
    const now = Date.now();
    if (now > s.br_exp) return false;
    return true  // Only returns boolean, not the actual token
};

// Usage of poisoned token - lines 1136-1148
chrome.storage.local.get(['br'])
.then((s) => {
    if (s.br === null) return false;

    const options = {
        method: 'POST',
        headers: new Headers({
            'Authorization': `Bearer ${s.br}`,  // Poisoned token used
        }),
        body: new URLSearchParams(d)
    }

    fetch(url, options)  // url = `${ENDPOINT}/api/add_item` (hardcoded backend)
    .then((resp) => {
        // Response from backend, not sent to attacker
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While the attacker can poison storage (token, login, level, full) via external message, there is no retrieval path back to the attacker. The 'check' message only returns a boolean (needToken: true/false), not the actual poisoned data. The poisoned token is only used in fetch requests to the hardcoded backend URL "https://easybuy.im" (trusted infrastructure).

---

## Sink 2-4: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (login, level, full)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oabiamjbccjoohfkeihoibamjfdhkhdl/opgen_generated_files/bg.js
Line 1008	            user: msg.login,
Line 1009	            level: msg.level,
Line 1010	            full: msg.full,

**Code:**

```javascript
// Same as Sink 1 - lines 1004-1014
else if (isObj(msg) && 'token' in msg) {
    chrome.storage.local.set({
        br: msg.token,
        br_exp: add_days(2),
        user: msg.login,  // ← attacker-controlled
        level: msg.level,  // ← attacker-controlled
        full: msg.full,  // ← attacker-controlled
    }).then(() => {
        return true
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - incomplete storage exploitation. The poisoned login, level, and full values are stored but never retrieved and sent back to the attacker. No sendResponse path exists to exfiltrate these values, and they only flow to the hardcoded backend (trusted infrastructure).
