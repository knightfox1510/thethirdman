// Runs inside the page. Records the JSON the page itself loads (as you scroll or click
// "load more") and hands each response to panel.js. It makes no requests of its own.
(() => {
  const send = (url, body) => {
    if (!body || typeof body !== "object") return;
    window.postMessage({ __ttm: true, url: String(url), body }, "*");
  };
  const wanted = (url) => /api|consumer|comments|scorecard|statistics|match/i.test(String(url));

  const origFetch = window.fetch;
  window.fetch = async function (...args) {
    const res = await origFetch.apply(this, args);
    try {
      const url = (args[0] && args[0].url) || args[0];
      const ct = res.headers.get("content-type") || "";
      if (wanted(url) && ct.includes("json")) res.clone().json().then((b) => send(url, b)).catch(() => {});
    } catch (e) {}
    return res;
  };

  const origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (m, url, ...rest) {
    this.__ttmUrl = url;
    this.addEventListener("load", () => {
      try {
        if (!wanted(url)) return;
        const t = this.responseType === "json" ? this.response : JSON.parse(this.responseText);
        send(url, t);
      } catch (e) {}
    });
    return origOpen.call(this, m, url, ...rest);
  };
})();
