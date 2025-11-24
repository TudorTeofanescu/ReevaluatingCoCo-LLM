# CoCo Analysis: ekaeipfbpbiebnlioffpapkflflmflfj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ekaeipfbpbiebnlioffpapkflflmflfj/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message', function(a){...chrome.storage.local.set({CompanyName:companyName})...})

**Code:**

```javascript
// Content script (cs_0.js) - Line 467 (minified, key parts extracted)
window.addEventListener('message', function(a) {
    if (event.origin !== WebModuleURL) return;

    // Handler for validatecompanny operation
    if (a.data !== undefined && a.data.Operation === 'validatecompanny' && a.data.CompanyData) {
        var g = a.data.CompanyData.filter(function(a){
            return a.companyname === companyName;
        });

        if (g.length === 1) {
            companyName = g[0].companyname; // ← attacker-controlled
            chrome.storage.local.set({CompanyName: companyName}); // ← sink
            chrome.storage.local.set({isValidatedCompanyName: 'True'});
        }
        else if (a.data.CompanyData.length === 1) {
            companyName = a.data.CompanyData[0].companyname; // ← attacker-controlled
            chrome.storage.local.set({CompanyName: companyName}); // ← sink
            chrome.storage.local.set({isValidatedCompanyName: 'True'});
        }
        else if (a.data.CompanyData.length > 1) {
            // Creates dialog for user to select company
            // When user clicks Save button:
            companyName = document.getElementsByTagName('option')[selectedIndex].innerText;
            chrome.storage.local.set({CompanyName: companyName}); // ← sink
            chrome.storage.local.set({isValidatedCompanyName: 'True'});
        }
    }
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (window.addEventListener)

**Attack:**

```javascript
// From any webpage matching content_scripts patterns:
// "*://*/bbAppFx/webui/*", "*://*/bbappfxunf-Aletheia/webui/*", "*://*/bbappfxunf-AliSPUpdate/webui/*"

// Note: The code checks if event.origin !== WebModuleURL, but this check has a vulnerability:
// If WebModuleURL is empty or attacker-controlled, the check can be bypassed

// Attack payload:
window.postMessage({
    Operation: 'validatecompanny',
    CompanyData: [{
        companyname: 'malicious_company_name_<script>alert(1)</script>',
        companydata: 'malicious_data'
    }]
}, '*');

// The extension will store the attacker-controlled companyname in chrome.storage.local
```

**Impact:** An attacker on pages matching the content_scripts patterns can send a postMessage to poison the extension's chrome.storage.local with an arbitrary CompanyName value. The vulnerability exists because:
1. The origin check `event.origin !== WebModuleURL` can be bypassed if WebModuleURL is not properly initialized or is empty
2. The attacker can control the `companyname` field in the CompanyData array
3. This stored company name may be used in subsequent operations, potentially causing:
   - XSS if the name is rendered without sanitization
   - Logic bypasses if the company name is used for authorization decisions
   - Data corruption in the PaperSave integration

**Note:** Per the methodology, this is classified as TRUE POSITIVE because:
1. External attacker can trigger the flow via window.postMessage (window.addEventListener)
2. Extension has required 'storage' permission in manifest.json
3. Attacker controls the data flowing to the sink (CompanyData.companyname)
4. Content script runs on specific Blackbaud CRM URLs, but per CRITICAL RULE #1, we ignore manifest restrictions
5. Per CRITICAL RULE #1: "If code has window.addEventListener('message'), assume ANY attacker can trigger it"
