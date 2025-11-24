# CoCo Analysis: cnfmojhcmleelapdiapckcdlkgbmdolh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: fetch_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cnfmojhcmleelapdiapckcdlkgbmdolh/opgen_generated_files/bg.js
Line 978: const response = JSON.parse(result);
Line 981: kwsEverywhereToken: response.data.token,
Line 982: kwsEverywhereEndpoints: response.data.endpoints,

**Code:**

```javascript
// Background script - bg.js (Lines 965-993)
chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.get(['kwsEverywhereToken'], (result) => {
        const kwsApiUrl = "https://kwseverywhere.com/api/v1/auth/token"; // ← hardcoded backend URL

        if (result.kwsEverywhereToken == undefined) {
            const requestOptions = {
                method: "POST",
                redirect: "follow"
            };

            fetch(kwsApiUrl, requestOptions) // ← fetch to hardcoded backend
            .then((response) => response.text())
            .then((result) => {
                const response = JSON.parse(result); // ← data from hardcoded backend

                chrome.storage.local.set({
                    kwsEverywhereToken: response.data.token, // ← storage.set with backend data
                    kwsEverywhereEndpoints: response.data.endpoints,
                    kwsEverywhereSettings: {
                        location: '01jd561te3xxk5k3ypwksax056',
                        language: '01jdky88b88xbbrjertqyan6dx',
                        network: 'GOOGLE_SEARCH',
                        allowAdultKeywords: false
                    }
                });
            })
        }
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** No external attacker trigger. The flow is triggered only by `chrome.runtime.onInstalled` (internal extension lifecycle event, not externally triggerable). Additionally, the data flows from a hardcoded backend URL (`https://kwseverywhere.com/api/v1/auth/token`) which is trusted infrastructure, not attacker-controlled.

---

## Sink 2: fetch_source → chrome_storage_local_set_sink (variant)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cnfmojhcmleelapdiapckcdlkgbmdolh/opgen_generated_files/bg.js
Line 978: const response = JSON.parse(result);
Line 981: kwsEverywhereToken: response.data.token,
(Same as Sink 1, different trace path)

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - no external attacker trigger, data from hardcoded trusted backend.

---

## Sink 3: fetch_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cnfmojhcmleelapdiapckcdlkgbmdolh/opgen_generated_files/bg.js
Line 1008: const response = JSON.parse(result);
Line 1015: kwsEverywhereToken: response.data.token,
Line 1016: kwsEverywhereEndpoints: response.data.endpoints,

**Code:**

```javascript
// Background script - bg.js (Lines 1005-1024)
// else branch of same onInstalled listener
fetch(kwsApiUrl, requestOptions) // ← fetch to hardcoded backend
.then((response) => response.text())
.then((result) => {
    const response = JSON.parse(result); // ← data from hardcoded backend

    chrome.storage.local.clear(() => {
        console.log('Storage cleared.');
    });

    chrome.storage.local.set({
        kwsEverywhereToken: response.data.token, // ← storage.set with backend data
        kwsEverywhereEndpoints: response.data.endpoints,
        kwsEverywhereSettings: {
            location: '01jd561te3xxk5k3ypwksax056',
            language: '01jdky88b88xbbrjertqyan6dx',
            network: 'GOOGLE_SEARCH',
            allowAdultKeywords: false
        }
    });
})
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - no external attacker trigger, data from hardcoded trusted backend.

---

## Sink 4: fetch_source → chrome_storage_local_set_sink (variant)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cnfmojhcmleelapdiapckcdlkgbmdolh/opgen_generated_files/bg.js
Line 1008: const response = JSON.parse(result);
Line 1015: kwsEverywhereToken: response.data.token,
(Same as Sink 3, different trace path)

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 3 - no external attacker trigger, data from hardcoded trusted backend.
