import re

with open('tip-animated05.html', 'r') as f:
    text = f.read()

# 1. Base Layer Opacity
text = text.replace('rgba(255,255,255,0.015)', 'rgba(255,255,255,0.3)')
text = text.replace('rgba(217,32,32,0.02)', 'rgba(217,32,32,0.4)')
text = text.replace('stroke: rgba(255,255,255,0.06)', 'stroke: rgba(255,255,255,0.15)')

# 2. Body font size
text = text.replace('font-size: 18px;', 'font-size: 20px;')
# Make subtexts readable too
text = text.replace('fill="rgba(255,255,255,0.015)"', 'fill="rgba(255,255,255,0.3)"')

# 3. Eyebrow font size
text = text.replace('font-size: 11px; letter-spacing: 0.2rem;', 'font-size: 16px; letter-spacing: 0.15em;')

# 4. Tab Active font color & Tab size
text = text.replace('.tab-btn.active { background: rgba(255,255,255,0.08); color: var(--accent); box-shadow: inset 0 3px 0 var(--accent); }', '.tab-btn.active { background: rgba(255,255,255,0.08); color: #fff; box-shadow: inset 0 3px 0 var(--accent); }')
text = text.replace('font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--dim); border: none; cursor: pointer; transition: all 0.3s; text-align: left;', 'font-size: 13px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--dim); border: none; cursor: pointer; transition: all 0.3s; text-align: left;')

# 5. Cycle Step Hover
text = text.replace('.cycle-step { background: rgba(10,10,10,0.8); padding: 3rem; position: relative; }', '.cycle-step { background: rgba(10,10,10,0.8); padding: 3rem; position: relative; transition: all 0.3s ease; outline: 1px solid transparent; }\n    .cycle-step:hover { background: rgba(30,30,30,0.95); transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.6); outline-color: rgba(255,255,255,0.15); z-index: 10; }')

# 6. About image
old_about = """<div class="abt-inner">
        <div>
          <h2 class="sec-title" style="font-size:3.5rem;">Roti Akinsanmi</h2>"""
new_about = """<div class="abt-inner">
        <div>
          <div style="width: 250px; height: 250px; border-radius: 50%; padding: 2px; background: linear-gradient(45deg, var(--accent), transparent, rgba(255,255,255,0.1)); margin-bottom: 3rem; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;">
            <div style="width: 100%; height: 100%; border-radius: 50%; background: #0a0a0a; display: flex; align-items: center; justify-content: center; position: absolute; z-index: 1;">
              <span style="font-family:var(--font-mono); font-size:0.7rem; color:var(--dim); letter-spacing:0.2em; text-transform:uppercase; z-index:2;">Photo Pending</span>
            </div>
            <div style="position: absolute; inset: -50%; background: radial-gradient(circle at center, rgba(217,32,32,0.6) 0%, transparent 60%); animation: breathe 8s ease-in-out infinite alternate; z-index: 2; mix-blend-mode: screen;"></div>
          </div>
          <h2 class="sec-title" style="font-size:3.5rem;">Roti Akinsanmi</h2>"""
text = text.replace(old_about, new_about)

# 7. Award Star placeholder
old_star = """<div class="award-star">★</div>"""
new_star = """<div style="width: 80px; height: 80px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0;"><span style="font-family:var(--font-mono); font-size:9px; letter-spacing:0.1em; color:var(--dim); text-transform:uppercase; text-align:center;">Award<br>Photo</span></div>"""
text = text.replace(old_star, new_star)

# 8. Contact Form
old_cta = """<div class="container">
      <h2 class="cta-title">Ready to act differently on "Monday"?</h2>
      <a href="mailto:info@theoryinpractice.ca" class="btn-sub" data-cursor-hover>Initiate Contact</a>
    </div>"""
new_cta = """<div class="container">
      <h2 class="cta-title">Ready to act differently on "Monday"?</h2>
      <form id="contactForm" style="max-width: 700px; margin: 3rem auto 0; display: flex; flex-direction: column; gap: 1rem; text-align: left;">
        <div style="display: flex; gap: 1rem;" class="f-row">
          <input type="text" placeholder="Name" required style="flex: 1; padding: 1.25rem; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); color: #fff; font-family: var(--font-sans); font-size: 1rem; border-radius: 2px;" onfocus="this.style.borderColor='#d92020'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'"/>
          <input type="email" placeholder="Email Address" required style="flex: 1; padding: 1.25rem; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); color: #fff; font-family: var(--font-sans); font-size: 1rem; border-radius: 2px;" onfocus="this.style.borderColor='#d92020'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'"/>
        </div>
        <textarea placeholder="How can we help?" rows="4" required style="width: 100%; padding: 1.25rem; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); color: #fff; font-family: var(--font-sans); font-size: 1rem; border-radius: 2px;" onfocus="this.style.borderColor='#d92020'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'"></textarea>
        <button type="submit" class="btn-sub" style="width: 100%; border: none; cursor: pointer;">Initiate Contact</button>
      </form>
      <div id="formSuccess" style="max-width: 700px; margin: 3rem auto 0; padding: 4rem; background: rgba(255,255,255,0.05); text-align: center; border-radius: 2px; display: none; border: 1px solid rgba(255,255,255,0.1);">
        <h3 style="font-family:var(--font-serif); font-size:2.5rem; color:#fff; margin-bottom:0.5rem;">Message Sent Successfully</h3>
        <p style="color:var(--dim); font-size:1.1rem;">We will be in touch shortly to continue the conversation.</p>
      </div>
    </div>"""
text = text.replace(old_cta, new_cta)

script_add = """// CONTACT FORM AJAX SIMULATION
    const contactForm = document.getElementById('contactForm');
    if(contactForm) {
      contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        this.style.display = 'none';
        document.getElementById('formSuccess').style.display = 'block';
      });
    }"""
text = text.replace('  </script>', script_add + '\n  </script>')

keyf = """@keyframes blink { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }"""
new_keyf = keyf + "\\n    @keyframes breathe { 0% { transform: scale(0.9) translate(-5%, -5%); opacity: 0.5; } 100% { transform: scale(1.1) translate(5%, 5%); opacity: 1; } }"
text = text.replace(keyf, new_keyf)

hq = """@media (max-width: 1000px) {"""
new_hq = """@media (max-width: 768px) {
      .hero { padding: 8rem 0 3rem 0 !important; }
      .venn-svg { width: 160%; max-width: none; transform: translateX(-15%); }
      .f-row { flex-direction: column; }
      .text-title { font-size: 60px; }
      .text-title.in { font-size: 50px; }
      .tab-btn { flex: 1 1 100%; border-bottom: 1px solid var(--rule); }
    }
    """ + hq
text = text.replace(hq, new_hq)

with open('tip-animated07.html', 'w') as f:
    f.write(text)
