import streamlit as st
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
import sqlite3
import os
import hashlib
from datetime import datetime
import json
from pathlib import Path

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="DeadLock - Real APK Analyzer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/Gaurang-5/deadlock',
        'Report a bug': "https://github.com/Gaurang-5/deadlock/issues",
        'About': "# DeadLock - Real APK Security Analysis\nAnalyze actual APK files for banking app threats"
    }
)

# Initialize theme state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Modern Minimal UI CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Theme Toggle Button */
    .theme-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 50px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .theme-toggle:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    .theme-toggle-icon {
        font-size: 1.2rem;
    }
    
    .theme-toggle-text {
        font-size: 0.875rem;
        font-weight: 600;
        color: white;
    }
    
    /* Animated Background Canvas */
    #cyber-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: linear-gradient(135deg, #0a1628 0%, #1a2332 100%);
        transition: background 0.5s ease;
    }
    
    body.light-mode #cyber-canvas {
        background: linear-gradient(135deg, #f0f2f6 0%, #e2e8f0 100%);
    }
    
    /* Main container */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    
    .hero-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        font-weight: 400;
    }
    
    /* Card design */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border: 1px solid rgba(240, 240, 240, 0.5);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        color: #1a1a1a;
    }
    
    .custom-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    body.light-mode .custom-card {
        background: rgba(255, 255, 255, 0.98);
        border: 1px solid rgba(200, 200, 200, 0.3);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    body.light-mode .custom-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    /* Modern buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
    
    .stButton button:hover {
        box-shadow: 0 6px 20px rgba(102,126,234,0.6);
        transform: translateY(-2px);
    }
    
    /* Metrics styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(245, 247, 250, 0.95) 0%, rgba(195, 207, 226, 0.95) 100%);
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    body.light-mode div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 242, 246, 0.9) 100%);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Alert boxes */
    .stInfo {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border-left: 4px solid #0284c7;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #059669;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #d97706;
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #dc2626;
    }
    
    h2, h3 {
        color: #1a1a1a;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        transition: color 0.3s ease;
    }
    
    body.light-mode h1,
    body.light-mode h2,
    body.light-mode h3,
    body.light-mode p {
        color: #1a1a1a !important;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .hero-title {
            font-size: 2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .stButton button {
            width: 100%;
        }
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    html {
        scroll-behavior: smooth;
    }
    
    .main {
        background: transparent !important;
    }
</style>

<!-- Theme Toggle Button -->
<div class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">
    <span class="theme-toggle-icon" id="theme-icon">🌙</span>
    <span class="theme-toggle-text" id="theme-text">Dark</span>
</div>

<!-- Animated Cyber Background Canvas -->
<canvas id="cyber-canvas"></canvas>

<script>
let isDarkMode = true;

function toggleTheme() {
    isDarkMode = !isDarkMode;
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');
    
    if (isDarkMode) {
        body.classList.remove('light-mode');
        icon.textContent = '🌙';
        text.textContent = 'Dark';
    } else {
        body.classList.add('light-mode');
        icon.textContent = '☀️';
        text.textContent = 'Light';
    }
}

(function() {
    const canvas = document.getElementById('cyber-canvas');
    const ctx = canvas.getContext('2d');
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const particles = [];
    const particleCount = 50;
    const mouse = { x: null, y: null, radius: 150 };
    const lockSymbol = '🔒';
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 15 + 10;
            this.baseX = this.x;
            this.baseY = this.y;
            this.density = Math.random() * 30 + 10;
            this.vx = Math.random() * 0.5 - 0.25;
            this.vy = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.5 + 0.3;
            this.rotation = Math.random() * Math.PI * 2;
            this.rotationSpeed = (Math.random() - 0.5) * 0.02;
        }
        
        draw() {
            ctx.save();
            ctx.globalAlpha = this.opacity;
            ctx.translate(this.x, this.y);
            ctx.rotate(this.rotation);
            ctx.font = `${this.size}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            const gradient = ctx.createLinearGradient(-this.size/2, -this.size/2, this.size/2, this.size/2);
            if (isDarkMode) {
                gradient.addColorStop(0, '#667eea');
                gradient.addColorStop(0.5, '#764ba2');
                gradient.addColorStop(1, '#667eea');
            } else {
                gradient.addColorStop(0, '#4c51bf');
                gradient.addColorStop(0.5, '#5a67d8');
                gradient.addColorStop(1, '#4c51bf');
            }
            ctx.fillStyle = gradient;
            ctx.fillText(lockSymbol, 0, 0);
            ctx.restore();
        }
        
        update() {
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < mouse.radius && mouse.x != null) {
                let forceDirectionX = dx / distance;
                let forceDirectionY = dy / distance;
                let force = (mouse.radius - distance) / mouse.radius;
                this.x -= forceDirectionX * force * this.density;
                this.y -= forceDirectionY * force * this.density;
            } else {
                if (this.x !== this.baseX) {
                    let dx = this.x - this.baseX;
                    this.x -= dx / 20;
                }
                if (this.y !== this.baseY) {
                    let dy = this.y - this.baseY;
                    this.y -= dy / 20;
                }
            }
            
            this.baseX += this.vx;
            this.baseY += this.vy;
            
            if (this.baseX > canvas.width) this.baseX = 0;
            if (this.baseX < 0) this.baseX = canvas.width;
            if (this.baseY > canvas.height) this.baseY = 0;
            if (this.baseY < 0) this.baseY = canvas.height;
            
            this.rotation += this.rotationSpeed;
            this.opacity = 0.3 + Math.sin(Date.now() / 1000 + this.density) * 0.2;
        }
    }
    
    function init() {
        particles.length = 0;
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }
    init();
    
    function connect() {
        for (let a = 0; a < particles.length; a++) {
            for (let b = a + 1; b < particles.length; b++) {
                let dx = particles[a].x - particles[b].x;
                let dy = particles[a].y - particles[b].y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 120) {
                    if (isDarkMode) {
                        ctx.strokeStyle = `rgba(102, 126, 234, ${0.2 * (1 - distance / 120)})`;
                    } else {
                        ctx.strokeStyle = `rgba(76, 81, 191, ${0.3 * (1 - distance / 120)})`;
                    }
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particles[a].x, particles[a].y);
                    ctx.lineTo(particles[b].x, particles[b].y);
                    ctx.stroke();
                }
            }
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        connect();
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
        }
        requestAnimationFrame(animate);
    }
    animate();
    
    window.addEventListener('mousemove', function(event) {
        mouse.x = event.x;
        mouse.y = event.y;
    });
    
    window.addEventListener('mouseout', function() {
        mouse.x = null;
        mouse.y = null;
    });
})();
</script>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🔒 DeadLock</div>
    <div class="hero-subtitle">Real APK Analysis • Detect Fake Banking Apps • Security Threat Detection</div>
</div>
""", unsafe_allow_html=True)

# --- DATABASE INITIALIZATION ---
def init_database():
    conn = sqlite3.connect('apk_analysis.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS analyzed_apks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  apk_name TEXT,
                  package_name TEXT UNIQUE,
                  file_hash TEXT,
                  risk_score INTEGER,
                  threat_flags TEXT,
                  analysis_time TIMESTAMP,
                  status TEXT,
                  permissions TEXT,
                  manifest_data TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_metrics
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  analysis_time TIMESTAMP,
                  total_apks INTEGER,
                  threats_found INTEGER,
                  analysis_duration REAL,
                  permissions_count INTEGER)''')
    conn.commit()
    conn.close()

init_database()

# --- APK ANALYSIS FUNCTIONS ---
def extract_apk_info(apk_file):
    """Extract package name and manifest from APK"""
    try:
        with zipfile.ZipFile(apk_file, 'r') as zip_ref:
            # Read AndroidManifest.xml
            manifest_data = zip_ref.read('AndroidManifest.xml')
            
            # Extract package name (basic parsing)
            if b'package=' in manifest_data:
                start = manifest_data.find(b'package="') + 9
                end = manifest_data.find(b'"', start)
                package_name = manifest_data[start:end].decode('utf-8', errors='ignore')
                return package_name, manifest_data
    except Exception as e:
        st.error(f"Error reading APK: {str(e)}")
        return None, None
    
    return None, None

def analyze_permissions(apk_file):
    """Extract permissions from APK"""
    permissions = []
    try:
        with zipfile.ZipFile(apk_file, 'r') as zip_ref:
            manifest_data = zip_ref.read('AndroidManifest.xml')
            # Simple permission extraction
            if b'uses-permission' in manifest_data:
                parts = manifest_data.split(b'uses-permission')
                for part in parts[1:]:
                    if b'android:name=' in part:
                        start = part.find(b'android:name="') + 14
                        end = part.find(b'"', start)
                        perm = part[start:end].decode('utf-8', errors='ignore')
                        permissions.append(perm)
    except:
        pass
    
    return permissions

def calculate_apk_hash(apk_file):
    """Calculate SHA256 hash of APK"""
    sha256_hash = hashlib.sha256()
    with open(apk_file, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def analyze_apk_risk(package_name, permissions, manifest_data):
    """Analyze APK for security risks"""
    risk_score = 0
    flags = []
    
    suspicious_keywords = ['fake', 'clone', 'update', 'security', 'reward', 'cash', 'free']
    
    # Check package name for suspicious patterns
    for keyword in suspicious_keywords:
        if keyword.lower() in package_name.lower():
            risk_score += 25
            flags.append(f"Suspicious keyword: {keyword}")
    
    # Check for suspicious permissions
    dangerous_perms = [
        'android.permission.READ_CONTACTS',
        'android.permission.READ_SMS',
        'android.permission.ACCESS_FINE_LOCATION',
        'android.permission.RECORD_AUDIO',
        'android.permission.CAMERA'
    ]
    
    for perm in permissions:
        if any(dp in perm for dp in dangerous_perms):
            risk_score += 15
            flags.append(f"Dangerous permission: {perm}")
    
    # Package name normalization checks
    legit_banking_apps = [
        'com.phonepe',
        'com.paytm',
        'com.upi',
        'com.icici',
        'com.axis',
        'com.kotak',
        'com.hdfc'
    ]
    
    for legit in legit_banking_apps:
        if legit in package_name.lower():
            if package_name.lower() != legit:
                risk_score += 50
                flags.append("Typosquatting attempt detected")
    
    # Risk classification
    if risk_score >= 70:
        status = "🔴 CRITICAL"
    elif risk_score >= 50:
        status = "🟡 MEDIUM"
    else:
        status = "🟢 SAFE"
    
    return risk_score, flags, status

# --- UI LAYOUT ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📱 APK Upload")
    
    uploaded_file = st.file_uploader("Upload APK File", type="apk", help="Select a banking app APK to analyze")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file is not None:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # Save uploaded file temporarily
        with open("temp.apk", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract APK info
        package_name, manifest_data = extract_apk_info("temp.apk")
        permissions = analyze_permissions("temp.apk")
        apk_hash = calculate_apk_hash("temp.apk")
        
        st.info(f"**Package:** {package_name}")
        st.info(f"**Permissions Found:** {len(permissions)}")
        st.info(f"**File Hash:** {apk_hash[:16]}...")
        
        if st.button("🔍 Analyze APK"):
            # Analyze risk
            risk_score, flags, status = analyze_apk_risk(package_name, permissions, manifest_data)
            
            # Store in database
            conn = sqlite3.connect('apk_analysis.db')
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO analyzed_apks 
                             (apk_name, package_name, file_hash, risk_score, threat_flags, analysis_time, status, permissions)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (uploaded_file.name, package_name, apk_hash, risk_score, 
                           json.dumps(flags), datetime.now(), status, json.dumps(permissions)))
                conn.commit()
            except:
                pass
            conn.close()
            
            # Store in session
            st.session_state.analysis_result = {
                'package_name': package_name,
                'risk_score': risk_score,
                'flags': flags,
                'status': status,
                'permissions': permissions,
                'file_hash': apk_hash
            }
        
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("### 🚨 Analysis Results")
    
    if 'analysis_result' in st.session_state:
        result = st.session_state.analysis_result
        
        # Threat Dashboard
        col_status, col_score = st.columns(2)
        
        with col_status:
            st.markdown(f'<div class="custom-card"><h3>{result["status"]}</h3></div>', unsafe_allow_html=True)
        
        with col_score:
            st.metric("Risk Score", f"{result['risk_score']}/100")
        
        # Threat Flags
        st.markdown("#### ⚠️ Detected Threats")
        if result['flags']:
            for flag in result['flags']:
                st.warning(f"🚨 {flag}")
        else:
            st.success("✅ No threats detected")
        
        # Permissions
        st.markdown("#### 📋 Permissions")
        if result['permissions']:
            cols = st.columns(2)
            for i, perm in enumerate(result['permissions']):
                with cols[i % 2]:
                    st.write(f"• {perm}")
        
        # Evidence Kit
        st.markdown("#### 📄 Evidence Summary")
        evidence = f"""
        **APK Analysis Report**
        
        Package: {result['package_name']}
        Risk Score: {result['risk_score']}/100
        Status: {result['status']}
        Permissions: {len(result['permissions'])}
        Hash: {result['file_hash'][:32]}...
        """
        st.code(evidence)
    else:
        st.info("📤 Upload an APK file to start analysis")

# Historical Analysis
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 Analysis History"):
    conn = sqlite3.connect('apk_analysis.db')
    history = pd.read_sql_query(
        "SELECT apk_name, package_name, risk_score, status, analysis_time FROM analyzed_apks ORDER BY analysis_time DESC LIMIT 10",
        conn
    )
    conn.close()
    
    if not history.empty:
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No analysis history yet")

# Clean up temp file
if os.path.exists("temp.apk"):
    try:
        os.remove("temp.apk")
    except:
        pass
