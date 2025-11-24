# CoCo Analysis: fedlhlkkbmflfhmeffadldpojnielkgn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 16

---

## Sink: fetch_source → chrome_storage_local_set_sink (All instances)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fedlhlkkbmflfhmeffadldpojnielkgn/opgen_generated_files/bg.js
Line 265    var responseText = 'data_from_fetch';

(Note: CoCo detected 16 separate instances, all following the same pattern)

**Code:**

```javascript
// Background script - Message listener triggering fetchData()
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  fetchData();  // Triggered by internal message
  // ... other logic
});

function fetchData() {
  // POST request 1 - Fetching student grade totals from hardcoded university API
  fetch('https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreSungjukTot.do', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
  .then(response => response.json())
  .then(data => {
    chrome.storage.local.set({ AtnlcScreSungjukTot: data }, () => {});
  });

  // POST request 2 - Fetching student grade info
  fetch('https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreSungjukInfo.do', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
  .then(response => response.json())
  .then(data => {
    chrome.storage.local.set({ AtnlcScreSungjukInfo: data }, () => {});
  });

  // POST request 3 - Fetching student academic info
  fetch('https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreHakjukInfo.do', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
  .then(response => response.json())
  .then(data => {
    chrome.storage.local.set({ AtnlcScreHakjukInfo: data }, () => {});
  });

  // POST request 4 - Fetching general education course info
  fetch('https://klas.kw.ac.kr/std/cps/inqire/GyoyangIsuInfo.do', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
  .then(response => response.json())
  .then(data => {
    chrome.storage.local.set({GyoyangIsuInfo: data }, () => {});
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** All 16 detected flows involve fetching data from hardcoded university backend URLs (klas.kw.ac.kr - Kwangwoon University's learning management system). This is trusted infrastructure that the extension is designed to work with. The extension is a graduation simulation tool for university students that fetches academic data from the university's official API endpoints. The data comes from the university's servers (trusted infrastructure), not attacker-controlled sources. There is no external attacker trigger - the fetches are initiated by internal message passing within the extension's own functionality. This is internal extension logic, not an exploitable vulnerability.
