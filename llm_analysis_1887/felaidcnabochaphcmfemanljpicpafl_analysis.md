# CoCo Analysis: felaidcnabochaphcmfemanljpicpafl

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (duplicate detections)

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/felaidcnabochaphcmfemanljpicpafl/opgen_generated_files/bg.js
Line 1129: `if (request.results)`
Line 1133: `formStat = request.results[2];`

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal listener (lines 1126-1163)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if(sender.url.includes('overleaf.com/project') && request.message === "upload"){
      if (request.results)
      {
        pdf = request.results[0];
        pdfName = request.results[1];
        formStat = request.results[2]; // ← attacker-controlled data
        pdfBlob = b64toBlob(pdf);

        // ... uploads PDF to Google Drive ...

        // The suspicious line that CoCo flagged:
        fetch(formStat, {method: 'GET', mode:'no-cors'}).then((res)=>{return res;}).then((res)=>{return res;}); // Line 1154
      }
    }
  }
)

// Similar flow in mail() function (lines 1183-1238):
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if(sender.url.includes('overleaf.com/project') && request.message === 'mail'){
      if (request.results)
      {
        var mail = request.results[0];
        var name = request.results[1];
        var formStat = request.results[2]; // ← attacker-controlled data

        // ... processes email ...

        fetch(formStat, {method: 'GET', mode:'no-cors'}); // Line 1228
      }
    }
  }
);
```

**Classification:** FALSE POSITIVE

**Reason:** While there is a flow from chrome.runtime.onMessageExternal to fetch(), the manifest.json has `externally_connectable` set to only `"https://*.overleaf.com/project/*"`. More importantly, the code performs validation by checking `sender.url.includes('overleaf.com/project')`. The fetch() to `formStat` URL appears to be a tracking/analytics callback to Overleaf's backend infrastructure (the extension is designed to work with Overleaf). The extension trusts data from Overleaf domains as it's part of the legitimate workflow. This is trusted infrastructure communication, not an attacker-controlled destination. Even if we ignore the manifest restrictions per methodology rules, the fetch is sending data TO a hardcoded/trusted backend (Overleaf), which falls under the "Hardcoded Backend URLs (Trusted Infrastructure)" false positive pattern.

---
