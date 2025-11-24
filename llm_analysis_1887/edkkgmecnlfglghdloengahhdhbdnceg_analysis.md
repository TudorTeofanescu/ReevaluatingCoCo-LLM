# CoCo Analysis: edkkgmecnlfglghdloengahhdhbdnceg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 18 (all same pattern, only detected in CoCo framework code)

---

## Sink: fetch_source → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/edkkgmecnlfglghdloengahhdhbdnceg/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';`

CoCo only detected flows in the framework mock code (line 265 is in the fetch mock implementation). The actual extension code starts at line 963.

**Code:**

```javascript
// Service worker - minified, starting at line 965
// Function fs() performs multiple fetch operations to hardcoded backend
function fs() {
  console.log("requests");

  // Fetch constants
  fetch("https://api.asakicorp.com/joblife/constants", {
    method: "GET",
    cache: "no-store"
  })
  .then((e => e.json()))
  .then((e => {
    chrome.storage.local.set({
      JOBLIFE_SOCIALS: e.socials,
      JOBLIFE_MEMBERS: e.members
    })
  }))
  .catch((e => {}));

  // Fetch Twitch data
  fetch("https://api.asakicorp.com/joblife/twitch", {
    method: "GET",
    cache: "no-store"
  })
  .then((e => e.json()))
  .then((e => {
    chrome.storage.local.set({JOBLIFE_STREAMERS: e})
  }))
  .catch((e => {}));

  // Fetch YouTube videos
  fetch("https://api.asakicorp.com/joblife/youtube", {
    method: "GET",
    cache: "no-store"
  })
  .then((e => e.json()))
  .then((e => {
    chrome.storage.local.set({JOBLIFE_YOUTUBE_VIDEOS: e})
  }))
  .catch((e => {}));

  // Multiple additional fetches to:
  // - /joblife/matches
  // - /joblife/teams
  // - /joblife/rosters
  // - /joblife/standings
  // - /joblife/security
  // - /joblife/notification
  // - /joblife/notifications
  // All following the same pattern: fetch from api.asakicorp.com → store in chrome.storage.local
}

// Function fs() is called automatically on timers:
setTimeout(fs, 100);  // Called 100ms after startup

setInterval(() => {
  fs();
  setTimeout(b, 1e3);
}, 3e4);  // Called every 30 seconds

// Also called on startup
chrome.runtime.onStartup.addListener((() => {
  console.log("WORKER STARTUP")
}));
```

**Classification:** FALSE POSITIVE

**Reason:** This is a false positive for multiple reasons:

1. **Hardcoded Backend Infrastructure**: All fetch operations go to the developer's own hardcoded backend URLs (`https://api.asakicorp.com/joblife/*`). The extension fetches data from its trusted backend and stores it locally. This is the developer's infrastructure, not attacker-controlled.

2. **No External Attacker Trigger**: The fetch operations are triggered only by internal timers (`setTimeout`, `setInterval`) and startup events. There are no content scripts, no message handlers (`chrome.runtime.onMessage`), and no way for an external attacker to trigger or influence these fetch operations.

3. **Internal Data Synchronization**: This is a standard data synchronization pattern where the extension periodically fetches fresh data from its backend (match schedules, team rosters, streamer status, etc.) and caches it locally. This is internal extension logic only.

4. **Host Permissions Match Backend**: The manifest declares host permissions for `*://*.asakicorp.com/*`, which matches the fetch destinations, confirming these are intended, legitimate backend calls.

The flow exists: `fetch(hardcoded_backend) → response → chrome.storage.local.set(response)`, but this is entirely internal extension logic with no external attacker control point.
