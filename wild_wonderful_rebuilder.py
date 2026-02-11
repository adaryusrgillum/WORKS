"""
WILD & WONDERFUL WEBSITES - Rebuilder
Stripped down, black & white, maximum impact
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# BRAND: WILD & WONDERFUL WEBSITES
# COLORS: Black & White ONLY
# PHILOSOPHY: Strip everything unnecessary

WILD_CSS = """
/* WILD & WONDERFUL WEBSITES - Black & White Design System */
/* Zero bloat. Maximum impact. */

:root {
    --black: #000000;
    --white: #ffffff;
    --gray-100: #f5f5f5;
    --gray-200: #e5e5e5;
    --gray-800: #262626;
    --gray-900: #171717;
    
    --font-display: 'Bebas Neue', Impact, sans-serif;
    --font-body: 'Inter', system-ui, sans-serif;
}

/* RESET - Aggressive */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:16px;-webkit-font-smoothing:antialiased}
body{font-family:var(--font-body);background:var(--white);color:var(--black);line-height:1.6;overflow-x:hidden}
img{max-width:100%;display:block;height:auto}
a{color:inherit;text-decoration:none}
button{font-family:inherit;border:none;background:none;cursor:pointer}

/* TYPOGRAPHY - Bold */
h1,h2,h3,h4{font-family:var(--font-display);text-transform:uppercase;letter-spacing:0.02em;line-height:0.95}
h1{font-size:clamp(4rem,12vw,10rem);font-weight:900}
h2{font-size:clamp(2.5rem,6vw,5rem)}
h3{font-size:clamp(1.5rem,3vw,2.5rem)}
p{font-size:clamp(1rem,1.5vw,1.25rem);max-width:65ch}

/* LAYOUT - Brutalist */
.container{width:100%;max-width:1400px;margin:0 auto;padding:0 4vw}
.grid{display:grid;gap:0}
.grid-2{grid-template-columns:repeat(2,1fr)}
.grid-3{grid-template-columns:repeat(3,1fr)}
.flex{display:flex;align-items:center}
.flex-between{justify-content:space-between}

/* HEADER - Fixed, bold */
.header{position:fixed;top:0;left:0;right:0;z-index:100;background:var(--white);border-bottom:2px solid var(--black)}
.header-inner{height:70px;display:flex;align-items:center;justify-content:space-between}
.logo{font-family:var(--font-display);font-size:1.75rem;font-weight:900;letter-spacing:0.05em}
.logo span{color:var(--white);background:var(--black);padding:0.25rem 0.5rem}
.nav{display:flex;gap:3rem;font-weight:600;font-size:0.875rem;text-transform:uppercase;letter-spacing:0.05em}
.nav a{position:relative}
.nav a::after{content:'';position:absolute;bottom:-4px;left:0;width:0;height:2px;background:var(--black);transition:width 0.3s}
.nav a:hover::after{width:100%}
.menu-btn{display:none;font-size:1.5rem}

/* HERO - Full viewport */
.hero{min-height:100vh;display:flex;align-items:center;position:relative;background:var(--white)}
.hero-alt{background:var(--black);color:var(--white)}
.hero-content{position:relative;z-index:2}
.hero-label{font-family:var(--font-display);font-size:1rem;letter-spacing:0.2em;margin-bottom:2rem;text-transform:uppercase}
.hero h1{margin-bottom:2rem}
.hero p{font-size:1.25rem;margin-bottom:3rem;max-width:50ch}

/* BUTTONS - Sharp */
.btn{display:inline-flex;align-items:center;gap:1rem;padding:1rem 2.5rem;background:var(--black);color:var(--white);font-weight:700;text-transform:uppercase;letter-spacing:0.05em;font-size:0.875rem;transition:all 0.2s;border:2px solid var(--black)}
.btn:hover{background:var(--white);color:var(--black)}
.btn-white{background:var(--white);color:var(--black);border-color:var(--white)}
.btn-white:hover{background:var(--black);color:var(--white);border-color:var(--black)}
.btn-outline{background:transparent;color:var(--black)}
.btn-outline:hover{background:var(--black);color:var(--white)}

/* SECTIONS - High contrast */
.section{padding:8rem 0}
.section-black{background:var(--black);color:var(--white)}
.section-gray{background:var(--gray-100)}
.section-header{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:4rem;border-bottom:2px solid currentColor;padding-bottom:2rem}

/* CARDS - Minimal */
.card{border:2px solid var(--black);padding:2rem;transition:transform 0.2s,box-shadow 0.2s;background:var(--white)}
.card:hover{transform:translate(-4px,-4px);box-shadow:8px 8px 0 var(--black)}
.card-black{background:var(--black);color:var(--white);border-color:var(--white)}
.card-black:hover{box-shadow:8px 8px 0 var(--white)}
.card h3{margin-bottom:1rem}

/* IMAGES - Hard edges */
.img-frame{border:2px solid var(--black);overflow:hidden}
.img-frame img{transition:transform 0.5s}
.img-frame:hover img{transform:scale(1.05)}

/* VIDEO - Full bleed */
.video-bg{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;filter:grayscale(100%) contrast(1.2)}
.video-overlay{position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5)}

/* STATS - Big numbers */
.stat-number{font-family:var(--font-display);font-size:clamp(4rem,10vw,8rem);line-height:1}
.stat-label{font-size:0.875rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:0.5rem}

/* FOOTER - Heavy */
.footer{background:var(--black);color:var(--white);padding:4rem 0 2rem}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:4rem;margin-bottom:4rem}
.footer h4{font-family:var(--font-display);font-size:1.25rem;margin-bottom:1.5rem}
.footer a{color:var(--gray-200);display:block;margin-bottom:0.75rem;font-size:0.875rem;transition:color 0.2s}
.footer a:hover{color:var(--white)}
.footer-bottom{display:flex;justify-content:space-between;padding-top:2rem;border-top:1px solid var(--gray-800);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em}

/* MARQUEE */
.marquee{overflow:hidden;white-space:nowrap;border-top:2px solid var(--black);border-bottom:2px solid var(--black);padding:1rem 0;background:var(--black);color:var(--white)}
.marquee-content{display:inline-block;animation:marquee 20s linear infinite;font-family:var(--font-display);font-size:1.5rem;text-transform:uppercase;letter-spacing:0.1em}
@keyframes marquee{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}

/* GLITCH EFFECT */
.glitch{position:relative}
.glitch::before,.glitch::after{content:attr(data-text);position:absolute;top:0;left:0;width:100%;height:100%}
.glitch::before{left:2px;text-shadow:-2px 0 red;clip:rect(24px,550px,90px,0);animation:glitch-anim-2 3s infinite linear alternate-reverse}
.glitch::after{left:-2px;text-shadow:-2px 0 blue;clip:rect(85px,550px,140px,0);animation:glitch-anim 2.5s infinite linear alternate-reverse}
@keyframes glitch-anim{0%{clip:rect(10px,9999px,85px,0)}20%{clip:rect(63px,9999px,130px,0)}40%{clip:rect(25px,9999px,145px,0)}60%{clip:rect(89px,9999px,55px,0)}80%{clip:rect(45px,9999px,99px,0)}100%{clip:rect(12px,9999px,120px,0)}}
@keyframes glitch-anim-2{0%{clip:rect(65px,9999px,99px,0)}20%{clip:rect(15px,9999px,45px,0)}40%{clip:rect(85px,9999px,120px,0)}60%{clip:rect(35px,9999px,75px,0)}80%{clip:rect(95px,9999px,140px,0)}100%{clip:rect(5px,9999px,60px,0)}}

/* SCROLLBAR - Minimal */
::-webkit-scrollbar{width:8px}
::-webkit-scrollbar-track{background:var(--gray-100)}
::-webkit-scrollbar-thumb{background:var(--black)}

/* MOBILE */
@media(max-width:768px){
.nav{display:none;position:absolute;top:70px;left:0;right:0;background:var(--white);flex-direction:column;padding:2rem;border-bottom:2px solid var(--black)}
.nav.active{display:flex}
.menu-btn{display:block}
.grid-2,.grid-3{grid-template-columns:1fr}
.footer-grid{grid-template-columns:1fr;gap:2rem}
.section{padding:4rem 0}
}

/* PRINT */
@media print{*{background:transparent!important;color:black!important;box-shadow:none!important}}

/* SELECTION */
::selection{background:var(--black);color:var(--white)}
"""


def generate_wild_template(project: dict) -> str:
    """Generate WILD & WONDERFUL website"""
    
    name = project['name']
    ptype = project['type']
    
    # Different layouts for different types
    if ptype == "Portfolio":
        content = generate_portfolio_wild(project)
    elif ptype == "Advocacy":
        content = generate_advocacy_wild(project)
    elif ptype == "Tattoo":
        content = generate_tattoo_wild(project)
    elif ptype == "Training":
        content = generate_training_wild(project)
    elif ptype == "Marketing":
        content = generate_marketing_wild(project)
    else:
        content = generate_default_wild(project)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project['title']}</title>
    <meta name="description" content="{project['description']}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>{WILD_CSS}</style>
</head>
<body>
    {content}
</body>
</html>"""


def generate_portfolio_wild(p: dict) -> str:
    return f'''
    <header class="header">
        <div class="container header-inner">
            <a href="/" class="logo">WILD<span>&</span>WONDERFUL</a>
            <nav class="nav" id="nav">
                <a href="/work">Work</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
            <button class="menu-btn" onclick="document.getElementById('nav').classList.toggle('active')">☰</button>
        </div>
    </header>
    
    <section class="hero" style="padding-top:70px">
        <div class="container">
            <div class="hero-content">
                <p class="hero-label">Web Design & Development</p>
                <h1 class="glitch" data-text="DIGITAL">DIGITAL</h1>
                <h1 style="margin-left:10vw">EXCELLENCE</h1>
                <p style="margin-top:3rem;max-width:40ch">Award-winning portfolio showcasing brutalist designs with cutting-edge technology. Based in West Virginia.</p>
                <a href="/work" class="btn" style="margin-top:3rem">View Selected Work →</a>
            </div>
        </div>
    </section>
    
    <div class="marquee">
        <div class="marquee-content">
            REACT • THREE.JS • WEBGL • NODE • TYPESCRIPT • REACT • THREE.JS • WEBGL • NODE • TYPESCRIPT •
        </div>
    </div>
    
    <section class="section">
        <div class="container">
            <div class="section-header">
                <h2>Selected Work</h2>
                <a href="/work" class="btn btn-outline">View All</a>
            </div>
            <div class="grid grid-2">
                <div class="card">
                    <div class="img-frame" style="margin-bottom:1.5rem">
                        <div style="aspect-ratio:16/9;background:linear-gradient(135deg,#000 0%,#333 100%)"></div>
                    </div>
                    <h3>NCRJ WATCH</h3>
                    <p>Advocacy platform design</p>
                </div>
                <div class="card">
                    <div class="img-frame" style="margin-bottom:1.5rem">
                        <div style="aspect-ratio:16/9;background:linear-gradient(135deg,#333 0%,#666 100%)"></div>
                    </div>
                    <h3>DARK ROSE TATTOO</h3>
                    <p>Brand identity & website</p>
                </div>
                <div class="card">
                    <div class="img-frame" style="margin-bottom:1.5rem">
                        <div style="aspect-ratio:16/9;background:linear-gradient(135deg,#666 0%,#999 100%)"></div>
                    </div>
                    <h3>MDI TRAINING</h3>
                    <p>Training facility platform</p>
                </div>
                <div class="card">
                    <div class="img-frame" style="margin-bottom:1.5rem">
                        <div style="aspect-ratio:16/9;background:linear-gradient(135deg,#999 0%,#ccc 100%)"></div>
                    </div>
                    <h3>ADVERTISEWV</h3>
                    <p>Marketing agency site</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="section section-black">
        <div class="container" style="text-align:center">
            <h2 style="margin-bottom:2rem">Let's Create Something</h2>
            <p style="margin:0 auto 3rem;opacity:0.8">Ready to build your digital presence? Let's talk.</p>
            <a href="/contact" class="btn btn-white">Start a Project →</a>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <h4>WILD & WONDERFUL</h4>
                    <p style="color:#999;margin-top:1rem">Web design & development studio based in West Virginia.</p>
                </div>
                <div>
                    <h4>Navigation</h4>
                    <a href="/">Home</a>
                    <a href="/work">Work</a>
                    <a href="/about">About</a>
                    <a href="/contact">Contact</a>
                </div>
                <div>
                    <h4>Social</h4>
                    <a href="#">Twitter</a>
                    <a href="#">Instagram</a>
                    <a href="#">LinkedIn</a>
                    <a href="#">GitHub</a>
                </div>
                <div>
                    <h4>Contact</h4>
                    <a href="mailto:hello@wildwonderful.com">hello@wildwonderful.com</a>
                    <p style="color:#999;margin-top:1rem;font-size:0.875rem">West Virginia, USA</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2024 WILD & WONDERFUL WEBSITES</p>
                <p>All Rights Reserved</p>
            </div>
        </div>
    </footer>
    '''


def generate_advocacy_wild(p: dict) -> str:
    return f'''
    <header class="header">
        <div class="container header-inner">
            <a href="/" class="logo">NCRJ<span>WATCH</span></a>
            <nav class="nav" id="nav">
                <a href="/crisis">Crisis</a>
                <a href="/cases">Cases</a>
                <a href="/report">Report</a>
            </nav>
            <button class="menu-btn" onclick="document.getElementById('nav').classList.toggle('active')">☰</button>
        </div>
    </header>
    
    <section class="hero hero-alt" style="padding-top:70px">
        <div class="container">
            <div class="hero-content">
                <p class="hero-label">North Central Regional Jail</p>
                <h1>DEMANDING</h1>
                <h1 style="color:transparent;-webkit-text-stroke:2px white">ACCOUNTABILITY</h1>
                <p style="margin-top:3rem;max-width:50ch;opacity:0.9">Exposing overcrowding, tracking ICE detention contracts, and honoring those lost to a system that prioritizes profit over people.</p>
                <div style="display:flex;gap:1rem;margin-top:3rem;flex-wrap:wrap">
                    <a href="/crisis" class="btn btn-white">View The Data →</a>
                    <a href="/report" class="btn btn-outline" style="border-color:white;color:white">Report a Story →</a>
                </div>
            </div>
        </div>
    </section>
    
    <section class="section">
        <div class="container">
            <div class="grid grid-4" style="text-align:center">
                <div>
                    <div class="stat-number">146%</div>
                    <div class="stat-label">Over Capacity</div>
                </div>
                <div>
                    <div class="stat-number">19+</div>
                    <div class="stat-label">Deaths Since 2020</div>
                </div>
                <div>
                    <div class="stat-number">50+</div>
                    <div class="stat-label">ICE Detainees</div>
                </div>
                <div>
                    <div class="stat-number">8</div>
                    <div class="stat-label">Federal Cases</div>
                </div>
            </div>
        </div>
    </section>
    
    <section class="section section-gray">
        <div class="container">
            <h2 style="text-align:center;margin-bottom:4rem">Take Action</h2>
            <div class="grid grid-3">
                <div class="card" style="text-align:center">
                    <div style="font-size:4rem;margin-bottom:1rem">📊</div>
                    <h3>THE CRISIS</h3>
                    <p>View live data on conditions, incidents, and statistics.</p>
                    <a href="/crisis" class="btn" style="margin-top:1.5rem;width:100%">View Data →</a>
                </div>
                <div class="card" style="text-align:center">
                    <div style="font-size:4rem;margin-bottom:1rem">⚖️</div>
                    <h3>FEDERAL CASES</h3>
                    <p>Explore ongoing litigation and legal documentation.</p>
                    <a href="/cases" class="btn" style="margin-top:1.5rem;width:100%">View Cases →</a>
                </div>
                <div class="card" style="text-align:center">
                    <div style="font-size:4rem;margin-bottom:1rem">📝</div>
                    <h3>REPORT STORY</h3>
                    <p>Share information about conditions anonymously.</p>
                    <a href="/report" class="btn" style="margin-top:1.5rem;width:100%">Report →</a>
                </div>
            </div>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <h4>NCRJ WATCH</h4>
                    <p style="color:#999;margin-top:1rem">Demanding accountability. Exposing inhumanity.</p>
                </div>
                <div>
                    <h4>Navigation</h4>
                    <a href="/">Home</a>
                    <a href="/crisis">The Crisis</a>
                    <a href="/cases">Federal Cases</a>
                    <a href="/report">Report</a>
                </div>
                <div>
                    <h4>Resources</h4>
                    <a href="#">ACLU WV</a>
                    <a href="#">WV Division of Corrections</a>
                    <a href="#">Federal Court Records</a>
                </div>
                <div>
                    <h4>Contact</h4>
                    <a href="mailto:info@ncrjwatch.org">info@ncrjwatch.org</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2024 NCRJ WATCH</p>
                <p>Justice for All</p>
            </div>
        </div>
    </footer>
    '''


def generate_tattoo_wild(p: dict) -> str:
    return f'''
    <header class="header" style="background:transparent;position:absolute;border:none">
        <div class="container header-inner">
            <a href="/" class="logo" style="color:white">DARK<span style="background:white;color:black">ROSE</span></a>
            <nav class="nav" id="nav" style="color:white">
                <a href="/gallery">Gallery</a>
                <a href="/artists">Artists</a>
                <a href="/booking">Book</a>
            </nav>
            <button class="menu-btn" onclick="document.getElementById('nav').classList.toggle('active')" style="color:white">☰</button>
        </div>
    </header>
    
    <section class="hero hero-alt" style="padding:0;min-height:100vh;position:relative">
        <video class="video-bg" autoplay muted loop playsinline poster="/poster.jpg">
            <source src="firefly_gears.mp4" type="video/mp4">
        </video>
        <div class="video-overlay"></div>
        <div class="container" style="position:relative;z-index:2;height:100vh;display:flex;align-items:center">
            <div class="hero-content">
                <p class="hero-label">Premium Tattoo Studio</p>
                <h1>ART ON</h1>
                <h1 style="-webkit-text-stroke:2px white;color:transparent">SKIN</h1>
                <p style="margin-top:3rem;max-width:40ch">Custom designs. Professional piercings. Walk-ins welcome.</p>
                <a href="/booking" class="btn btn-white" style="margin-top:3rem">Book Appointment →</a>
            </div>
        </div>
    </section>
    
    <section class="section">
        <div class="container">
            <h2 style="text-align:center;margin-bottom:4rem">Our Work</h2>
            <div class="grid grid-3">
                <div class="img-frame"><div style="aspect-ratio:1;background:#111"></div></div>
                <div class="img-frame"><div style="aspect-ratio:1;background:#222"></div></div>
                <div class="img-frame"><div style="aspect-ratio:1;background:#333"></div></div>
                <div class="img-frame"><div style="aspect-ratio:1;background:#444"></div></div>
                <div class="img-frame"><div style="aspect-ratio:1;background:#555"></div></div>
                <div class="img-frame"><div style="aspect-ratio:1;background:#666"></div></div>
            </div>
        </div>
    </section>
    
    <section class="section section-black">
        <div class="container">
            <div class="grid grid-3" style="text-align:center">
                <div>
                    <div style="font-size:3rem;margin-bottom:1rem">🎨</div>
                    <h3 style="font-size:1.5rem">CUSTOM TATTOOS</h3>
                    <p style="opacity:0.7;margin-top:1rem">Unique designs tailored to your vision</p>
                </div>
                <div>
                    <div style="font-size:3rem;margin-bottom:1rem">💎</div>
                    <h3 style="font-size:1.5rem">PIERCINGS</h3>
                    <p style="opacity:0.7;margin-top:1rem">Professional body piercing services</p>
                </div>
                <div>
                    <div style="font-size:3rem;margin-bottom:1rem">✏️</div>
                    <h3 style="font-size:1.5rem">COVER UPS</h3>
                    <p style="opacity:0.7;margin-top:1rem">Transform existing tattoos</p>
                </div>
            </div>
        </div>
    </section>
    
    <footer class="footer" style="background:white;color:black">
        <div class="container">
            <div style="text-align:center;padding:4rem 0">
                <h2 style="margin-bottom:2rem">Ready for Your Next Piece?</h2>
                <a href="/booking" class="btn" style="font-size:1.25rem;padding:1.25rem 3rem">Book Now →</a>
            </div>
            <div class="footer-bottom" style="border-color:#e5e5e5;color:#666">
                <p>© 2024 DARK ROSE TATTOO</p>
                <p>West Virginia</p>
            </div>
        </div>
    </footer>
    '''


def generate_training_wild(p: dict) -> str:
    return f'''
    <header class="header">
        <div class="container header-inner">
            <a href="/" class="logo">MDI<span>TRAINING</span></a>
            <nav class="nav" id="nav">
                <a href="/courses">Courses</a>
                <a href="/schedule">Schedule</a>
                <a href="/contact">Contact</a>
            </nav>
            <button class="menu-btn" onclick="document.getElementById('nav').classList.toggle('active')">☰</button>
        </div>
    </header>
    
    <section class="hero" style="padding-top:70px">
        <div class="container">
            <div class="hero-content">
                <p class="hero-label">NRA Certified Instructors</p>
                <h1>TRAIN</h1>
                <h1 style="margin-left:15vw">DEFEND</h1>
                <h1 style="margin-left:5vw">PROTECT</h1>
                <p style="margin-top:3rem;max-width:45ch">Professional firearms training and tactical education in West Virginia. From first-time shooters to advanced tactical operations.</p>
                <a href="/courses" class="btn" style="margin-top:3rem">View Courses →</a>
            </div>
        </div>
    </section>
    
    <div class="marquee">
        <div class="marquee-content">
            NRA CERTIFIED • CONCEALED CARRY • TACTICAL TRAINING • DEFENSIVE PISTOL • NRA CERTIFIED • CONCEALED CARRY •
        </div>
    </div>
    
    <section class="section section-gray">
        <div class="container">
            <h2 style="text-align:center;margin-bottom:4rem">Training Programs</h2>
            <div class="grid grid-2">
                <div class="card">
                    <h3>CONCEALED CARRY</h3>
                    <p style="margin:1rem 0">WV permit certification course. 8-hour comprehensive training with live fire qualification.</p>
                    <ul style="margin:1.5rem 0;padding-left:1.5rem">
                        <li>Classroom instruction</li>
                        <li>Range time included</li>
                        <li>Permit application assistance</li>
                    </ul>
                    <a href="/courses/ccw" class="btn" style="width:100%">Enroll →</a>
                </div>
                <div class="card">
                    <h3>TACTICAL TRAINING</h3>
                    <p style="margin:1rem 0">Advanced firearms handling for security professionals and serious shooters.</p>
                    <ul style="margin:1.5rem 0;padding-left:1.5rem">
                        <li>Defensive pistol techniques</li>
                        <li>Low-light operations</li>
                        <li>Scenario-based training</li>
                    </ul>
                    <a href="/courses/tactical" class="btn" style="width:100%">Enroll →</a>
                </div>
            </div>
        </div>
    </section>
    
    <section class="section section-black" style="text-align:center">
        <div class="container">
            <h2 style="margin-bottom:2rem">Train With The Best</h2>
            <p style="opacity:0.8;margin-bottom:3rem;max-width:50ch;margin-left:auto;margin-right:auto">Join thousands of responsible gun owners who have trained with MDI. Your safety is our priority.</p>
            <a href="/contact" class="btn btn-white">Contact Us →</a>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <h4>MDI TRAINING</h4>
                    <p style="color:#999;margin-top:1rem">Professional firearms training in West Virginia.</p>
                </div>
                <div>
                    <h4>Courses</h4>
                    <a href="/courses/ccw">Concealed Carry</a>
                    <a href="/courses/tactical">Tactical Training</a>
                    <a href="/courses/basic">Basic Pistol</a>
                    <a href="/courses/advanced">Advanced Courses</a>
                </div>
                <div>
                    <h4>Company</h4>
                    <a href="/about">About</a>
                    <a href="/instructors">Instructors</a>
                    <a href="/facilities">Facilities</a>
                    <a href="/careers">Careers</a>
                </div>
                <div>
                    <h4>Contact</h4>
                    <a href="mailto:info@mditraining.com">info@mditraining.com</a>
                    <p style="color:#999;margin-top:1rem">Morgantown, WV</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2024 MDI TRAINING</p>
                <p>NRA Certified</p>
            </div>
        </div>
    </footer>
    '''


def generate_marketing_wild(p: dict) -> str:
    return f'''
    <header class="header">
        <div class="container header-inner">
            <a href="/" class="logo">ADVERTISE<span>WV</span></a>
            <nav class="nav" id="nav">
                <a href="/services">Services</a>
                <a href="/work">Work</a>
                <a href="/contact">Contact</a>
            </nav>
            <button class="menu-btn" onclick="document.getElementById('nav').classList.toggle('active')">☰</button>
        </div>
    </header>
    
    <section class="hero" style="padding-top:70px">
        <div class="container">
            <div class="hero-content">
                <p class="hero-label">Digital Marketing Agency</p>
                <h1>GROW</h1>
                <h1 style="margin-left:10vw">YOUR</h1>
                <h1 style="margin-left:20vw">BUSINESS</h1>
                <p style="margin-top:3rem;max-width:45ch">West Virginia's premier digital marketing agency. SEO, web design, social media, and PPC that delivers results.</p>
                <a href="/contact" class="btn" style="margin-top:3rem">Free Consultation →</a>
            </div>
        </div>
    </section>
    
    <section class="section section-gray">
        <div class="container">
            <h2 style="text-align:center;margin-bottom:4rem">Our Services</h2>
            <div class="grid grid-3">
                <div class="card" style="text-align:center">
                    <div style="font-size:3rem;margin-bottom:1rem">📈</div>
                    <h3>SEO</h3>
                    <p>Rank higher. Get found. Drive organic traffic.</p>
                </div>
                <div class="card" style="text-align:center">
                    <div style="font-size:3rem;margin-bottom:1rem">💻</div>
                    <h3>WEB DESIGN</h3>
                    <p>Beautiful, fast, conversion-focused websites.</p>
                </div>
                <div class="card" style="text-align:center">
                    <div style="font-size:3rem;margin-bottom:1rem">📱</div>
                    <h3>SOCIAL MEDIA</h3>
                    <p>Build your brand. Engage your audience.</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="section">
        <div class="container" style="text-align:center">
            <h2 style="margin-bottom:2rem">Ready to Scale?</h2>
            <p style="max-width:50ch;margin:0 auto 3rem">Let's build a marketing strategy that works for your business.</p>
            <a href="/contact" class="btn" style="font-size:1.125rem">Get Started →</a>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <h4>ADVERTISEWV</h4>
                    <p style="color:#999;margin-top:1rem">Digital marketing that delivers results.</p>
                </div>
                <div>
                    <h4>Services</h4>
                    <a href="/seo">SEO</a>
                    <a href="/web">Web Design</a>
                    <a href="/social">Social Media</a>
                    <a href="/ppc">PPC Advertising</a>
                </div>
                <div>
                    <h4>Company</h4>
                    <a href="/about">About</a>
                    <a href="/work">Work</a>
                    <a href="/careers">Careers</a>
                    <a href="/blog">Blog</a>
                </div>
                <div>
                    <h4>Contact</h4>
                    <a href="mailto:hello@advertisewv.com">hello@advertisewv.com</a>
                    <p style="color:#999;margin-top:1rem">Charleston, WV</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2024 ADVERTISEWV</p>
                <p>Results Driven</p>
            </div>
        </div>
    </footer>
    '''


def generate_default_wild(p: dict) -> str:
    return f'''
    <header class="header">
        <div class="container header-inner">
            <a href="/" class="logo">{p['name'].upper().replace(' ', '<span>')}</span></a>
            <nav class="nav" id="nav">
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
            <button class="menu-btn" onclick="document.getElementById('nav').classList.toggle('active')">☰</button>
        </div>
    </header>
    
    <section class="hero" style="padding-top:70px">
        <div class="container">
            <div class="hero-content">
                <h1>{p['name'].upper()}</h1>
                <p style="margin-top:2rem;max-width:50ch">{p['description']}</p>
                <a href="/contact" class="btn" style="margin-top:3rem">Get Started →</a>
            </div>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>© 2024 {p['name'].upper()}</p>
                <p>All Rights Reserved</p>
            </div>
        </div>
    </footer>
    '''


def main():
    """Build all 6 WILD & WONDERFUL websites"""
    
    projects = [
        {
            "name": "WILD & WONDERFUL",
            "title": "WILD & WONDERFUL - Web Design & Development Studio | WV",
            "description": "Award-winning web design studio. Brutalist designs with cutting-edge technology.",
            "type": "Portfolio",
            "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\app\dist_wild"
        },
        {
            "name": "NCRJ WATCH",
            "title": "NCRJ WATCH - Jail Accountability Platform | WV",
            "description": "Demanding accountability. Exposing inhumanity at North Central Regional Jail.",
            "type": "Advocacy",
            "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\NCRJFincal-main\public_html_wild"
        },
        {
            "name": "ADVERTISEWV",
            "title": "ADVERTISEWV - Digital Marketing Agency | West Virginia",
            "description": "West Virginia's premier digital marketing agency. SEO, web design, social media.",
            "type": "Marketing",
            "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\advertisewv_wild"
        },
        {
            "name": "DARK ROSE TATTOO",
            "title": "DARK ROSE TATTOO - Premium Tattoo Studio | WV",
            "description": "Custom tattoos and professional piercings in West Virginia. Walk-ins welcome.",
            "type": "Tattoo",
            "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\darkrose_wild"
        },
        {
            "name": "MDI TRAINING",
            "title": "MDI TRAINING - Firearms & Tactical Training | WV",
            "description": "NRA-certified firearms training in West Virginia. Concealed carry and tactical courses.",
            "type": "Training",
            "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\mdi_wild"
        },
        {
            "name": "ULTIMATE GOTTI LINE",
            "title": "ULTIMATE GOTTI LINE - American Bully Breeding | WV",
            "description": "Premium American Bully breeding. Gottiline bloodline. Healthy puppies.",
            "type": "Breeding",
            "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\ultimategotti_wild"
        }
    ]
    
    print("\n" + "="*60)
    print("WILD & WONDERFUL WEBSITES")
    print("Black & White. Zero Bloat. Maximum Impact.")
    print("="*60)
    
    for project in projects:
        output_dir = Path(project['path'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        html = generate_wild_template(project)
        (output_dir / "index.html").write_text(html, encoding='utf-8')
        
        print(f"\n[OK] {project['name']}")
        print(f"     -> {output_dir}")
    
    print("\n" + "="*60)
    print("ALL 6 SITES BUILT")
    print("Black & White design system applied")
    print("="*60)


if __name__ == "__main__":
    main()
