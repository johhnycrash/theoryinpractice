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

    // Send via Resend
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
        subject: `New inquiry from ${safeName}`,
        html: [
          '<div style="font-family:sans-serif;max-width:600px;">',
          `<h2 style="color:#d92020;">New Contact Form Submission</h2>`,
          `<p><strong>Name:</strong> ${safeName}</p>`,
          `<p><strong>Email:</strong> <a href="mailto:${safeEmail}">${safeEmail}</a></p>`,
          `<hr style="border:none;border-top:1px solid #eee;margin:20px 0;">`,
          `<p><strong>Message:</strong></p>`,
          `<p style="white-space:pre-wrap;">${safeMessage}</p>`,
          `<hr style="border:none;border-top:1px solid #eee;margin:20px 0;">`,
          `<p style="color:#999;font-size:12px;">Sent via theoryinpractice.ca contact form</p>`,
          '</div>',
        ].join(''),
      }),
    });

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
