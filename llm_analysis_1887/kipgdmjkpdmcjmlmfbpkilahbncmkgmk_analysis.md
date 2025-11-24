# CoCo Analysis: kipgdmjkpdmcjmlmfbpkilahbncmkgmk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 16 (all same pattern)

---

## Sink: fetch_source → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kipgdmjkpdmcjmlmfbpkilahbncmkgmk/opgen_generated_files/bg.js
Line 265: responseText = 'data_from_fetch'
Line 987: var htmlObj = parser.parseFromString(data, 'text/html');
Line 991: callback(htmlObj.getElementsByClassName("gvClass_basic_nowrap")[1].textContent);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kipgdmjkpdmcjmlmfbpkilahbncmkgmk/opgen_generated_files/cs_0.js
Line 1437: url: "http://www.ratemyprofessors.com" + response.profLink

**Code:**

```javascript
// Content script (cs_0.js) - sends professor info to background
chrome.runtime.sendMessage({
    action: "getProfEmail",
    firstName: firstName,
    lastName: lastName
}, function (response) {
    // response.profLink comes from background script
    // which fetched it from apps.unr.edu Campus Directory
    chrome.runtime.sendMessage({
        action: "getOverallScore",
        method: "GET",
        url: "http://www.ratemyprofessors.com" + response.profLink  // ← data from fetch
    }, function (resp) {
        // Process professor rating
    });
});

// Background script (bg.js) - Line 984+
chrome.runtime.onMessage.addListener(function (request, sender, callback) {
    if (request.action == "GetProfEmail") {
        // Fetch from UNR Campus Directory (hardcoded URL)
        fetch("https://apps.unr.edu/CampusDirectory/index.aspx?AcceptsCookies=1", {...})
            .then(response => response.text())
            .then(data => {
                var parser = new DOMParser();
                var htmlObj = parser.parseFromString(data, 'text/html');
                // Extract professor link from response
                callback(htmlObj.getElementsByClassName("gvClass_basic_nowrap")[1].textContent);
            });
    }

    // Handle XMLHttpRequest for any URL in request.url
    var xhr = new XMLHttpRequest();
    var method = request.method ? request.method.toUpperCase() : 'GET';
    xhr.open(method, request.url, true);  // ← request.url from message
    // ... send request
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is trusted infrastructure communication. The extension fetches professor data FROM hardcoded backend URLs (`apps.unr.edu` and `ratemyprofessors.com`), parses the response, and then makes additional requests TO the same hardcoded backend domain (`ratemyprofessors.com`). Per the methodology, "Data TO/FROM developer's own backend servers = FALSE POSITIVE" and "Compromising developer infrastructure is separate from extension vulnerabilities." While the response.profLink is technically attacker-controlled if RateMyProfessors is compromised, the data flows entirely between the extension and its intended backend services. This is normal extension operation, not a vulnerability.

---

**Note:** All 16 detected flows follow the same pattern - data fetched from hardcoded RateMyProfessors or UNR URLs being used to construct additional requests to the same trusted backend services.
