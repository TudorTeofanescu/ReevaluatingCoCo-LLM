# CoCo Analysis: hdbenfgeoomkaiddadkoammkpeofpfkj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (chrome_cookies_set_sink, appearing as 4 duplicate detections)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink

**CoCo Trace:**
$FilePath$/Users/jianjia/Documents/tmp/EOPG/result_analyze/opgen_results/server/all/detected/hdbenfgeoomkaiddadkoammkpeofpfkj/opgen_generated_files/bg.js
Line 935: request.params = requestFromWeb.params;
Line 979: if (request.method == "proxyRequest" && request.params.url.match(regex)) {
- Detection shows request.params.url flowing to chrome.cookies.set

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(function (requestFromWeb, sender, sendResponse) {
    console.debug("Message from client.js", requestFromWeb, sender);
    var request = {};
    request.method = requestFromWeb.method;
    request.params = requestFromWeb.params; // ← attacker-controlled params
    request.sender = {};
    request.sender.url = sender.url;
    request.sender.title = sender.title;
    request.sender.browser = "Chrome";
    request.sender.userAgent = navigator.userAgent;
    request.data = requestFromWeb.data;

    console.debug("Sending to host", request);

    // Send to native messaging host
    chrome.runtime.sendNativeMessage(hostName, request, function (respFromNative) {
        console.debug("Message from host", respFromNative);
        var resp = {};
        resp.type = null;
        resp.error = null;
        resp.data = null;

        if (respFromNative == null || respFromNative.type === "error") {
            // Error handling
            resp.type = "error";
            // ... error handling code ...
        } else {
            resp.data = respFromNative.data;
            resp.type = respFromNative.type;

            /*
             * XXX: hack in order to handler set-cookie header.
             * *.set.rn.gov.br has a requisite to set cookie on browser
             */

            /* RegEx: https://regex101.com/r/uI7vbl/2 --> match sites like *.set.rn.gov.br and localhost */
            var regex = /^https?:\/\/[^\/]*?\.?(?:set.rn.gov.br|localhost)(?::\d+)?(?:\/|$)/gm;
            try {
                // Validate URL matches trusted domain regex
                if (request.method == "proxyRequest" && request.params.url.match(regex)) {
                    // Parse response from native host
                    var cookies = parseSetCookie(JSON.parse(resp.data));
                    if (cookies) {
                        cookies.forEach(function(cookie) {
                            cookie.url = request.params.url; // ← URL validated by regex
                            chrome.cookies.set(cookie, function (setCookie) { // ← Cookie sink
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
            } catch (e) {
                console.error("Exception while trying to set a cookie:", e);
            }
        }

        sendResponse(resp);
    });

    return true;
});
```

**Classification:** FALSE POSITIVE

**Exploitable by:** `*://*.set.rn.gov.br/*` and `*://localhost/*` (per manifest's externally_connectable)

**Reason:** This extension is designed to interact with the government website *.set.rn.gov.br (Rio Grande do Norte state government in Brazil) and localhost for testing. The cookies are only set for URLs that match the strict regex validation: `/^https?:\/\/[^\/]*?\.?(?:set.rn.gov.br|localhost)(?::\d+)?(?:\/|$)/gm`

Key security controls:
1. **externally_connectable restriction**: Only `*://*.set.rn.gov.br/*` and `*://localhost/*` can send external messages
2. **URL validation**: The request.params.url must match the regex that only allows set.rn.gov.br or localhost domains
3. **Trusted infrastructure**: The set.rn.gov.br domain is the government website this extension is designed to serve
4. **Cookie data source**: Cookie values come from native messaging host response (respFromNative.data), not directly from external message
5. **Purpose**: The extension is a security module for government website authentication/tokens

The attacker-controlled data (request.params.url) is only used to validate against the whitelist regex and set the cookie.url property. The actual cookie values come from the native messaging host response, which processes requests through the local security module. This is trusted infrastructure interaction, not an exploitable vulnerability.

While technically an external website (set.rn.gov.br) could send messages, this is the intended and trusted use case - the extension exists specifically to serve this government website's security needs.
