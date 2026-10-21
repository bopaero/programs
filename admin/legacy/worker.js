// The old sf50-costing Worker, retired 2026-10-21: every address forwards to the same page on
// the bopaero-admin Worker, so bookmarks and old e-mail links keep working. It holds no
// secrets and touches no repo; the new Worker's own Access login still applies after the hop.
const NEW = 'https://bopaero-admin.compilotrc.workers.dev';
export default {
  fetch(request) {
    const url = new URL(request.url);
    // The SF50 editor used to be the root; everything else kept its path
    const path = url.pathname === '/' || url.pathname.startsWith('/api/') ? '/sf50' + url.pathname : url.pathname;
    return Response.redirect(NEW + path + url.search, 301);
  }
};
