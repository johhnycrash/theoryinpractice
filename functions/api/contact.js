export async function onRequestPost(context) {
  const { request, env } = context;

  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  };

  try {
    const body = await request.json();
    const { name, email, message, token } = body;

    if (!name || !email || !message) {
      return new Response(JSON.stringify({ error: 'Missing required fields' }), { status: 400, headers });
    }

    // Verify Turnstile token
    if (env.TURNSTILE_SECRET_KEY && token) {
      const verify = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          secret: env.TURNSTILE_SECRET_KEY,
          response: token,
        }),
      });
      const result = await verify.json();
      if (!result.success) {
        return new Response(JSON.stringify({ error: 'Bot check failed' }), { status: 403, headers });
      }
    }

    // Sanitize
    const clean = (s) => String(s).replace(/</g, '&lt;').replace(/>/g, '&gt;').trim();
    const safeName = clean(name).substring(0, 80);
    const safeEmail = clean(email).substring(0, 120);
    const safeMessage = clean(message).substring(0, 4000);

    // Build email HTML — dark-themed, site-branded
    const now = new Date();
    const stamp = now.toLocaleString('en-CA', {
      dateStyle: 'medium',
      timeStyle: 'short',
      timeZone: 'America/Edmonton',
    });

    const adminHtml = buildAdminEmail({ safeName, safeEmail, safeMessage, stamp });
    const replyHtml = buildReplyEmail({ safeName });

    // Send admin notification via Resend
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Theory in Practice <team@theoryinpractice.ca>',
        to: ['dev@theoryinpractice.ca'],
        reply_to: safeEmail,
        subject: `New inquiry — ${safeName}`,
        html: adminHtml,
      }),
    });

    // Fire-and-forget auto-reply to the submitter (don't block on failure)
    if (res.ok) {
      fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: 'Theory in Practice <team@theoryinpractice.ca>',
          to: [safeEmail],
          subject: 'We received your message — Theory in Practice',
          html: replyHtml,
        }),
      }).catch(() => {});
    }

    if (res.ok) {
      return new Response(JSON.stringify({ success: true }), { status: 200, headers });
    } else {
      const err = await res.text();
      console.error('Resend error:', err);
      return new Response(JSON.stringify({ error: 'Email delivery failed' }), { status: 502, headers });
    }
  } catch (e) {
    console.error('Contact function error:', e);
    return new Response(JSON.stringify({ error: 'Server error' }), { status: 500, headers });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

// ---------------------------------------------------------------------------
// Email templates — dark-themed, brand-matched to theoryinpractice.ca
// ---------------------------------------------------------------------------

const SERIF = "'Cormorant Garamond', Georgia, 'Times New Roman', serif";
const SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif";
const MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace";
const ACCENT = '#d92020';
const BG = '#030303';
const CARD = '#0a0a0a';
const RULE = 'rgba(255,255,255,0.1)';
const DIM = '#7a7a7a';

function logoMark() {
  return `
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;">
      <tr>
        <td style="font-family:${SERIF};font-size:26px;line-height:1;color:#ffffff;padding:0;">
          Theory <span style="color:${ACCENT};font-style:italic;">in Practice</span>
        </td>
      </tr>
    </table>
  `;
}

function emailShell(innerHtml, preheader) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="supported-color-schemes" content="dark">
<title>Theory in Practice</title>
</head>
<body style="margin:0;padding:0;background:${BG};color:#ffffff;font-family:${SANS};">
  <span style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;">${preheader}</span>
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:${BG};">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px;width:100%;background:${CARD};border:1px solid ${RULE};border-radius:6px;overflow:hidden;">
          <tr>
            <td style="padding:28px 32px;border-bottom:1px solid ${RULE};">
              ${logoMark()}
            </td>
          </tr>
          <tr>
            <td style="padding:36px 32px;">
              ${innerHtml}
            </td>
          </tr>
          <tr>
            <td style="padding:20px 32px;border-top:1px solid ${RULE};background:rgba(0,0,0,0.4);">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="font-family:${MONO};font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:${DIM};">
                    Calgary · Alberta
                  </td>
                  <td align="right" style="font-family:${MONO};font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:${DIM};">
                    <a href="https://theoryinpractice.ca" style="color:${DIM};text-decoration:none;">theoryinpractice.ca</a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
        <div style="font-family:${MONO};font-size:10px;color:#444;margin-top:18px;letter-spacing:0.08em;">
          © ${new Date().getFullYear()} Theory in Practice Inc.
        </div>
      </td>
    </tr>
  </table>
</body>
</html>`;
}

function buildAdminEmail({ safeName, safeEmail, safeMessage, stamp }) {
  const messageHtml = safeMessage.replace(/\n/g, '<br>');
  const inner = `
    <div style="font-family:${MONO};font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:${ACCENT};margin-bottom:12px;">
      New Inquiry
    </div>
    <h1 style="font-family:${SERIF};font-size:34px;line-height:1.1;font-weight:400;color:#ffffff;margin:0 0 8px 0;letter-spacing:-0.01em;">
      ${safeName}
    </h1>
    <div style="font-family:${MONO};font-size:12px;color:${DIM};margin-bottom:28px;">
      ${stamp}
    </div>

    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-top:1px solid ${RULE};border-bottom:1px solid ${RULE};margin-bottom:28px;">
      <tr>
        <td style="padding:18px 0;width:90px;font-family:${MONO};font-size:11px;letter-spacing:0.15em;text-transform:uppercase;color:${DIM};vertical-align:top;">
          From
        </td>
        <td style="padding:18px 0;font-family:${SANS};font-size:15px;color:#ffffff;vertical-align:top;">
          ${safeName}
        </td>
      </tr>
      <tr>
        <td style="padding:0 0 18px 0;font-family:${MONO};font-size:11px;letter-spacing:0.15em;text-transform:uppercase;color:${DIM};vertical-align:top;">
          Reply to
        </td>
        <td style="padding:0 0 18px 0;font-family:${SANS};font-size:15px;vertical-align:top;">
          <a href="mailto:${safeEmail}" style="color:${ACCENT};text-decoration:none;">${safeEmail}</a>
        </td>
      </tr>
    </table>

    <div style="font-family:${MONO};font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:${ACCENT};margin-bottom:14px;">
      Message
    </div>
    <div style="font-family:${SERIF};font-size:18px;line-height:1.55;color:#ffffff;font-style:italic;padding:22px 24px;background:rgba(255,255,255,0.03);border-left:2px solid ${ACCENT};">
      ${messageHtml}
    </div>

    <div style="margin-top:32px;">
      <a href="mailto:${safeEmail}?subject=Re:%20Your%20inquiry%20to%20Theory%20in%20Practice"
         style="display:inline-block;padding:14px 28px;font-family:${MONO};font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#ffffff;background:${ACCENT};text-decoration:none;border-radius:100px;">
        Reply to ${safeName.split(' ')[0] || safeName}
      </a>
    </div>
  `;
  return emailShell(inner, `New inquiry from ${safeName} — ${safeEmail}`);
}

function buildReplyEmail({ safeName }) {
  const firstName = safeName.split(' ')[0] || safeName;
  const inner = `
    <div style="font-family:${MONO};font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:${ACCENT};margin-bottom:12px;">
      Message Received
    </div>
    <h1 style="font-family:${SERIF};font-size:38px;line-height:1.1;font-weight:400;color:#ffffff;margin:0 0 20px 0;letter-spacing:-0.01em;">
      Thank you, ${firstName}.
    </h1>

    <p style="font-family:${SERIF};font-size:19px;line-height:1.6;color:rgba(255,255,255,0.85);margin:0 0 18px 0;font-style:italic;">
      Your message is in. Roti will read it personally and reply within a couple of working days.
    </p>

    <p style="font-family:${SANS};font-size:14px;line-height:1.7;color:${DIM};margin:0 0 28px 0;">
      In the meantime, feel free to revisit the site — the Academy calendar and consulting cycles are live. If anything is time-sensitive, just reply to this email and flag it.
    </p>

    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-top:1px solid ${RULE};margin-top:10px;">
      <tr>
        <td style="padding:22px 0 0 0;">
          <div style="font-family:${MONO};font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:${DIM};margin-bottom:6px;">
            — Roti Akinsanmi
          </div>
          <div style="font-family:${MONO};font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:${DIM};">
            Founder · Theory in Practice
          </div>
        </td>
      </tr>
    </table>

    <div style="margin-top:32px;">
      <a href="https://theoryinpractice.ca"
         style="display:inline-block;padding:14px 28px;font-family:${MONO};font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#ffffff;background:transparent;text-decoration:none;border:1px solid rgba(255,255,255,0.25);border-radius:100px;">
        Visit theoryinpractice.ca
      </a>
    </div>
  `;
  return emailShell(inner, `We got your message, ${firstName}. Roti will be in touch shortly.`);
}
