# CoCo Analysis: nbkemmgoeipjjinkjmeldjcoonapafbi

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nbkemmgoeipjjinkjmeldjcoonapafbi/opgen_generated_files/bg.js
Line 981: console.log("Received message:", message.data);
Line 997: chrome.storage.sync.set({ userData: message.data }, ...

**Code:**

```javascript
// Background script (Lines 979-1005)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    console.log("Received message:", message.data);
    if (message.data == "LOGOUT") {
      console.log("User wants to log out");

      chrome.storage.sync.remove("userData", () => {
        console.log("User data removed from chrome.storage.sync");
        chrome.storage.sync.get(null, function (items) {
          console.log("Current contents of chrome.storage.sync:", items);
        });
        sendResponse("User logged out successfully");
      });
    } else {
      chrome.storage.sync.set({ userData: message.data }, () => {  // Storage poisoning
        console.log("User data saved to chrome.storage.sync");
        chrome.storage.sync.get(null, function (items) {
          console.log("Current contents of chrome.storage.sync:", items);
        });
        sendResponse("User data saved successfully");
      });
    }
  }
);

// Later retrieval and use (Lines 1082-1135)
async function getUserToken() {
  return new Promise((resolve, reject) => {
    chrome.storage.sync.get(["userData"], function (result) {
      if (result.userData && result.userData.accessToken) {
        const storedToken = result.userData.accessToken;
        console.log("Token found in Chrome storage:", storedToken);
        resolve(storedToken);
      } else {
        reject("Token not found in Chrome storage.");
      }
    });
  });
}

async function vectorizeData(webpageData) {
  try {
    const token = await getUserToken();
    const userID = await getUserID();
    webpageData["userID"] = userID;

    const response = await fetch(
      CEREBRUS_URL + "chromeWebsiteChunk",  // CEREBRUS_URL = "https://cerebrus-prod-eastus.azurewebsites.net/"
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,  // Token sent to hardcoded backend
        },
        body: JSON.stringify(webpageData),
      }
    );
    // ...
  }
}
```

**Manifest Configuration:**
```json
{
  "externally_connectable": {
    "matches": [
      "https://cerebrus-maximus.web.app/*",
      "http://localhost:3000/*"
    ]
  }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. The extension allows external messages to set userData (including accessToken) in chrome.storage.sync (storage poisoning). However, the stored token is only sent to the hardcoded developer backend URL (https://cerebrus-prod-eastus.azurewebsites.net/chromeWebsiteChunk). Per methodology: "Storage to hardcoded backend: storage.get → fetch(hardcodedBackendURL) = FALSE POSITIVE. Developer trusts their own infrastructure; compromising it is infrastructure issue, not extension vulnerability." The attacker cannot retrieve the poisoned token back, and it only flows to trusted infrastructure.
