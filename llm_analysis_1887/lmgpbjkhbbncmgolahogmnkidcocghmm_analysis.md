# CoCo Analysis: lmgpbjkhbbncmgolahogmnkidcocghmm

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (tracking document_body_innerText variations)

---

## Sink: document_body_innerText → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lmgpbjkhbbncmgolahogmnkidcocghmm/opgen_generated_files/cs_0.js
Line 29: Document_element.prototype.innerText = new Object();

**Analysis:**

CoCo only detected flows in framework code (Line 29 is in the CoCo framework header, before the 3rd "// original" marker at line 465). The actual extension code starts at line 465.

**Actual Extension Behavior:**

The extension "AutoSave & Recovery" is a legitimate form autosave/recovery tool. Looking at the actual extension code (minified in lines 467-476):

```javascript
// Simplified/deobfuscated flow from the minified code:

// Function M extracts text from HTML elements
const M = e => {
    var t, n = document.createElement("div");
    n.innerHTML = e;
    var i = n.querySelector("p");
    return i && (null === (t = i.parentNode) || void 0 === t || t.removeChild(i)),
    n.innerText  // ← Uses innerText to extract text from HTML
};

// Function B creates a record from form input elements
function B(e, t) {
    return {
        category: e,
        text: M((t.val() || "").toString().trim()),  // ← Gets value from input element
        page: I(),  // Current page URL
        date: (new Date).toISOString(),
        type: t.prop("type"),
        xpath: _(t)
    }
}

// Function z stores the data
function z(e, t) {
    const i = B(t, e);
    // ... stores to chrome.storage.local.set({menu: b()}, ...)
}

// Triggered on blur events for form inputs
e.addEventListener("blur", (e => function(e) {
    b().settings.activeAutoSave && R($(e.target), "AutoSave")
}(e)))
```

**Classification:** FALSE POSITIVE

**Reason:** This is internal extension logic only, with no external attacker trigger. The extension monitors form input elements (text, password, email, etc.) on web pages and automatically saves their values to local storage when users blur (leave) the input fields. While this functionality involves reading page content (via innerText during HTML sanitization), it is:

1. **No External Attacker Trigger**: The autosave is triggered by legitimate user interactions (blur events on form inputs the user is actually filling out), not by any attacker-controllable mechanism like postMessage or external messages.

2. **Incomplete Storage Exploitation**: While data is written to chrome.storage.local, there is no retrieval path that sends this data back to an attacker via sendResponse, postMessage, or attacker-controlled URLs.

3. **Legitimate Extension Functionality**: This is the core intended functionality of an autosave extension - it saves form data for user recovery purposes.

The innerText usage in function M is for sanitizing HTML content from form values, not for reading attacker-controlled document.body.innerText directly. CoCo's detection appears to be a false positive from analyzing the framework code rather than the actual extension's vulnerable data flows.
