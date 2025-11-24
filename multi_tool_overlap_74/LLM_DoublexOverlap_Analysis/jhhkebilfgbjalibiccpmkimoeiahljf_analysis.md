# CoCo Analysis: jhhkebilfgbjalibiccpmkimoeiahljf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (all XMLHttpRequest_url_sink - duplicates of same flow)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jhhkebilfgbjalibiccpmkimoeiahljf/opgen_generated_files/cs_0.js
Line 469: window.addEventListener("message", function(evt)
Line 470: evt.data.enq === 20
Line 470: evt.data

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jhhkebilfgbjalibiccpmkimoeiahljf/opgen_generated_files/bg.js
Line 3256: showQueryResult(aRequest.urlq, aRequest.outp);
Line 3208: aQueryUrl.trim()

**Code:**

```javascript
// Content script - Entry point (cs_0.js Lines 469-477)
window.addEventListener("message", function(evt) {
  if (evt.data.enq === 20) { // ← requires specific enq value
    chrome.runtime.sendMessage(evt.data, function(aResponse) {
      if (!chrome.runtime.lastError && aResponse) {
        window.postMessage({ enq: 21, srcv: evt.data.srcv }, "*");
      }
    });
  }
}, false);

// Background script - Message handler (bg.js Line 3255-3256)
case EnqType.ShowQueryResult:
  showQueryResult(aRequest.urlq, aRequest.outp); // ← urlq is attacker-controlled
  break;

// Show query result function (bg.js Lines 3326-3354)
async function showQueryResult(aQueryUrl, outputType) {
  // Checks if URL matches specific API patterns
  if (isWikiApiUrl(aQueryUrl)) {
    queryApi(aQueryUrl, extractApiDataWiki, async function(resultTitle, resultHtml, resultUrl) {
      await showResultInTab(outputType, aQueryUrl, resultUrl, resultTitle, resultHtml);
    });
  } else if (isGoogleApisUrl(aQueryUrl)) {
    // ... similar pattern
  } else if (isYandexApisUrl(aQueryUrl)) {
    // ... similar pattern
  } else {
    await showResultInTab(outputType, aQueryUrl, undefined, undefined, undefined);
  }
}

async function showResultInTab(outputType, aQueryUrl, resultUrl, resultTitle, resultHtml) {
  var urlToOpen = resultUrl || aQueryUrl;
  // Opens URL in new tab
  chrome.tabs.create({ url: urlToOpen }); // ← Opens attacker-controlled URL
}
```

**Classification:** FALSE POSITIVE

**Reason:** The content script only runs on pages matching "*://*.querybench.com/*/mod/*" (as specified in manifest.json). This means the postMessage listener is only active on the extension developer's own website. An attacker cannot trigger this flow from an arbitrary malicious website because the content script is not injected there. This is internal extension functionality accessible only from the developer's trusted domain, not an external attacker-triggerable vulnerability.
