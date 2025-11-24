# CoCo Analysis: achlegaapdgcnnhfmliagapbampafine

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (document_write_sink)

---

## Sink: document_body_innerText → document_write_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/achlegaapdgcnnhfmliagapbampafine/opgen_generated_files/cs_0.js
Line 29: Document_element.prototype.innerText = new Object();
Line 535: var beautified_text_plain = JSON.stringify(JSON.parse(original_body), null, 4);
Line 597: document.write(`</pre></td><td align='left'><pre id='json_content'>${beautified_text_final}</pre></td></tr></table>`);

**Code:**

```javascript
// Content script - jsonify.js (cs_0.js)
function jsonify(o) {
    saved_items = set_defaults(o.saved_items);
    var original_body = document.body.innerText; // Reading JSON from page
    var beautified_text_plain = JSON.stringify(JSON.parse(original_body), null, 4);
    var lines = beautified_text_plain.split('\n');

    // Formats the JSON text
    beautified_text_final = beautified_text_plain;

    if (setting_enable_name_format) {
        beautified_text_final = '';
        for(var i = 0; i < line_count; i++) {
            var line = lines[i];
            // ... formatting logic ...
            beautified_text_final += `<span class='name'>${lhs}</span>${rhs}\n`;
        }
    }

    // Write back to page
    document.write(`<pre id='json_content'>${beautified_text_final}</pre>`);
}

// Automatically runs on pages with JSON
var first_char = document.body.innerText[0];
if (first_char == '{' || first_char == '[') {
    chrome.storage.local.get('saved_items', jsonify);
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is a JSON beautifier extension that reads JSON content from the page's body.innerText (the same page context), processes it, and writes it back to the same page using document.write. This is NOT attacker-controlled data from an external source - it's the extension reading and reformatting content that's already on the page the user is viewing. There is no external attacker trigger (no message passing, no external events). The data flow is entirely within the same DOM context: page content → extension processes it → writes back to same page. This is the intended functionality of a JSON beautifier and does not represent a security vulnerability.
