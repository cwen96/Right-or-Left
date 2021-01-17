/*global chrome*/
chrome.runtime.onMessage.addListener(receiver);

function receiver(request, sender, sendResponse) {
  document.documentElement.innerHTML = request.dom;
  dom = document;
}
