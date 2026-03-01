# -*- coding: utf-8 -*-
"""
AgriGuard AI — Advanced Multi-Language AI Backend
Fully Standalone Version (Zero External Files Needed)
Powered by Google Gemini Vision
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import logging
from datetime import datetime

# --- from dataclasses import dataclass ---
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

import io
import re
import json
import traceback

# --- 1. Constants & Configurations ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "ar")
GEMINI_MODEL = "models/gemini-flash-latest"
GEMINI_MAX_TOKENS = 4096

BLUR_THRESHOLD = 80.0
BRIGHT_MIN = 30.0
BRIGHT_MAX = 240.0
GREEN_RATIO_THRESHOLD = 0.05

def get_api_key() -> str:
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not key:
        raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY environment variable.")
    return key


# --- 2. Embedded HTML / CSS / JS ---
CSS_CONTENT = """
/* Import High-Legibility Fonts */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --tech-bg: #030712;
    --tech-surface: #0f172a;
    --tech-accent: #2563eb;
    --tech-highlight: #38bdf8;
    --tech-silver: #f1f5f9;
    --tech-muted: #64748b;
    --glass-border: rgba(255, 255, 255, 0.08);
    --shadow-elite: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
}

* { box-sizing: border-box; }

body {
    margin: 0; padding: 0; background: var(--tech-bg); font-family: 'Cairo', 'Inter', sans-serif;
    color: var(--tech-silver); line-height: 1.6; overflow-x: hidden;
}

#particles-canvas {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; opacity: 0.4;
}

.app-container { position: relative; z-index: 10; max-width: 1400px; margin: 0 auto; padding: 0 2rem; }

.navbar { display: flex; justify-content: space-between; align-items: center; padding: 2rem 0; }
.nav-brand { font-size: 1.8rem; font-weight: 900; letter-spacing: 2px; }
.nav-brand span { color: var(--tech-highlight); }
.nav-status {
    display: flex; align-items: center; gap: 0.8rem; background: rgba(0, 0, 0, 0.5); padding: 0.6rem 1.4rem;
    border-radius: 50px; border: 1px solid var(--glass-border); font-size: 0.75rem; font-weight: 700; letter-spacing: 1px;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981; }

.hero-header { text-align: center; padding: 6rem 1rem; margin-bottom: 4rem; }
.hero-header h1 {
    font-size: 5rem; line-height: 1; margin: 0; font-weight: 900;
    background: linear-gradient(to right, #ffffff 30%, var(--tech-highlight) 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-header h1 span { display: block; filter: brightness(1.2); }
.hero-header p { font-size: 1.4rem; color: var(--tech-muted); max-width: 800px; margin: 2rem auto 0; }

.content-grid { display: grid; grid-template-columns: 450px 1fr; gap: 3rem; margin-bottom: 6rem; }
@media (max-width: 1100px) { .content-grid { grid-template-columns: 1fr; } }

.card {
    background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border-radius: 24px;
    border: 1px solid var(--glass-border); padding: 2.5rem; margin-bottom: 2rem; box-shadow: var(--shadow-elite);
    position: relative; overflow: hidden;
}

.card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.step-num {
    font-size: 0.9rem; font-weight: 800; color: var(--tech-highlight); background: rgba(56, 189, 248, 0.1);
    width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 12px;
    border: 1px solid rgba(56, 189, 248, 0.2);
}
.card-header h2 { font-size: 1.4rem; margin: 0; font-weight: 800; }
.card-header h2 span { display: block; font-size: 0.8rem; color: var(--tech-muted); font-weight: 500; margin-top: 0.2rem; }

.upload-zone {
    border: 2px dashed rgba(255, 255, 255, 0.05); background: rgba(0, 0, 0, 0.2); border-radius: 20px;
    padding: 4rem 1rem; text-align: center; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.upload-zone:hover { border-color: var(--tech-highlight); background: rgba(37, 99, 235, 0.05); }
.upload-icon { font-size: 4rem; margin-bottom: 1.5rem; filter: drop-shadow(0 0 15px var(--tech-highlight)); }
.upload-zone h3 { margin: 0; font-size: 1.2rem; color: #fff; }
.upload-zone p { margin: 0.5rem 0 0; color: var(--tech-muted); font-size: 0.9rem; }

.preview-container img { width: 100%; max-height: 400px; object-fit: contain; border-radius: 16px; border: 1px solid var(--glass-border); }
.btn-text { background: none; border: none; color: var(--tech-highlight); cursor: pointer; font-weight: 700; margin-top: 1rem; }

.btn {
    position: relative; width: 100%; padding: 1.2rem; border-radius: 16px; border: none; font-family: 'Cairo', sans-serif;
    font-weight: 800; font-size: 1.2rem; cursor: pointer; overflow: hidden; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.btn-primary { background: var(--tech-accent); color: #fff; box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.5); }
.btn-primary:hover { transform: translateY(-5px); box-shadow: 0 20px 40px -10px rgba(37, 99, 235, 0.7); }

.placeholder-content { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--tech-muted); }
.placeholder-icon { font-size: 5rem; opacity: 0.2; margin-bottom: 2rem; }

.res-title { font-size: 2.8rem !important; margin: 0 !important; color: #fff !important; }
.res-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 2.5rem 0; }
.badge { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border); padding: 1.5rem; border-radius: 20px; text-align: center; }
.badge label { display: block; font-size: 0.8rem; color: var(--tech-muted); text-transform: uppercase; margin-bottom: 0.5rem; letter-spacing: 1px; }
.badge span { font-size: 2rem; font-weight: 900; color: var(--tech-highlight); }

.treatment-area { background: rgba(37, 99, 235, 0.08); border-radius: 24px; padding: 2.5rem; border-right: 6px solid var(--tech-accent); }
.treatment-area h4 { font-size: 1.4rem; color: var(--tech-highlight) !important; margin: 0 0 1.5rem; }
.treatment-area p { margin: 0; font-size: 1.1rem; line-height: 1.8; }

.stats-row { display: flex; gap: 1.5rem; }
.stat-item { flex: 1; background: rgba(0, 0, 0, 0.2); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--glass-border); }
.stat-label { font-size: 0.75rem; color: var(--tech-muted); }
.stat-val { font-size: 2rem; font-weight: 900; color: var(--tech-highlight); }

.spinner-container { text-align: center; padding: 4rem 0; }
.liquid-spinner {
    width: 80px; height: 80px; margin: 0 auto 2rem; border: 4px solid rgba(255, 255, 255, 0.05);
    border-top-color: var(--tech-highlight); border-radius: 50%; animation: spin 0.8s cubic-bezier(0.5, 0.1, 0.4, 0.9) infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.app-footer { text-align: center; padding: 4rem 0; color: var(--tech-muted); font-size: 0.9rem; }
"""

JS_CONTENT = """
const STATE = { language: 'ar', selectedFile: null, isAnalyzing: false, context: null };
const UI = {
    uploadZone: document.getElementById('upload-zone'),
    fileInput: document.getElementById('file-input'),
    analyzeBtn: document.getElementById('analyze-btn'),
    resultCard: document.getElementById('result-card'),
    placeholder: document.getElementById('results-placeholder'),
    loadingSpinner: document.getElementById('loading-spinner'),
    analysisContent: document.getElementById('analysis-content'),
    previewContainer: document.getElementById('preview-container'),
    previewImage: document.getElementById('preview-image'),
    uploadContent: document.getElementById('upload-content')
};

document.addEventListener('DOMContentLoaded', () => {
    initParticles(); initUpload(); checkSystemStatus(); loadAnalytics();
});

function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    window.addEventListener('resize', resize); resize();
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width; this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5; this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25; this.opacity = Math.random() * 0.5 + 0.1;
        }
        update() {
            this.x += this.speedX; this.y += this.speedY;
            if (this.x > canvas.width) this.x = 0; if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0; if (this.y < 0) this.y = canvas.height;
        }
        draw() {
            ctx.fillStyle = `rgba(56, 189, 248, ${this.opacity})`; ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
        }
    }
    for (let i = 0; i < 70; i++) particles.push(new Particle());
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); }); requestAnimationFrame(animate);
    }
    animate();
}

async function checkSystemStatus() {
    try {
        const res = await fetch('/api/status'); const data = await res.json();
        const dot = document.getElementById('status-dot');
        dot.style.background = data.status === 'online' ? '#10b981' : '#ef4444';
        dot.style.boxShadow = `0 0 10px ${data.status === 'online' ? '#10b981' : '#ef4444'}`;
    } catch (e) { console.error("Link Failure"); }
}

function initUpload() {
    UI.uploadZone.addEventListener('click', () => UI.fileInput.click());
    UI.fileInput.addEventListener('change', (e) => { if (e.target.files.length > 0) handleFile(e.target.files[0]); });
    UI.uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); UI.uploadZone.style.borderColor = '#38bdf8'; });
    UI.uploadZone.addEventListener('dragleave', () => UI.uploadZone.style.borderColor = '');
    UI.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault(); UI.uploadZone.style.borderColor = '';
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) return;
    STATE.selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        UI.previewImage.src = e.target.result;
        UI.previewContainer.style.display = 'block'; UI.uploadContent.style.display = 'none';
        UI.placeholder.style.display = 'flex'; UI.analysisContent.innerHTML = '';
    };
    reader.readAsDataURL(file);
}

function resetFile() {
    STATE.selectedFile = null; UI.fileInput.value = ''; UI.previewContainer.style.display = 'none';
    UI.uploadContent.style.display = 'block'; UI.analysisContent.innerHTML = ''; UI.placeholder.style.display = 'flex';
}

async function handleAnalysis() {
    if (!STATE.selectedFile || STATE.isAnalyzing) return;
    STATE.isAnalyzing = true; UI.analyzeBtn.disabled = true;
    UI.placeholder.style.display = 'none'; UI.loadingSpinner.style.display = 'block'; UI.analysisContent.innerHTML = '';

    const formData = new FormData();
    formData.append('image', STATE.selectedFile); formData.append('language', STATE.language);

    try {
        const res = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        UI.loadingSpinner.style.display = 'none';
        if (data.error) { showError(data.error); }
        else if (data.quality && !data.quality.is_valid) { showQualityWarning(data.quality.warnings); }
        else { STATE.context = data; renderAnalysis(data); saveToHistory(data); }
    } catch (e) {
        UI.loadingSpinner.style.display = 'none'; showError("Satellite connection lost. Please verify server status.");
    } finally { STATE.isAnalyzing = false; UI.analyzeBtn.disabled = false; }
}

function showError(msg) { UI.analysisContent.innerHTML = `<div class="error-panel">🚨 <strong>خطأ في النظام:</strong> ${msg}</div>`; }
function showQualityWarning(warnings) {
    UI.analysisContent.innerHTML = `<div class="warning-panel"><h3>⚠️ جودة الصورة غير كافية</h3><ul>${warnings.map(w => `<li>${w}</li>`).join('')}</ul><p>يرجى محاكاة إضاءة أفضل.</p></div>`;
}

function renderAnalysis(data) {
    const isAr = STATE.language === 'ar';
    const disease = isAr ? (data.disease_name_ar || data.disease_name) : (data.disease_name_en || data.disease_name);
    const health = data.health_score || 0; const confidence = Math.round((data.confidence || 0) * 100);
    const rec = isAr ? (data.recommendation?.treatment_plan_ar || data.recommendation?.treatment_plan) : (data.recommendation?.treatment_plan_en || data.recommendation?.treatment_plan);
    UI.analysisContent.innerHTML = `
        <div class="result-box">
            <h1 class="res-title">${disease}</h1>
            <div class="res-meta">
                <div class="badge"><label>صحة النبات</label><span>${health}%</span></div>
                <div class="badge"><label>ثقة الذكاء الاصطناعي</label><span>${confidence}%</span></div>
            </div>
            <div class="treatment-area">
                <h4>🔬 بروتوكول العلاج العلمي:</h4>
                <p>${rec || 'لا توجد بيانات علاج متوفرة لهذا التشخيص.'}</p>
            </div>
        </div>
    `;
}

async function saveToHistory(data) {
    try {
        await fetch('/api/save', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ disease: data.disease_name, confidence: data.confidence, health_score: data.health_score })
        });
        loadAnalytics();
    } catch (e) { }
}

async function loadAnalytics() {
    try {
        const res = await fetch('/api/stats'); const data = await res.json();
        document.getElementById('stat-total').textContent = data.total_scans; document.getElementById('stat-avg').textContent = data.avg_health + '%';
    } catch (e) { }
}
"""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriGuard AI — المؤسسة العالمية لصحة النباتات</title>
    <!-- CSS is loaded natively -->
    <link rel="stylesheet" href="/static/style.css">
</head>
<body class="rtl">
    <canvas id="particles-canvas"></canvas>
    <div class="app-container">
        <!-- Navigation -->
        <nav class="navbar">
            <div class="nav-brand">AGRIGUARD <span>AI</span></div>
            <div class="nav-status">
                <span id="status-dot" class="dot"></span>
                <span data-i18n="status_online">SATELLITE LINK ACTIVE</span>
            </div>
        </nav>
        <!-- Hero Section -->
        <header class="hero-header reveal">
            <h1 data-i18n="hero_title">Precision Plant <span>Pathology</span></h1>
            <p data-i18n="hero_desc">المنصة المؤسسية لتحليل أمراض النباتات باستخدام الذكاء الاصطناعي الفائق. دقة علمية، تشخيص فوري، وخطط علاجية شاملة.</p>
        </header>
        <main class="content-grid">
            <!-- Left: Logic & Input -->
            <div class="control-panel reveal">
                <section class="card analyzer-card">
                    <div class="card-header">
                        <span class="step-num">01</span>
                        <h2 data-i18n="analyzer_title">تحميل العينة <span>(Image Upload)</span></h2>
                    </div>
                    <div id="upload-zone" class="upload-zone">
                        <input type="file" id="file-input" hidden accept="image/*">
                        <div id="upload-content">
                            <div class="upload-icon">💠</div>
                            <h3 data-i18n="upload_title">اسحب الصورة هنا</h3>
                            <p data-i18n="upload_desc">أو انقر للاختيار من الجهاز (JPG, PNG)</p>
                        </div>
                        <div id="preview-container" class="preview-container" style="display:none">
                            <img id="preview-image" src="" alt="Sample Preview">
                            <div class="preview-actions">
                                <button class="btn-text" onclick="resetFile()" data-i18n="btn_change">استبدال الصورة</button>
                            </div>
                        </div>
                    </div>
                    <div class="action-bar" style="margin-top: 2rem;">
                        <button id="analyze-btn" class="btn btn-primary" onclick="handleAnalysis()" data-i18n="btn_analyze">
                            <span>بدء التحليل الذكي</span>
                        </button>
                    </div>
                </section>
                <section class="card stats-card">
                    <div class="card-header">
                        <span class="step-num">02</span>
                        <h2 data-i18n="dash_title">ملخص الأنظمة <span>(System Stats)</span></h2>
                    </div>
                    <div class="stats-row">
                        <div class="stat-item">
                            <div class="stat-label">إجمالي الفحوصات</div>
                            <div id="stat-total" class="stat-val">0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">متوسط الصحة</div>
                            <div id="stat-avg" class="stat-val">0%</div>
                        </div>
                    </div>
                </section>
            </div>
            <!-- Right: Results -->
            <div class="display-panel reveal">
                <section id="result-card" class="card result-card" style="min-height: 400px;">
                    <div id="results-placeholder" class="placeholder-content">
                        <div class="placeholder-icon">📡</div>
                        <p>بانتظار تحليل العينة...</p>
                    </div>
                    <div id="loading-spinner" class="spinner-container" style="display:none">
                        <div class="liquid-spinner"></div>
                        <p>جاري المعالجة بواسطة الذكاء الاصطناعي...</p>
                    </div>
                    <div id="analysis-content" class="analysis-content"></div>
                </section>
            </div>
        </main>
        <footer class="app-footer">
            <p>© 2026 AgriGuard AI — القمة العالمية في التكنولوجيا الزراعية الذكية</p>
        </footer>
    </div>
    <!-- JS is loaded natively -->
    <script src="/static/app.js"></script>
</body>
</html>
"""

# --- 3. Domain Entities ---

@dataclass
class ImageQuality:
    is_valid: bool
    blur_score: float
    brightness_score: float
    green_ratio: float
    warnings: List[str]

@dataclass
class Recommendation:
    treatment_plan: str
    suggested_pesticide: str
    application_frequency: str
    safety_precautions: str
    treatment_plan_ar: Optional[str] = None
    treatment_plan_en: Optional[str] = None
    suggested_pesticide_ar: Optional[str] = None
    suggested_pesticide_en: Optional[str] = None
    application_frequency_ar: Optional[str] = None
    application_frequency_en: Optional[str] = None
    safety_precautions_ar: Optional[str] = None
    safety_precautions_en: Optional[str] = None

@dataclass
class PredictionResult:
    disease_name: str
    confidence: float
    health_score: float
    recommendation: Optional[Recommendation] = None
    plant_type: Optional[str] = None
    severity: Optional[str] = None
    affected_part: Optional[str] = None
    pathogen_type: Optional[str] = None
    scientific_explanation: Optional[str] = None
    differential_diagnosis: Optional[str] = None
    treatment_effectiveness: Optional[str] = None
    prognosis: Optional[str] = None
    plant_type_ar: Optional[str] = None
    plant_type_en: Optional[str] = None
    disease_name_ar: Optional[str] = None
    disease_name_en: Optional[str] = None
    severity_ar: Optional[str] = None
    severity_en: Optional[str] = None
    affected_part_ar: Optional[str] = None
    affected_part_en: Optional[str] = None
    scientific_explanation_ar: Optional[str] = None
    scientific_explanation_en: Optional[str] = None
    differential_diagnosis_ar: Optional[str] = None
    differential_diagnosis_en: Optional[str] = None
    treatment_effectiveness_ar: Optional[str] = None
    treatment_effectiveness_en: Optional[str] = None
    prognosis_ar: Optional[str] = None
    prognosis_en: Optional[str] = None
    symptoms_analysis: Optional[str] = None
    is_plant: bool = True

# --- 4. Image Processor ---
try:
    import cv2
    import numpy as np
except ImportError:
    logging.warning("OpenCV/NumPy not installed. Image pre-validation will be skipped.")
    cv2 = None

class ImageProcessor:
    @staticmethod
    def validate_image(image_bytes) -> ImageQuality:
        if cv2 is None:
            return ImageQuality(True, 100.0, 100.0, 1.0, [])
            
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return ImageQuality(False, 0, 0, 0, ["Invalid image file"])

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness_score = np.mean(gray)
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        green_ratio = np.sum(mask > 0) / (img.shape[0] * img.shape[1])
        
        warnings = []
        if blur_score < BLUR_THRESHOLD: warnings.append("Image is too blurry. Please take a clearer photo.")
        if brightness_score < BRIGHT_MIN: warnings.append("Image is too dark. Please increase lighting.")
        elif brightness_score > BRIGHT_MAX: warnings.append("Image is too bright. Please reduce glare.")
        if green_ratio < GREEN_RATIO_THRESHOLD: warnings.append("No plant material detected. Ensure the specimen occupies most of the frame.")
            
        is_valid = len(warnings) <= 1
        return ImageQuality(is_valid=is_valid, blur_score=round(blur_score, 2), brightness_score=round(brightness_score, 2), green_ratio=round(green_ratio, 4), warnings=warnings)

# --- 5. History Manager ---
class HistoryManager:
    def __init__(self, file_path: str = "data/scans.csv"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        try:
            import pandas as pd
            if not os.path.exists(self.file_path):
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                pd.DataFrame(columns=["timestamp", "disease", "confidence", "health_score"]).to_csv(self.file_path, index=False)
        except ImportError: pass

    def log_scan(self, disease: str, confidence: float, health_score: float):
        try:
            import pandas as pd
            new_data = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "disease": disease, "confidence": round(confidence, 2), "health_score": round(health_score, 2)}
            pd.DataFrame([new_data]).to_csv(self.file_path, mode='a', header=False, index=False)
        except ImportError: pass

    def get_history(self):
        try:
            import pandas as pd
            if os.path.exists(self.file_path): return pd.read_csv(self.file_path)
        except Exception: pass
        class DummyDF:
            def __len__(self): return 0
            @property
            def empty(self): return True
            def mean(self): return 0
            def mode(self):
                class D:
                    @property
                    def empty(self): return True
                return D()
            def __getitem__(self, key): return self
        return DummyDF()

# --- 6. Gemini Client ---
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    from PIL import Image
except ImportError:
    genai = None

SYSTEM_PROMPT = """You are Dr. AgriGuard, an elite AI Plant Pathologist. Complete JSON format strictly!"""

class GeminiClient:
    def __init__(self, api_key: str):
        if not genai:
            logging.error("google.generativeai not installed")
            return
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(temperature=0.2, max_output_tokens=GEMINI_MAX_TOKENS, response_mime_type="application/json"),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            system_instruction=SYSTEM_PROMPT
        )
    
    def analyze_plant(self, image_bytes: bytes, language: str = "en") -> Dict[str, Any]:
        if not hasattr(self, 'model'): return self._get_fallback_result(language)
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGB': img = img.convert('RGB')
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            prompt = self._create_premium_prompt(language)
            response = self.model.generate_content([prompt, img], request_options={"timeout": 60})
            
            if not getattr(response, 'text', None): return self._get_fallback_result(language)
            cleaned = re.sub(r'^```(json)?\s*', '', response.text.strip(), flags=re.MULTILINE)
            cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
            result = json.loads(cleaned)
            
            if "recommendation" not in result: result["recommendation"] = {}
            if "is_plant" not in result: result["is_plant"] = True
            return result
        except Exception as e:
            logging.error(f"Gemini API failure: {e}")
            return self._get_fallback_result(language)
            
    def _create_premium_prompt(self, language: str) -> str:
        base = """Analyze this plant. Follow Chain-of-Thought reasoning, then return strictly this JSON format:
{
  "is_plant": true/false, "plant_type_ar": "", "plant_type_en": "", "disease_name_ar": "", "disease_name_en": "",
  "confidence": 0.85, "is_healthy": false, "health_score": 50,
  "recommendation": { "treatment_plan_ar": "", "treatment_plan_en": "" }
}"""
        return base

    def _get_fallback_result(self, language: str) -> Dict[str, Any]:
        return {
            "is_plant": True, "plant_type_ar": "غير معروف", "plant_type_en": "Unknown",
            "disease_name_ar": "عطل في التحليل", "disease_name_en": "Analysis Error", "confidence": 0.0, "is_healthy": False,
            "recommendation": {"treatment_plan_ar": "يرجى المحاولة مرة أخرى", "treatment_plan_en": "Please try again"}
        }

# --- 7. Model Predictor & Analyzer ---
class ModelPredictor:
    def __init__(self, api_key: str = None):
        try:
            self.api_key = api_key or get_api_key()
            self.gemini_client = GeminiClient(self.api_key)
        except Exception:
            self.gemini_client = None

    def predict(self, image_bytes: bytes, language: str = "en"):
        if not self.gemini_client: return None, 0.0
        try:
            response = self.gemini_client.analyze_plant(image_bytes, language)
            return response, float(response.get("confidence", 0.75))
        except Exception:
            return None, 0.0

class PlantAnalyzer:
    def __init__(self, model_predictor: ModelPredictor):
        self.image_processor = ImageProcessor()
        self.model_predictor = model_predictor

    def analyze(self, file_path: str, language: str = "ar") -> dict:
        with open(file_path, "rb") as f: image_bytes = f.read()
        quality = self.image_processor.validate_image(image_bytes)
        if not quality.is_valid:
            return {"quality": {"is_valid": False, "warnings": quality.warnings}}

        res, confidence = self.model_predictor.predict(image_bytes, language)
        if not res or not isinstance(res, dict): return {"error": "Analysis failed"}

        def get_val(key_base, default=''):
            if language == 'ar' and res.get(f'{key_base}_ar'): return res.get(f'{key_base}_ar')
            if language != 'ar' and res.get(f'{key_base}_en'): return res.get(f'{key_base}_en')
            return res.get(f'{key_base}_en', res.get(f'{key_base}_ar', res.get(key_base, default)))

        rec_data = res.get('recommendation', {})
        def get_rec(key_base):
            if language == 'ar' and rec_data.get(f'{key_base}_ar'): return rec_data.get(f'{key_base}_ar')
            if language != 'ar' and rec_data.get(f'{key_base}_en'): return rec_data.get(f'{key_base}_en')
            return rec_data.get(f'{key_base}_en', rec_data.get(f'{key_base}_ar', rec_data.get(key_base, 'N/A')))

        is_h = res.get('is_healthy', False)
        health_score = max(min(100.0 * confidence if is_h else (1.0 - confidence) * 100.0, 100.0), 5.0)

        return {
            "quality": {"is_valid": True, "warnings": quality.warnings},
            "disease_name": get_val('disease_name', 'Unknown'),
            "confidence": confidence,
            "health_score": health_score,
            "recommendation": {"treatment_plan": get_rec('treatment_plan')},
            "plant_type": get_val('plant_type', 'Unknown'),
        }

# --- 8. Flask Server Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# We use an empty template_folder because all templates come from memory.
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

try:
    predictor = ModelPredictor()
    plant_analyzer = PlantAnalyzer(predictor)
    ai_online = True
except Exception:
    ai_online = False

history_manager = HistoryManager()

# --- 9. Native Routes (Serve directly from memory) ---
@app.route('/')
def index():
    return HTML_CONTENT

@app.route('/static/style.css')
def serve_css():
    response = make_response(CSS_CONTENT)
    response.headers['Content-Type'] = 'text/css'
    return response

@app.route('/static/app.js')
def serve_js():
    response = make_response(JS_CONTENT)
    response.headers['Content-Type'] = 'application/javascript'
    return response

# --- 10. API Endpoints ---
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online" if ai_online else "offline", "model": "Gemini 1.5 Pro", "engine": "AgriGuard AI Core v4.0"})

@app.route('/api/analyze', methods=['POST'])
def analyze_plant():
    if not ai_online: return jsonify({"error": "AI Engine is offline"}), 503
    if 'image' not in request.files: return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '': return jsonify({"error": "No file selected"}), 400

    language = request.form.get('language', 'ar')
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{file.filename}")
        file.save(file_path)

        result = plant_analyzer.analyze(file_path, language=language)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Analysis Failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_scan():
    data = request.json
    if not data: return jsonify({"error": "No data provided"}), 400
    try:
        history_manager.log_scan(data.get('disease', 'Unknown'), data.get('confidence', 0), data.get('health_score', 0))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        df = history_manager.get_history()
        total_scans = len(df)
        avg_health = round(df['health_score'].mean(), 1) if total_scans > 0 else 0
        common_disease = df['disease'].mode()[0] if total_scans > 0 and not df['disease'].mode().empty else "None"
        return jsonify({"total_scans": total_scans, "avg_health": avg_health, "common_disease": common_disease})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Force single threaded to avoid Watchdog/Waitress overhead while testing standalone scripts
    # Turn off debug mode to avoid werkzeug reloader crashing.
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

