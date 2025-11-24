# CoCo Analysis: lhadpmpcjcobenognnngndjlghneikfe

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (all same flow: Document_element_href → chrome_storage_local_set_sink)

---

## Sink: Document_element_href → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhadpmpcjcobenognnngndjlghneikfe/opgen_generated_files/cs_0.js
Line 20: this.href = 'Document_element_href' (CoCo framework mock code)

CoCo detected this flow only in framework code (before third "// original" marker at line 465). The actual extension code does not use document.href or element.href in any way.

**Code:**

```javascript
// CoCo Framework Code (Line 20) - NOT actual extension code
function Document_element(id, class_name, tag) {
    this.id = id;
    this.class_name = class_name;
    this.tag = tag;
    this.href = 'Document_element_href'; // ← CoCo framework mock
    MarkSource(this.href, 'Document_element_href');
}

// Actual Extension Code (Lines 465-544) - nicecursorcontent.js
// The extension manages custom cursor styles:

nicecursorstyleManager = function(e) {
    var check_popup_page = document.body.contains(document.getElementById("use_system_cursors"));
    cur_storage.get(local_values, function(data) {
        var default_curSize = data.default_curSize;
        var pointer_curSize = data.pointer_curSize;
        var dSrc = data.default_cursor_result; // ← cursor image source from storage
        var pSrc = data.pointer_cursor_result;
        var switch_status = data.switch_status;
        var cssElm = data.css_elm;

        if (e === "create" && switch_status == "true") {
            let t = "";
            // Build CSS for cursor styles
            if (typeof dSrc !== "undefined" && dSrc.length > 0)
                t = t + cursorADD + ".mc_default { cursor: url(" + dSrc + "), default !important; } ";
            if (typeof pSrc !== "undefined" && pSrc.length > 0)
                t = t + pointerADD + ".mc_pointer { cursor: url(" + pSrc + "), pointer !important; } ";

            if (!check_popup_page) {
                // Create style element with cursor CSS
                document.querySelectorAll('[cursors="cursors_style_code"]').forEach(el => el.remove());
                cursors_style_code = t;
                cssElm = document.createElement("style");
                cssElm.rel = "stylesheet";
                cssElm.setAttribute("cursors", "cursors_style_code");
                cssElm.innerHTML = t; // ← CSS string, not document.href
                document.head.appendChild(cssElm);
            }
        }

        cur_storage.set({
            css_elm: cssElm // ← stores style element, no connection to document.href
        });
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** CoCo only detected this flow in framework mock code (Document_element.href). The actual extension code (after line 465) does not read or use document.href or any element.href property. The extension creates custom cursor styles by reading cursor image URLs from storage, building CSS strings, and storing the resulting style element. There is no data flow from document.href to chrome.storage.local.set in the actual extension implementation.
