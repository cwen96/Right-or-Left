/*global chrome*/
const message = {
  type: "content",
  dom: document.documentElement.innerHTML,
};
chrome.runtime.sendMessage(message);
