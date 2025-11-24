# CoCo Analysis: lnlohfhabkgnelnpbacookjnnfklehii

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: document_body_innerText → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lnlohfhabkgnelnpbacookjnnfklehii/opgen_generated_files/cs_0.js
Line 29	Document_element.prototype.innerText = new Object();
	new Object()
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lnlohfhabkgnelnpbacookjnnfklehii/opgen_generated_files/cs_0.js
Line 489	    if (page.startsWith("--styleme stylescript v1.0--")) {
	page.startsWith("--styleme stylescript v1.0--")
```

**Analysis:**

CoCo detected a flow where Line 29 is in the CoCo framework code. Examining the actual extension code (after the third "// original" marker at line 465), the complete flow is:

**Code:**
```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("load", async () => {
    let page = document.body.innerText; // ← attacker-controlled (webpage can set body text)
    if (page.startsWith("--styleme stylescript v1.0--")) {
        console.log("[styleme] found stylescript on page!");

        let style = await stylescript.parse(page);
        if (styles.map(s => s.hash).includes(style.hash)) {
            return;
        }

        if (!style || style.version !== 1.0 || !style.css || !style.title || (!style.url && !style.global)) {
            return alert("[ERROR] Unable to load this stylescript.")
        }
        let install = confirm(`[styleme]\nInstall stylescript "${style.title}"?`);

        if (install) {
            console.log("[styleme] installing stylescript...");
            stylescripts.push(page); // ← attacker-controlled data

            chrome.storage.local.set({
                stylescripts // ← storage poisoning
            }, () => {
                try {
                    if(!style.url)
                        return;

                    let url = new URL(style.url);
                    if (url.protocol === "http:" || url.protocol === "https:") {
                        let redir = confirm("[styleme]\nStylescript installed successfully!\nTry out your new style?");
                        if (redir) {
                            console.log("[styleme] redirecting to stylescript url!");
                            location.href = style.url;
                        }
                    }
                } catch (err) {}
            });
        }
    }
}, false);

// Retrieval but no path back to attacker
chrome.storage.local.get('stylescripts', async (result) => {
    stylescripts = result.stylescripts || [];
    styles = await Promise.all(stylescripts.map(s => stylescript.parse(s)));

    console.log(stylescripts, styles);

    let active = styles.filter(s => location.href.startsWith(s.url) || s.global);
    let css = active.map(s => s.css).join("\n\n");

    if (css) {
        chrome.runtime.sendMessage({
            method: "installCSS",
            css // ← used for CSS injection, not sent back to attacker
        });
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While an attacker can control `document.body.innerText` and poison `chrome.storage.local` with malicious stylescript data, there is no retrieval path back to the attacker. The stored data is retrieved and used for CSS injection via `chrome.scripting.insertCSS` (see background.js line 987), but the attacker cannot retrieve the poisoned value back. According to the methodology, storage poisoning alone is NOT a vulnerability - the stored data MUST flow back to the attacker via sendResponse/postMessage, be used in fetch() to attacker-controlled URL, or used in executeScript/eval. CSS injection without data exfiltration does not meet the exploitable impact criteria.

---

## Sink 2: document_body_innerText → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lnlohfhabkgnelnpbacookjnnfklehii/opgen_generated_files/cs_0.js
Line 29	Document_element.prototype.innerText = new Object();
	new Object()
```

**Classification:** FALSE POSITIVE

**Reason:** Same flow as Sink 1. Incomplete storage exploitation - no retrieval path to attacker.
