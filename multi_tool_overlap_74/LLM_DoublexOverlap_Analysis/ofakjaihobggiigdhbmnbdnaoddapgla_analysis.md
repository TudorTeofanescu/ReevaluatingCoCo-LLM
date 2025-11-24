# CoCo Analysis: ofakjaihobggiigdhbmnbdnaoddapgla

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (cs_window_eventListener_message to fetch_resource_sink)

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ofakjaihobggiigdhbmnbdnaoddapgla/opgen_generated_files/cs_0.js
Line 500: window.addEventListener("message", function(event)
Line 553: asin: event.data.asin

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ofakjaihobggiigdhbmnbdnaoddapgla/opgen_generated_files/bg.js
Line 1210: var eligibilityURL = baseURL + "/hz/approvalrequest/restrictions/approve?cor=mmp_EU&asin=" + request.asin
Line 1218: fetch(eligibilityURL, { method: 'GET', credentials: 'include' })

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 500)
window.addEventListener("message", function(event) {
  if (event.source != window) return;
  if (!event.data.type) return;

  if (event.data.type == "FROM_PAGE_ELIGIBLE") {
    chrome.runtime.sendMessage(
      {
        type: 'IS_ELIGIBLE',
        dir_mcid: event.data.dir_mcid,
        dir_paid: event.data.dir_paid,
        asin: event.data.asin, // ← attacker-controlled
        region: event.data.region // ← attacker-controlled
      },
      function(response) {
        // ...
      }
    );
  }
});

// Background script - Message handler (bg.js line 1087-1218)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  var baseURL = "https://sellercentral-europe.amazon.com"; // ← hardcoded trusted domain

  if (request.type == 'IS_ELIGIBLE') {
    // Builds URL with attacker-controlled parameters but hardcoded base
    var eligibilityURL = baseURL + "/hz/approvalrequest/restrictions/approve?cor=mmp_EU&asin=" + request.asin
    if (request.region)
      eligibilityURL += "&mons_sel_mkid=" + MKIDS[request.region.toUpperCase()];
    if (request.dir_mcid)
      eligibilityURL += "&mons_sel_dir_mcid=" + request.dir_mcid
    if (request.dir_paid)
      eligibilityURL += "&mons_sel_dir_paid=" + request.dir_paid

    // Fetch to hardcoded Amazon domain
    fetch(eligibilityURL, { method: 'GET', credentials: 'include' })
      .then(eligibilityResponse => {
        // ...
      });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** While an attacker can control URL parameters (asin, region, dir_mcid, dir_paid) via window.postMessage, the fetch request is made to a hardcoded trusted backend URL (https://sellercentral-europe.amazon.com). This falls under pattern X from the methodology: "Data TO hardcoded backend" - the developer trusts their own infrastructure. Compromising Amazon's infrastructure is an infrastructure issue, not an extension vulnerability. The attacker cannot redirect the request to an arbitrary domain.
