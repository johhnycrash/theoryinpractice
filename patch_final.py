import re
import json

# Start from tip-animated12.html which had our V13 logic (polygons, grid, shadow wipe)
with open('tip-animated12.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. FIX THE "GIANT WHITE CIRCLE" BUG
# The issue was loc-logo styling clashing wildly with GSAP scaling leading to insane borders.
# We'll completely simplify the loc-logo and eliminate any background or border-radius on it natively.
# We'll also add pointer-events: none; strictly.
new_loc_logo_css = """
        .loc-logo {
            position: absolute;
            top: 50%;
            left: 50%;
            opacity: 0;
            pointer-events: none;
            z-index: 20;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .loc-logo-txt {
            color: #fff;
            font-family: var(--font-sans);
            font-size: 14px;
            font-weight: 500;
            background: rgba(10,10,10,0.9);
            padding: 8px 16px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 4px;
            white-space: nowrap;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            pointer-events: none;
        }
"""
text = re.sub(r'\.loc-logo\s*\{[^}]*\}', '', text)
text = re.sub(r'\.loc-logo img\s*\{[^}]*\}', '', text)
text = re.sub(r'\.loc-logo-txt\s*\{[^}]*\}', '', text)
text = re.sub(r'\.loc-logo\s*\{.*?\}', '', text, flags=re.DOTALL) # double check

insertion_idx = text.find('.map-pin.active .loc-logo')
if insertion_idx != -1:
    text = text[:insertion_idx] + new_loc_logo_css + text[insertion_idx:]


# 2. VERTICALLY CENTER THE CITY PANEL
# Update loc-list CSS
css_loc_list_pattern = r'\.loc-list\s*\{[^}]*\}'
css_loc_list_new = """\.loc-list {
            position: absolute;
            top: 50%;
            left: 5vw;
            transform: translateY(-50%);
            width: 600px;
            background: transparent;
            z-index: 5;
            display: flex;
            flex-direction: column;
            justify-content: center;
            pointer-events: none;
        }"""
text = re.sub(css_loc_list_pattern, css_loc_list_new, text)

# Update city-item css to block pointer events to only its text, stopping city jitter loop
css_city_item = r'\.city-item\s*\{[^}]*\}'
new_city_item = """.city-item {
            list-style: none;
            padding: 1.5rem;
            background: rgba(10, 10, 10, 0.4);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            cursor: pointer;
            transition: all 0.3s;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
            pointer-events: auto;
        }"""
text = re.sub(css_city_item, new_city_item, text)

# Prevent the list glitch
text = text.replace('padding-left: 1rem;', '')
text = text.replace('transform: translateX(-5px);', 'border-color: var(--accent); background: rgba(217, 32, 32, 0.1);')

# The logos loop inside Javascript rendering
# Force logos to use strictly loc-logo-txt and ditch the giant broken images if exist
old_li_render = r"li\.innerHTML = `.*?`;"
new_li_render = """
                    li.innerHTML = `
                        <svg class="city-bg-geom" viewBox="0 0 100 100" style="position: absolute; right: -15px; bottom: -15px; width: 80px; height: 80px; opacity: 0.05; pointer-events: none; transform: rotate(-10deg);">
                            <polygon points="${dat.geom || '0,0 100,0 100,100 0,100'}" fill="rgba(255,255,255,1)" />
                        </svg>
                        <span class="city-name" style="position:relative; z-index:2; pointer-events:none;">${dat.name}</span>
                        <span class="city-logos" style="position:relative; z-index:2; pointer-events:none;">${c_names}</span>
                    `;"""
text = re.sub(old_li_render, new_li_render, text, flags=re.DOTALL)

# Ensure the JS injects loc-logo-txt reliably
js_logos_inject = r"let logosHtml = '';.*?addBtnHtml"
js_new_logos = """let logosHtml = '';
                    dat.logos.forEach((logoObj) => {
                        const lname = typeof logoObj === 'string' ? logoObj : logoObj.name;
                        logosHtml += `<div class="loc-logo"><div class="loc-logo-txt">${lname}</div></div>`;
                    });
                    
                    let addBtnHtml"""
text = re.sub(js_logos_inject, js_new_logos, text, flags=re.DOTALL)

# 3. REWRITE THE SEQUENCING PULSE PROPERLY
# The previous python script injected the logic, let's make sure it's perfect.
new_seq = """// SEQUENTIAL HEARTBEAT PULSE
            let pulseSeq = mapData.map((_, i) => i);
            for (let i = pulseSeq.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [pulseSeq[i], pulseSeq[j]] = [pulseSeq[j], pulseSeq[i]];
            }
            let pulseIdx = 0;
            setInterval(() => {
                if(pulseIdx >= pulseSeq.length) {
                    for (let i = pulseSeq.length - 1; i > 0; i--) {
                        const j = Math.floor(Math.random() * (i + 1));
                        [pulseSeq[i], pulseSeq[j]] = [pulseSeq[j], pulseSeq[i]];
                    }
                    pulseIdx = 0;
                }
                const target = mapData[pulseSeq[pulseIdx]];
                pulseIdx++;
                
                const pin = document.getElementById(target.id);
                if(pin && !pin.classList.contains('active')) {
                    pin.classList.add('auto-pulse');
                    setTimeout(() => {
                        if(pin) pin.classList.remove('auto-pulse');
                    }, 2500); 
                }
            }, 3500);"""
text = re.sub(r'// SEQUENTIAL HEARTBEAT PULSE.*?3500\);', new_seq, text, flags=re.DOTALL)

with open('tip-animated13.html', 'w', encoding='utf-8') as f:
    f.write(text)
