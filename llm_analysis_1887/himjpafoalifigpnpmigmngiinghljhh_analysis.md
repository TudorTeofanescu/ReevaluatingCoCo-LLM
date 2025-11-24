# CoCo Analysis: himjpafoalifigpnpmigmngiinghljhh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/himjpafoalifigpnpmigmngiinghljhh/opgen_generated_files/bg.js
Line 996: window.localStorage.setItem('k', request.k);

**Code:**

```javascript
// background.js - External message handler (lines 995-997)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    window.localStorage.setItem('k', request.k);  // <- attacker-controlled storage write
});

// background.js - Storage read and usage (lines 998-1010)
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        var redirecting_domains = [
            'freehdtabs.com'
        ];
        var req = new URL(details.url);
        var k = window.localStorage.getItem("k");  // Storage read
        if (redirecting_domains.indexOf(req.hostname) != -1 && req.pathname.includes('search') && k != null && details.url.indexOf("k=") == -1) {
            return {
                redirectUrl: details.url + '&k=' + k,  // Attacker-controlled data appended to URL
            };
        }
    }, { urls: ["<all_urls>"] }, ["blocking"]);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (freehdtabs.com)

**Attack:**

```javascript
// From freehdtabs.com webpage, attacker sends message to extension
chrome.runtime.sendMessage('himjpafoalifigpnpmigmngiinghljhh', {
    k: 'malicious_tracking_id_or_xss_payload'
});

// When user navigates to freehdtabs.com/search, the extension appends the malicious k parameter:
// https://freehdtabs.com/search?q=cats&k=malicious_tracking_id_or_xss_payload
```

**Impact:** Complete storage exploitation chain - the attacker (freehdtabs.com) can poison localStorage with arbitrary values via external messaging, and then retrieve those values back when the user navigates to their domain, as the extension automatically appends the stored 'k' parameter to URLs. This allows persistent tracking, session hijacking, or potentially XSS if the backend doesn't properly sanitize the k parameter. The manifest.json restricts externally_connectable to freehdtabs.com only, but per the methodology, even if only ONE domain can exploit it, this is classified as TRUE POSITIVE.
