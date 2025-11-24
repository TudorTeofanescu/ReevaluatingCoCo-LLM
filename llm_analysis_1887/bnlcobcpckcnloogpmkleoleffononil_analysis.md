# CoCo Analysis: bnlcobcpckcnloogpmkleoleffononil

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bnlcobcpckcnloogpmkleoleffononil/opgen_generated_files/bg.js
Line 1059	    if (request.token) {

**Code:**

```javascript
// Background script - External message listener
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    if (request.token) {
      sendResponse({
        success: true,
        message: `Token has been received`,
      })

      chrome.storage.local.set({ token: request.token }) // Storage write
    }
  }
)

// Token retrieval and usage
chrome.contextMenus.onClicked.addListener(async (info) => {
  const { menuItemId } = info

  // Retrieve poisoned token from storage
  const { token } = await chrome.storage.local
    .get(['token'])
    .then((result) => result)

  const API_URL = 'https://api.memoriae.io/memories' // Hardcoded backend

  if (menuItemId === 'save-in-memoriae-normal') {
    // Token sent to hardcoded developer backend
    const response = await fetch(API_URL, {
      headers: {
        'Content-Type': 'application/json',
        authorization: 'Digest ' + token, // Poisoned token sent to trusted backend
        provider: 'credentials',
      },
      method: 'POST',
      body: JSON.stringify({ url: tab.url }),
    })
  }
})
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation without retrieval path to attacker. Although an external source (memoriae.io or localhost:3000 based on externally_connectable in manifest) can send a malicious token via chrome.runtime.sendMessageExternal, and this token gets stored in chrome.storage.local, the stored token is only sent to the hardcoded developer backend URL (https://api.memoriae.io/memories). The poisoned token goes to trusted infrastructure (developer's own backend), not to any attacker-controlled destination. There is no retrieval path where the attacker can observe or retrieve the poisoned token value. According to the methodology, storage poisoning alone without retrieval to attacker is NOT exploitable.
