# CoCo Analysis: jakahgbcggmbjgkfjghonlokknhkdfeg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → jQuery_ajax_settings_data_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jakahgbcggmbjgkfjghonlokknhkdfeg/opgen_generated_files/cs_0.js
Line 543    window.addEventListener("message", function (event) {
Line 544    if (event.data.type == 'llamar') {
Line 545    chrome.runtime.sendMessage({method:'llamar', tel: event.data.phone});

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jakahgbcggmbjgkfjghonlokknhkdfeg/opgen_generated_files/bg.js
Line 986    var v_data = 'token=' + token + '&llamado=' + telefono;
Line 988    v_data = v_data + '&no_grabar=1';
Line 989    v_data = v_data + '&source=chromext_llamada_web&app=chromext_llamada_web';

**Code:**

```javascript
// Content script (cs_0.js) - Lines 543-546
window.addEventListener("message", function (event) {
    if (event.data.type == 'llamar') {
        chrome.runtime.sendMessage({method:'llamar', tel: event.data.phone}); // ← attacker-controlled
    }
});

// Background script (bg.js) - Lines 975-1006
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.method == 'llamar') {
        var telefono = request.tel; // ← attacker-controlled
        chrome.storage.sync.get(null, function (login) {
            if (login && login['token']) {
                var token = login['token'];
                var canal = login['canal'];
                var bd = login['bd'];
                var grabar = login['grabar'];
                var mac = (login['mac']) ? login['mac'] : "";
                var mascara = login['mascara'];
                var nombre_mascara = login['nombre_mascara'];
                var llamante = login['llamante'];

                // Hardcoded backend URLs
                var v_url = 'https://scgi.duocom.es/cgi-bin/oficinaweb/oficinaweb_m_webcall';
                if (canal == '0' && bd == '12')
                    v_url = 'https://scgi.duocom.es/cgi-bin/telefacil2/telefacil_m_webcall';
                else if (canal == '0' && bd == '10')
                    v_url = 'https://cgi.duocom.es/cgi-bin/telefacil2/telefacil_m_webcall';
                else if (bd == '10')
                    v_url = 'https://cgi.duocom.es/cgi-bin/oficinaweb/oficinaweb_m_webcall';

                var v_data = 'token=' + token + '&llamado=' + telefono; // ← attacker-controlled phone in data
                if (grabar == 0)
                    v_data = v_data + '&no_grabar=1';
                v_data = v_data + '&source=chromext_llamada_web&app=chromext_llamada_web';

                $.ajax({
                    url: v_url, // ← hardcoded developer backend
                    type: 'post',
                    data: v_data, // ← attacker-controlled data sent to trusted backend
                    dataType: 'json',
                    async: true,
                    success: function (res) {
                        // ... notification handling ...
                    }
                });
            }
        });
    }
    return true;
});
```

**Classification:** FALSE POSITIVE

**Reason:** While the flow exists and an attacker can trigger it via window.postMessage, the attacker-controlled phone number is sent to the developer's own hardcoded backend servers (scgi.duocom.es, cgi.duocom.es). Per the methodology, data sent TO hardcoded developer backend URLs is considered trusted infrastructure. Compromising the developer's backend infrastructure is a separate issue from extension vulnerabilities. The attacker cannot control the destination URL, only the phone number parameter sent to the legitimate backend.

---

## Sink 2: cs_window_eventListener_message → jQuery_ajax_settings_data_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jakahgbcggmbjgkfjghonlokknhkdfeg/opgen_generated_files/cs_0.js
Line 543    window.addEventListener("message", function (event) {
Line 544    if (event.data.type == 'llamar') {
Line 545    chrome.runtime.sendMessage({method:'llamar', tel: event.data.phone});

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jakahgbcggmbjgkfjghonlokknhkdfeg/opgen_generated_files/bg.js
Line 986    var v_data = 'token=' + token + '&llamado=' + telefono;
Line 989    v_data = v_data + '&source=chromext_llamada_web&app=chromext_llamada_web';

**Classification:** FALSE POSITIVE

**Reason:** This is the same flow as Sink 1, just with a slightly different trace path (without the intermediate line 988). The assessment remains the same: attacker-controlled data is sent to the developer's hardcoded backend URLs (trusted infrastructure), which is not considered an exploitable vulnerability per the methodology.
