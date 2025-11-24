# CoCo Analysis: bdiahcebghgckgbgmjhdbecjkedpcidn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple instances of bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdiahcebghgckgbgmjhdbecjkedpcidn/opgen_generated_files/bg.js
Line 965: Minified code containing `chrome.runtime.onMessageExternal.addListener` and `chrome.tabs.executeScript`

**Code (Formatted from minified source):**

```javascript
// Background script - External message listener
chrome.runtime.onMessageExternal.addListener(function(e, t, n) {
  var r = e.url,
      a = e.testId,  // ← Attacker-controlled
      i = e.useNewEditor,
      o = e.config,
      c = e.action,
      d = e.useSecureApiToken;

  switch(c) {
    case "launchEmbedEditor":
      return TEST.url = r, TEST.testId = a, TEST.useNewEditor = i, ...;
    case "launchHeatmap":
      return _launchHeatmap(o, t);  // ← Calls with config object
    case "launchPreview":
      return _launchPreview(o, t);
    case "launchSimulationBar":
      return _launchSimulationBar(o, t);
  }
  n({response: "success"});
});

// Heatmap launch function
function _launchHeatmap(e, t) {
  var n = e.testId,  // ← Attacker-controlled from config
      r = e.variationId,  // ← Attacker-controlled from config
      a = "previewHeatmap.php?testID=" + n + "&variationID=" + r;  // ← URL query params only
  _launchProject(t, e, a);
}

// Similar for _launchPreview
function _launchPreview(e, t) {
  var n = e.testId,
      r = e.variationId,
      a = e.disabledModifications,
      i = a.length > 0 ? "&disabledModifications=" + a.join() : "",
      o = "previewVariation.php?testID=" + n + "&variationID=" + r + i;
  window.isPreviewLaunched || _launchProject(t, e, o);
}

// Project launcher - constructs HARDCODED backend URL
function _launchProject(e, t, n) {
  var r = e.tab.id,
      a = t.url,
      i = t.environment,
      o = getDomain(i),  // ← Returns hardcoded abtasty.com domains
      c = o + "/ready/" + n,  // ← HARDCODED base URL + attacker params
      d = {code: _getInjectScriptUrlTag(c)};  // ← Creates script injection code

  chrome.tabs.update(r, {url: a}, function() {
    function e(t, n) {
      t === r && "complete" === n.status && (chrome.tabs.executeScript(r, d), ...);
    }
    _addListener(e);
  });
}

// Returns HARDCODED backend domains
function getDomain() {
  var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : "prod",
      t = {prod: "app", preprod: "preprod-app", local: "local.app"};
  return "https://" + t[e] + ".abtasty.com";  // ← HARDCODED: always abtasty.com
}

// Generates script injection code with HARDCODED src URL
function _getInjectScriptUrlTag(e) {
  var t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {},
      n = LOCAL ? "local." : "",
      r = Object.entries(t).reduce(function(e, t) {
        var n = _slicedToArray(t, 2), r = n[0], a = n[1];
        return e + '\nscript.setAttribute("' + r + '", "' + a + '");';
      }, ""),
      a = "\n        var script = document.createElement('script');\n        script.src = '" + n + e + "';\n        " + r + "\n        (document.head || document.documentElement).appendChild(script);\n    ";
  return a;
}

// For launchEmbedEditor case - also uses HARDCODED URL
function _loadEditorTarget(e, t, n) {
  var o = "https://teddytor.abtasty.com/dist/main.js";  // ← HARDCODED URL
  ...
  _executeScript(e, o, TEST.testId);  // ← testId only used as HTML attribute
}

function _executeScript(e, t, n) {
  chrome.tabs.executeScript(e, {
    code: _getInjectScriptUrlTag(t, {id: "abtasty-editor", "data-campaignid": n})
  });  // ← n (testId) only sets HTML attribute value, t (URL) is hardcoded
}
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend infrastructure (trusted URLs). While the extension accepts external messages from abtasty.com domains and uses attacker-controlled `testId` and `variationId` parameters, these values are only used in two ways:

1. **As URL query parameters to hardcoded backend**: The extension constructs URLs like `https://app.abtasty.com/ready/previewHeatmap.php?testID=<attacker-controlled>&variationID=<attacker-controlled>`, where the base domain is always hardcoded to `abtasty.com` (via `getDomain()` function)

2. **As HTML attribute values**: The testId is used to set the `data-campaignid` attribute on injected script tags, but the `src` attribute is always a hardcoded abtasty.com URL (`https://teddytor.abtasty.com/dist/main.js` or URLs constructed with hardcoded base domains)

Per the methodology: "Data TO/FROM hardcoded backend URLs (trusted infrastructure) = FALSE POSITIVE. Developer trusts their own infrastructure; compromising it is infrastructure issue, not extension vulnerability."

The attacker cannot:
- Load scripts from attacker-controlled domains
- Execute arbitrary JavaScript code
- Inject malicious script URLs

The attacker can only:
- Specify query parameters sent to the developer's own abtasty.com backend
- Set HTML attribute values on script tags that load from abtasty.com

While external messages can be sent from abtasty.com domains (per manifest `externally_connectable`), the flow only allows manipulation of parameters sent to trusted infrastructure, not execution of attacker-controlled code.
