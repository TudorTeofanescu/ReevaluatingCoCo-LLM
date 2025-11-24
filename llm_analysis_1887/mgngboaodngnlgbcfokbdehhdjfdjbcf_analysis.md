# CoCo Analysis: mgngboaodngnlgbcfokbdehhdjfdjbcf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (all identical flows)

---

## Sink: fetch_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mgngboaodngnlgbcfokbdehhdjfdjbcf/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';` (CoCo framework code)

**Classification:** FALSE POSITIVE

**Reason:** Data FROM hardcoded backend URLs is trusted infrastructure (per CoCo methodology rule #3 and FP pattern X). The extension fetches data from a hardcoded Azure Blob Storage URL (`https://azi.blob.core.windows.net/hltv/matches.json`) owned by the developer and stores it locally. This is internal extension logic with no external attacker trigger. Compromising the developer's backend infrastructure is a separate issue, not an extension vulnerability.

**Code:**

```javascript
// Background script (bg.js lines 965-1005)
function fetchDataAndStore() {
  console.log("Attempting to fetch data...");

  fetch(
    `https://azi.blob.core.windows.net/hltv/matches.json?timestamp=${new Date().getTime()}`
  )
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Data fetched:", data);
      chrome.storage.local.set({ matchesData: data }, () => {
        console.log("Data fetched and stored.");

        // Calculate live matches count
        const liveMatchesCount = data.filter((match) => {
          if (match.date === "Date not specified") {
            const now = new Date();
            const recordDate = new Date(match.recordDate);
            const hoursDiff = (now - recordDate) / 3600000;
            return hoursDiff <= 3;
          }
          return false;
        }).length;

        // Update the badge
        if (liveMatchesCount > 0) {
          chrome.action.setBadgeText({ text: liveMatchesCount.toString() });
          chrome.action.setBadgeBackgroundColor({ color: "#2b6ea4" });
        } else {
          chrome.action.setBadgeText({ text: "" });
        }
      });
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

// Triggered by extension lifecycle events only
chrome.runtime.onStartup.addListener(() => {
  fetchDataAndStore();
});
```

The extension is an HLTV matches viewer that fetches data from the developer's own backend. No attacker control over the fetch URL or the flow.

---
