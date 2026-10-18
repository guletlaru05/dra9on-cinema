export const SECURITY_HEADERS=Object.freeze({
 'Strict-Transport-Security':'max-age=15552000',
 'Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
 'X-Frame-Options':'DENY',
 'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
 'X-Content-Type-Options':'nosniff',
 'Referrer-Policy':'no-referrer',
});
