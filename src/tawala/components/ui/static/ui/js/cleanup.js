/**
 * Cleanup CSP nonce meta tag after use
 */
const metaTag = document.querySelector("meta[name='csp-nonce']");
if (metaTag) metaTag.remove();
