"""Local knowledge base used to generate beginner-friendly remediation guidance."""

KNOWLEDGE = {
    "missing_csp": (
        "A Content-Security-Policy is a rulebook that tells the browser which websites may provide scripts, images and other resources to your page.",
        "Without that rulebook, a browser will happily run script from anywhere, which makes injected script much more damaging.",
        "Define a policy with explicit allowed sources rather than allowing everything by default.",
        "Start with a strict policy in report-only mode, fix violations, then enforce it. Use nonces or hashes instead of allowing inline scripts.",
    ),
    "missing_xframe": (
        "X-Frame-Options tells browsers whether your page is allowed to be displayed inside a frame on another website.",
        "If framing is allowed, an attacker can place a transparent frame over your page and trick users into clicking hidden buttons.",
        "Send X-Frame-Options: SAMEORIGIN and add the frame-ancestors directive to your Content-Security-Policy.",
        "Review all pages that legitimately need framing and use an explicit allowlist rather than allowing every origin.",
    ),
    "missing_hsts": (
        "HSTS is a header that tells browsers to always use HTTPS for this site, even if a user types http:// or follows an old link.",
        "Without it, an attacker on the same network could strip TLS and read or change traffic before it reaches the server.",
        "Send Strict-Transport-Security with a long max-age on every HTTPS response.",
        "Confirm all subdomains support HTTPS, then add includeSubDomains and consider HSTS preloading.",
    ),
    "missing_nosniff": (
        "Browsers sometimes guess a file's type instead of trusting the type the server declares. This header stops that guessing.",
        "A file that looks like text to the server could be interpreted as script by the browser and execute unwanted code.",
        "Add X-Content-Type-Options: nosniff to every response.",
        "Always set correct Content-Type values and serve uploaded files from a separate, hardened origin.",
    ),
    "missing_referrer_policy": (
        "The Referrer-Policy header controls how much of the current URL is shared when a user follows a link to another site.",
        "Full URLs can contain search terms, record identifiers or tokens that should not be shared with third parties.",
        "Set Referrer-Policy: strict-origin-when-cross-origin.",
        "Avoid putting sensitive values in URLs and review analytics scripts that read document.referrer.",
    ),
    "missing_permissions_policy": (
        "Permissions-Policy limits which powerful browser features a page and its embedded content may use.",
        "Without limits, injected or third-party script may request camera, microphone or location access.",
        "Send a restrictive Permissions-Policy header listing only the features your application needs.",
        "Audit third-party scripts and remove features that are not required for the product.",
    ),
    "weak_xframe": (
        "Some older framing directives are not consistently supported by modern browsers.",
        "A browser that ignores the directive could allow clickjacking even though a header is present.",
        "Use X-Frame-Options: SAMEORIGIN together with CSP frame-ancestors.",
        "Prefer modern standards and keep an explicit allowlist of trusted framing origins.",
    ),
    "weak_hsts_max_age": (
        "The HSTS lifetime tells the browser how long it must remember to use only HTTPS.",
        "A short lifetime means the protection disappears quickly and users can be downgraded again.",
        "Increase max-age to at least 31536000 seconds (one year).",
        "Roll out longer values gradually and monitor for HTTPS errors before enabling preload.",
    ),
    "hsts_no_subdomains": (
        "This HSTS policy protects only the exact hostname that sent it, not subdomains.",
        "A subdomain that handles login sessions could still be accessed over plain HTTP.",
        "Add the includeSubDomains attribute once every subdomain supports HTTPS.",
        "Inventory subdomains first to avoid accidentally breaking internal services.",
    ),
    "unsafe_inline": (
        "The policy currently permits inline script or style code to run.",
        "An attacker who can inject a small piece of HTML can still execute inline JavaScript despite the policy.",
        "Replace inline scripts with external files or use a per-response nonce or hash.",
        "Build a Content-Security-Policy nonce into the server template and avoid inline event handlers.",
    ),
    "unsafe_eval": (
        "The policy permits JavaScript to generate and execute code dynamically.",
        "Many DOM XSS techniques rely on eval-like functions, so allowing them weakens the final defence layer.",
        "Remove unsafe-eval and refactor code that builds script from strings.",
        "Use JSON.parse for data and safe DOM APIs for rendering instead of string-to-code patterns.",
    ),
    "wildcard_source": (
        "A wildcard in the policy allows resources from many origins.",
        "A broad source list makes it easier for injected content to load allowed script or data.",
        "List explicit trusted origins instead of using *.",
        "Prefer a small allowlist and verify each third-party dependency.",
    ),
    "no_object_src": (
        "The policy does not explicitly block browser plug-in content.",
        "Legacy plug-ins can be loaded if the default source is broad, expanding the attack surface.",
        "Add object-src 'none' to the policy.",
        "Remove plug-in dependencies and keep the policy minimal.",
    ),
    "no_base_uri": (
        "The policy does not restrict where a base tag may point.",
        "An injected base tag can hijack relative script and link URLs without changing the script tag itself.",
        "Add base-uri 'self' to the policy.",
        "Avoid relative URLs for critical resources and sanitise user-provided HTML.",
    ),
    "no_frame_ancestors": (
        "The policy does not declare which sites may frame this application.",
        "Without a modern framing directive, protection depends on an older header that not every browser honours.",
        "Add frame-ancestors 'none' or an explicit allowlist.",
        "Test embedded dashboards and widgets after adding the directive.",
    ),
    "http_not_enforced": (
        "The site answers over plain HTTP, which sends data without encryption.",
        "Anyone on the network path can read passwords and tokens or change page content before it arrives.",
        "Enable HTTPS with a valid certificate and redirect all HTTP requests to HTTPS.",
        "Use HSTS, keep TLS configuration modern, and never submit credentials over HTTP.",
    ),
    "invalid_tls_certificate": (
        "The TLS certificate is not trusted for this hostname or has a validation problem.",
        "Users cannot be sure they are talking to the real server, and browsers show a security warning.",
        "Install the correct certificate chain issued by a trusted authority for the hostname.",
        "Automate renewal and verify the full chain with a TLS configuration checker.",
    ),
    "tls_handshake_failed": (
        "A trusted encrypted connection could not be established.",
        "Clients may fail to connect or fall back to unsafe settings.",
        "Configure a complete certificate chain and modern cipher suites.",
        "Test the configuration with SSL Labs or an equivalent tool before deployment.",
    ),
    "weak_tls_version": (
        "The server negotiated an old TLS protocol version.",
        "Old TLS versions have known weaknesses that can allow decryption or downgrade attacks.",
        "Disable TLS 1.0 and 1.1 and allow only TLS 1.2 or 1.3.",
        "Keep the web server and TLS library patched and review cipher configuration.",
    ),
    "tls_cert_expiring": (
        "The TLS certificate is close to its expiry date.",
        "An expired certificate breaks trust warnings and may stop users from reaching the application.",
        "Renew the certificate before it expires.",
        "Automate renewal with ACME and add monitoring alerts for certificate expiry.",
    ),
    "cookie_missing_httponly": (
        "A cookie can be read by JavaScript running on the page.",
        "If script injection happens elsewhere, an attacker can steal that cookie and reuse the user's session.",
        "Add the HttpOnly attribute when the server sets the cookie.",
        "Only omit HttpOnly for cookies that genuinely need client-side access, and keep them non-sensitive.",
    ),
    "cookie_missing_secure": (
        "A cookie is not restricted to encrypted HTTPS connections.",
        "The browser may send the cookie over plain HTTP where a network attacker can capture it.",
        "Add the Secure attribute to the cookie.",
        "Enforce HTTPS site-wide and enable HSTS so cookies are never sent in clear text.",
    ),
    "cookie_missing_samesite": (
        "The cookie has no SameSite rule telling the browser when to send it on cross-site requests.",
        "Cross-site requests may attach the cookie, which is a common ingredient in CSRF attacks.",
        "Set SameSite=Lax or SameSite=Strict for session cookies.",
        "Combine SameSite with anti-CSRF tokens for state-changing requests.",
    ),
    "server_header": (
        "The Server header reveals web server software details.",
        "Version details make it easier for an attacker to look for matching known vulnerabilities.",
        "Remove or genericise the Server header.",
        "Keep server software patched and minimise version banners in responses.",
    ),
    "powered_by_header": (
        "The X-Powered-By header reveals the application framework.",
        "Knowing the framework helps an attacker target framework-specific vulnerabilities.",
        "Disable the framework's version header in production.",
        "Keep dependencies updated and avoid publishing build or framework versions.",
    ),
    "directory_listing": (
        "A directory shows a browsable list of its files instead of a normal page.",
        "Files that were never meant to be public, such as backups or configuration, can be discovered and downloaded.",
        "Disable directory indexes in the web server configuration.",
        "Add index files, deny listing rules and store sensitive files outside the web root.",
    ),
    "potential_reflected_xss": (
        "A harmless test value appeared inside executable browser context. This is an indicator, not a confirmed exploit.",
        "If the application fails to encode this input, script supplied by an attacker could run in another user's browser.",
        "Encode output for the exact context where it appears and avoid innerHTML for user-controlled data.",
        "Use framework auto-escaping, safe DOM APIs and a strict Content-Security-Policy.",
    ),
    "input_reflected": (
        "The harmless test value appeared in the page as ordinary text.",
        "Plain reflection is safe by itself, but it is worth checking that encoding stays correct in every context.",
        "Keep using context-aware output encoding when rendering user-controlled values.",
        "Add tests that place special characters in parameters and verify they are displayed as text.",
    ),
    "potential_sqli_error": (
        "Database error details were visible in a normal response. No injection payload was sent by this scan.",
        "Error text can reveal query structure and encourage further probing by an attacker.",
        "Use parameterised queries for all database access and return generic error pages in production.",
        "Log detailed errors server-side, use least-privilege database accounts and validate input types.",
    ),
    "debug_token_header": (
        "A debugging token is exposed in a production response header.",
        "Debug endpoints can expose stack traces or internal state to unauthorised users.",
        "Disable debug headers and endpoints in production.",
        "Separate development diagnostics from production configuration.",
    ),
}


CATEGORY_FALLBACK = {
    "Security Headers": (
        "A security header is missing or weaker than recommended.",
        "The browser loses one of the protections it relies on to defend users.",
        "Add the recommended header value to every response.",
        "Review the site with a security-header checklist after each deployment.",
    ),
    "Transport Security": (
        "The encrypted connection configuration can be improved.",
        "Weak transport protection exposes data to interception.",
        "Use HTTPS with a valid certificate, modern TLS and HSTS.",
        "Monitor certificate validity and protocol settings continuously.",
    ),
    "Cookie Security": (
        "A session-related cookie is missing a recommended protection flag.",
        "Session cookies without protections are easier to steal or misuse.",
        "Set HttpOnly, Secure and SameSite on sensitive cookies.",
        "Review cookie attributes whenever authentication code changes.",
    ),
    "Information Disclosure": (
        "The application reveals technical details about its implementation.",
        "Version and stack details help attackers choose known exploits.",
        "Remove or genericise the disclosed value.",
        "Keep components patched and limit diagnostic output in production.",
    ),
    "Cross-Site Scripting (Potential)": (
        "An observation may allow script to be injected, but it needs manual review.",
        "Confirmed XSS can steal sessions or act on behalf of users.",
        "Apply context-aware encoding and a strict Content-Security-Policy.",
        "Use safe rendering APIs and review any use of innerHTML.",
    ),
    "SQL Injection (Potential)": (
        "An observation suggests database errors may be exposed.",
        "Injection flaws can read or modify data without authorisation.",
        "Use parameterised queries and generic error messages.",
        "Apply least privilege to database accounts and validate input types.",
    ),
}


def explanation_for(key, category):
    return KNOWLEDGE.get(key) or CATEGORY_FALLBACK.get(
        category,
        (
            "This configuration weakens the security posture of the application.",
            "An attacker may be able to use the weakness as part of a larger attack.",
            "Apply the recommendation shown for this finding.",
            "Include this check in the development and deployment checklist.",
        ),
    )
