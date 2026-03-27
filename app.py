"""
BeautyReel AI — Streamlit Dashboard (Pure Python — No HTML/CSS)
"""

import streamlit as st
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from rembg import remove
import io, requests, time
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout, colorx
from moviepy.video.VideoClip import VideoClip
import random, json
from datetime import datetime

st.set_page_config(
    page_title = "BeautyReel AI",
    page_icon  = "💄",
    layout     = "wide",
    initial_sidebar_state = "expanded"
)

# Write theme config at runtime
import os
config_dir  = Path(".streamlit")
config_file = config_dir / "config.toml"
config_dir.mkdir(exist_ok=True)
if not config_file.exists():
    config_file.write_text("""
[theme]
primaryColor              = "#D4748A"
backgroundColor           = "#FFF5F0"
secondaryBackgroundColor  = "#FFE8E0"
textColor                 = "#3D1A1A"
font                      = "sans serif"
""".strip())

# =============================================================================
#  CONFIG
# =============================================================================

HF_TOKEN   = "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" 
FLUX_URL   = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
TARGET_W   = 1080
TARGET_H   = 1920
OUTPUT_DIR = Path("streamlit_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
HISTORY_FILE = OUTPUT_DIR / "history.json"

VIBES = {
    "✨ Luxury"         : {"prompt": "deep midnight black background, golden warm glow, cinematic luxury",    "color": (220,185,130)},
    "🤍 Minimalist"    : {"prompt": "pure clean white background, soft diffused natural light",              "color": (180,160,150)},
    "💫 Funky"         : {"prompt": "holographic iridescent background, neon rainbow glow, futuristic",      "color": (180,140,230)},
    "💋 Bold Glam"     : {"prompt": "deep burgundy velvet background, dramatic spotlight, high-end glamour", "color": (220,80,100)},
    "🌸 Soft Feminine" : {"prompt": "dreamy blush pink to lavender gradient, soft feminine glow",            "color": (245,175,195)},
}

GRADIENT_BGS = {
    "Dark Burgundy"  : {"top":(6,1,3),      "mid":(80,8,18),    "bot":(4,1,2),    "glow":(200,60,80)},
    "Rose Gold"      : {"top":(20,8,14),    "mid":(95,45,62),   "bot":(15,5,10),  "glow":(225,140,168)},
    "Pure Black"     : {"top":(4,4,4),      "mid":(22,18,20),   "bot":(2,2,2),    "glow":(180,120,140)},
    "White Marble"   : {"top":(200,195,190),"mid":(242,240,237),"bot":(185,180,175),"glow":(200,190,185)},
    "Midnight Blue"  : {"top":(2,4,18),     "mid":(8,20,65),    "bot":(1,2,12),   "glow":(80,120,220)},
    "Deep Emerald"   : {"top":(2,10,6),     "mid":(8,55,30),    "bot":(1,6,3),    "glow":(60,180,100)},
    "Lavender Dream" : {"top":(10,5,20),    "mid":(55,35,90),   "bot":(7,3,14),   "glow":(190,160,230)},
}

SHOTS = [
    {"zoom_s":1.03,"zoom_e":1.00,"px":0.00, "py":0.00, "bright":1.04},
    {"zoom_s":1.04,"zoom_e":1.02,"px":0.00, "py":-0.02,"bright":1.04},
    {"zoom_s":1.03,"zoom_e":1.03,"px":-0.03,"py":0.00, "bright":1.04},
    {"zoom_s":1.03,"zoom_e":1.03,"px":0.03, "py":0.00, "bright":1.04},
    {"zoom_s":1.04,"zoom_e":1.02,"px":0.00, "py":0.02,"bright":1.05},
    {"zoom_s":1.04,"zoom_e":1.02,"px":0.01, "py":-0.01,"bright":1.05},
    {"zoom_s":1.02,"zoom_e":1.00,"px":0.00, "py":0.00, "bright":1.03},
]

# =============================================================================
#  HISTORY
# =============================================================================

def load_history():
    if HISTORY_FILE.exists():
        try: return json.loads(HISTORY_FILE.read_text())
        except: pass
    return []

def save_history(product, mode, path):
    history = load_history()
    history.insert(0, {
        "product": product,
        "mode"   : mode,
        "path"   : str(path),
        "time"   : datetime.now().strftime("%H:%M")
    })
    HISTORY_FILE.write_text(json.dumps(history[:5]))

# =============================================================================
#  CORE FUNCTIONS
# =============================================================================

def get_font(size, bold=False):
    for fp in [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try: return ImageFont.truetype(fp, size)
        except: continue
    return ImageFont.load_default()

def text_arr(text, w, h, size, color, bold=False):
    img  = Image.new("RGBA",(w,h),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font = get_font(size, bold)
    try:
        bbox  = draw.textbbox((0,0),text,font=font)
        tw,th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    except:
        tw,th = size*len(text)//2, size+4
    x = max((w-tw)//2, 10)
    y = max((h-th)//2, 5)
    for dx,dy,a in [(4,4,180),(3,3,140),(2,2,100),(-1,-1,60)]:
        draw.text((x+dx,y+dy), text, font=font, fill=(0,0,0,a))
    draw.text((x,y), text, font=font, fill=(*color,255))
    return np.array(img)

def make_vignette(w, h):
    ys,xs = np.mgrid[0:h,0:w]
    cx,cy = w/2, h/2
    dist  = np.clip(np.sqrt(((xs-cx)/cx)**2+((ys-cy)/cy)**2), 0, 1)
    alpha = (190*dist**2.2).astype(np.uint8)
    arr   = np.zeros((h,w,4), dtype=np.uint8)
    arr[:,:,3] = alpha
    return np.array(Image.fromarray(arr,"RGBA").filter(ImageFilter.GaussianBlur(35)))

def make_shimmer_frame(w, h, t, duration, color):
    img  = Image.new("RGBA",(w,h),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    random.seed(42)
    for i in range(45):
        phase      = i/45
        cycle      = (t/duration+phase)%1.0
        brightness = np.sin(cycle*np.pi*2)**2
        px   = int(w*(0.08+0.84*random.random()))
        py   = int(h*(0.04+0.72*random.random()))
        size = random.randint(2,8)
        alpha= int(180*brightness)
        if alpha>15:
            cr=min(255,color[0]+50); cg=min(255,color[1]+40); cb=min(255,color[2]+45)
            draw.ellipse([px-size,py-size,px+size,py+size], fill=(cr,cg,cb,alpha))
            if size>4:
                draw.line([px-size*2,py,px+size*2,py], fill=(255,220,225,alpha//2), width=1)
                draw.line([px,py-size*2,px,py+size*2], fill=(255,220,225,alpha//2), width=1)
    return np.array(img)

def make_shimmer_clip(w, h, duration, color):
    fps    = 24
    frames = int(duration*fps)
    imgs   = [make_shimmer_frame(w,h,i/fps,duration,color) for i in range(frames)]
    def mf(t): return imgs[min(int(t*fps),frames-1)][:,:,:3]
    def mm(t): return imgs[min(int(t*fps),frames-1)][:,:,3]/255.0
    c      = VideoClip(mf, duration=duration)
    c.mask = VideoClip(mm, ismask=True, duration=duration)
    return c

def apply_shot(clip, shot, seg_dur):
    def sf(get_frame, t):
        frame    = get_frame(t)
        fh,fw    = frame.shape[:2]
        progress = t/max(seg_dur,0.001)
        ease     = progress*progress*(3-2*progress)
        zoom     = shot["zoom_s"]+(shot["zoom_e"]-shot["zoom_s"])*ease
        pan_x    = shot.get("px",0)
        pan_y    = shot.get("py",0)+0.001*np.sin(progress*np.pi)
        nw = max(1,int(fw/zoom)); nh = max(1,int(fh/zoom))
        cx = int(fw/2+pan_x*fw); cy = int(fh/2+pan_y*fh)
        x1 = max(0,cx-nw//2); y1 = max(0,cy-nh//2)
        x2 = min(fw,x1+nw);   y2 = min(fh,y1+nh)
        if x2>fw: x1=fw-nw; x2=fw
        if y2>fh: y1=fh-nh; y2=fh
        x1=max(0,x1); y1=max(0,y1)
        cropped = frame[y1:y2,x1:x2]
        if cropped.size==0: return frame
        return np.array(Image.fromarray(cropped).resize((fw,fh),Image.LANCZOS))
    return clip.fl(sf)

def smart_crop(product_img):
    alpha = np.array(product_img)[:,:,3]
    rows  = np.any(alpha>5, axis=1)
    cols  = np.any(alpha>5, axis=0)
    if not rows.any() or not cols.any(): return product_img
    r0,r1 = np.where(rows)[0][[0,-1]]
    c0,c1 = np.where(cols)[0][[0,-1]]
    h,w   = alpha.shape
    px,py = int(w*0.06), int(h*0.06)
    return product_img.crop((max(0,c0-px),max(0,r0-py),min(w,c1+px),min(h,r1+py)))

def remove_bg(image_bytes):
    original = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    ow,oh    = original.size
    if max(ow,oh)>1500:
        ratio    = 1500/max(ow,oh)
        original = original.resize((int(ow*ratio),int(oh*ratio)),Image.LANCZOS)
    enhanced = ImageEnhance.Sharpness(original).enhance(2.0)
    enhanced = ImageEnhance.Contrast(enhanced).enhance(1.4)
    enhanced = ImageEnhance.Color(enhanced).enhance(1.2)
    buf = io.BytesIO()
    enhanced.save(buf, format="PNG")
    removed  = remove(buf.getvalue())
    mask     = Image.open(io.BytesIO(removed)).convert("RGBA")
    orig_full= Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if mask.size!=orig_full.size: mask=mask.resize(orig_full.size,Image.LANCZOS)
    _,_,_,alpha_ch = mask.split()
    alpha_smooth   = alpha_ch.filter(ImageFilter.GaussianBlur(0.4))
    prod = orig_full.convert("RGBA")
    prod.putalpha(alpha_smooth)
    return prod

def compose_on_bg(product_img, bg_img):
    product_img = smart_crop(product_img)
    pw,ph       = product_img.size
    aspect      = pw/ph
    bg          = bg_img.resize((TARGET_W,TARGET_H),Image.LANCZOS).convert("RGBA")
    if aspect>=2.0:    max_w,max_h = TARGET_W*0.94, TARGET_H*0.42
    elif aspect>=1.2:  max_w,max_h = TARGET_W*0.90, TARGET_H*0.48
    elif aspect>=0.75: max_w,max_h = TARGET_W*0.82, TARGET_H*0.55
    elif aspect>=0.45: max_w,max_h = TARGET_W*0.70, TARGET_H*0.60
    else:              max_w,max_h = TARGET_W*0.52, TARGET_H*0.65
    scale = max(min(max_w/pw,max_h/ph),(TARGET_W*0.38)/pw)
    while int(pw*scale)>int(TARGET_W*0.96): scale*=0.97
    while int(ph*scale)>int(TARGET_H*0.67): scale*=0.97
    nw,nh  = int(pw*scale), int(ph*scale)
    prod_r = product_img.resize((nw,nh),Image.LANCZOS)
    x      = (TARGET_W-nw)//2
    usable = int(TARGET_H*0.57)
    y      = max(int(TARGET_H*0.04),(usable-nh)//2)
    if nh>usable: y=int(TARGET_H*0.015)
    shadow = Image.new("RGBA",(TARGET_W,TARGET_H),(0,0,0,0))
    sd     = ImageDraw.Draw(shadow)
    sx,sy  = x+nw//2, y+nh+10
    sw     = int(nw*0.58)
    for r in range(38,0,-1):
        a = int(80*(1-r/38)**1.5)
        sd.ellipse([sx-sw//2-r,sy-r//5,sx+sw//2+r,sy+r//5],fill=(0,0,0,a))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    result = Image.alpha_composite(bg,shadow)
    result.paste(prod_r,(x,y),prod_r)
    return np.array(result.convert("RGB"))

def make_gradient_bg(w, h, bg_data):
    top,mid,bot,glow = bg_data["top"],bg_data["mid"],bg_data["bot"],bg_data["glow"]
    arr = np.zeros((h,w,3),dtype=np.uint8)
    for y in range(h):
        ratio = y/h
        if ratio<0.40:
            t2=ratio/0.40; r=int(top[0]+(mid[0]-top[0])*t2); g=int(top[1]+(mid[1]-top[1])*t2); b=int(top[2]+(mid[2]-top[2])*t2)
        elif ratio<0.70:
            t2=(ratio-0.40)/0.30; r=int(mid[0]+(bot[0]-mid[0])*t2); g=int(mid[1]+(bot[1]-mid[1])*t2); b=int(mid[2]+(bot[2]-mid[2])*t2)
        else: r,g,b=bot
        arr[y,:]=[r,g,b]
    img     = Image.fromarray(arr,"RGB")
    overlay = Image.new("RGBA",(w,h),(0,0,0,0))
    draw    = ImageDraw.Draw(overlay)
    cx,cy   = w//2, int(h*0.42)
    radius  = int(w*0.56)
    for i in range(radius,0,-6):
        ratio = i/radius
        alpha = int(105*(1-ratio)**1.7)
        draw.ellipse([cx-i,cy-i,cx+i,cy+i],fill=(min(255,glow[0]+30),min(255,glow[1]+20),min(255,glow[2]+25),alpha))
    img   = Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
    noise = np.random.randint(0,8,(h,w,3),dtype=np.uint8)
    return Image.fromarray(np.clip(np.array(img).astype(np.int16)+noise-4,0,255).astype(np.uint8),"RGB")

def generate_ai_bg(prompt):
    full    = f"{prompt}, product photography background, high quality, 8k, professional, no people, no text"
    headers = {"Authorization":f"Bearer {HF_TOKEN}","Content-Type":"application/json"}
    payload = {"inputs":full,"parameters":{"width":TARGET_W,"height":TARGET_H,"num_inference_steps":4,"guidance_scale":3.5}}
    for attempt in range(1,4):
        try:
            r = requests.post(FLUX_URL,headers=headers,json=payload,timeout=120)
            if r.status_code==200:
                bg = Image.open(io.BytesIO(r.content)).convert("RGB")
                return bg.resize((TARGET_W,TARGET_H),Image.LANCZOS)
            elif r.status_code==503: time.sleep(30)
            else:
                if attempt<3: time.sleep(15)
        except: time.sleep(10)
    return None

def join_brand_reel(video_bytes_list, output_path):
    from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
    import tempfile, os
    clips    = []
    tmp_files= []
    for vb in video_bytes_list:
        if vb is None: continue
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(vb); tmp.close()
        tmp_files.append(tmp.name)
        clip    = VideoFileClip(tmp.name).without_audio()
        scale   = min(TARGET_W/clip.w, TARGET_H/clip.h)
        resized = clip.resize(scale)
        bg      = ColorClip(size=(TARGET_W,TARGET_H),color=(8,8,8),duration=clip.duration)
        x       = (TARGET_W-resized.w)//2
        y       = (TARGET_H-resized.h)//2
        clips.append(CompositeVideoClip([bg,resized.set_position((x,y))]))
    if not clips: return None
    final = concatenate_videoclips(clips, method="compose")
    final = fadein(fadeout(final,0.5),0.5)
    final.write_videofile(str(output_path),fps=30,codec="libx264",bitrate="8000k",audio=False,threads=4,logger=None)
    for tf in tmp_files:
        try: os.unlink(tf)
        except: pass
    return str(output_path)

def build_video(base_arr, product_name, tagline, color, output_path):
    DURATION = 4.0
    seg_dur  = DURATION/len(SHOTS)
    vign     = make_vignette(TARGET_W,TARGET_H)
    wm_a     = text_arr("* BeautyReel AI *",TARGET_W,70,28,(190,145,162))
    name_a   = text_arr(product_name,TARGET_W,160,78,color,bold=True)
    tag_a    = text_arr(tagline,TARGET_W,85,34,(252,232,238))
    line_img = Image.new("RGBA",(TARGET_W,18),(0,0,0,0))
    ld       = ImageDraw.Draw(line_img)
    lx       = (TARGET_W-280)//2
    ld.rectangle([lx,6,lx+280,10],fill=(*color,215))
    line_a   = np.array(line_img)
    shot_clips = []
    for shot in SHOTS:
        sdur = seg_dur
        bc   = ImageClip(base_arr).set_duration(sdur)
        bc   = apply_shot(bc,shot,sdur)
        bc   = colorx(bc,shot["bright"])
        shimmer = make_shimmer_clip(TARGET_W,TARGET_H,sdur,color)
        bar_h   = 400
        bar_arr = np.zeros((bar_h,TARGET_W,4),dtype=np.uint8)
        for row in range(bar_h):
            ratio = row/bar_h
            alpha = int(210*np.sin(ratio*np.pi*0.85))
            bar_arr[row,:] = [30,15,20,alpha]
        bar_c    = ImageClip(bar_arr).set_duration(sdur).set_position((0,TARGET_H-bar_h))
        composed = CompositeVideoClip([
            bc, shimmer, ImageClip(vign).set_duration(sdur), bar_c,
            ImageClip(wm_a).set_duration(sdur).set_position(("center",58)),
            ImageClip(name_a).set_duration(sdur).set_position(("center",TARGET_H-340)),
            ImageClip(line_a).set_duration(sdur).set_position(("center",TARGET_H-200)),
            ImageClip(tag_a).set_duration(sdur).set_position(("center",TARGET_H-160)),
        ], size=(TARGET_W,TARGET_H))
        shot_clips.append(composed)
    final = concatenate_videoclips(shot_clips, method="compose")
    final = fadein(fadeout(final,0.5),0.5)
    final.write_videofile(str(output_path),fps=30,codec="libx264",bitrate="16000k",audio=False,threads=4,logger=None)

# =============================================================================
#  CUSTOM MODEL FUNCTION (UPDATED)
# =============================================================================

def run_custom_model(image_bytes):
    """
    Updated prediction function for the newly trained models (v3, v4, final).
    """
    try:
        import tensorflow as tf
    except ImportError:
        return None, 0.0, "TensorFlow not installed."

    # Define the paths for your updated models
    model_paths = [
        Path("beauty_model_final.keras"), # The most recently trained model
        Path("beauty_model_v4_pro.keras"),
        Path("beauty_model_v3.keras")
    ]

    model = None
    model_used = ""
    for mp in model_paths:
        if mp.exists():
            try:
                model = tf.keras.models.load_model(str(mp))
                model_used = mp.name
                break
            except Exception:
                continue

    if model is None:
        return None, 0.0, "❌ No model file (.keras) found. Please place the file in the project folder.", ""

    # 1. Image loading and resizing to 224x224
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img)
    
    # 2. Add Batch Dimension [1, 224, 224, 3]
    img_array = np.expand_dims(img_array, axis=0)

    # Note: If your model includes a 'preprocess_input' layer, 
    # you do not need to divide by 255.0 here.
    # However, if the model was trained on raw pixels, uncomment the line below:
    # img_array = img_array / 255.0 

    # 3. Perform Prediction
    predictions = model.predict(img_array, verbose=0)
    
    # 4. Apply Softmax for accurate confidence scores
    score = tf.nn.softmax(predictions[0]).numpy()

    # 5. Define Class Labels (must match the alphabetical order of your dataset folders)
    class_labels = [
        'Concealer', 
        'Lip Pencil', 
        'Lipstick', 
        'Powder'
    ]

    pred_idx   = np.argmax(score)
    label      = class_labels[pred_idx]
    confidence = float(score[pred_idx]) * 100
    all_preds  = {class_labels[i]: float(score[i])*100 for i in range(len(class_labels))}

    return label, confidence, all_preds, model_used

# =============================================================================
#  SESSION STATE
# =============================================================================
if "total_reels" not in st.session_state:
    st.session_state.total_reels = len(load_history())
if "total_products" not in st.session_state:
    hist = load_history()
    st.session_state.total_products = len(set(h["product"] for h in hist)) if hist else 0

# =============================================================================
#  SIDEBAR — Pure Python
# =============================================================================
with st.sidebar:
    st.title("💄 BeautyReel AI")
    st.caption("MAKEUP VIDEO STUDIO")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🎬 Studio", "🖼️ Gallery", "⚙️ Settings"],
        label_visibility="collapsed"
    )

    st.divider()
    st.metric("🎬 Reels Generated", st.session_state.total_reels)
    st.metric("💄 Products", st.session_state.total_products)
    st.metric("⚡ AI Credits", "∞")
    st.divider()


# =============================================================================
#  HEADER — Pure Python
# =============================================================================
st.title("💄 BeautyReel AI")
st.caption("✦  TRANSFORM YOUR PRODUCTS INTO VIRAL REELS  ✦  AIMAN & MAIRA")
st.divider()

# Stats row
c1, c2, c3 = st.columns(3)
c1.metric("🎬 Total Reels",    st.session_state.total_reels)
c2.metric("⚡ Credits Left",   "Unlimited")
c3.metric("💄 Total Products", st.session_state.total_products)
st.divider()

# =============================================================================
#  SETTINGS PAGE
# =============================================================================
if page == "⚙️ Settings":
    st.subheader("⚙️ Settings")

    with st.expander("🔑 HuggingFace Token", expanded=True):
        new_token = st.text_input("HF Token", value=HF_TOKEN, type="password")
        if st.button("💾 Save Token"):
            HF_TOKEN = new_token
            st.success("✓ Token updated!")

    with st.expander("📁 Output Folder"):
        st.code(str(OUTPUT_DIR.resolve()))
        st.info(f"Videos are saved here: {OUTPUT_DIR}")

    with st.expander("ℹ️ About"):
        st.write("**BeautyReel AI** — AI-Powered Makeup Video Generator")
        st.write("**Models:** FLUX.1-schnell · U2Net (rembg) · moviepy")
        st.write("**Students:** Aiman (AI-449865) · Maira (AI-451658)")
        st.write("**Instructor:** Javeria Hassan")


# =============================================================================
#  GALLERY PAGE
# =============================================================================
elif page == "🖼️ Gallery":
    st.subheader("🖼️ Your Generated Reels")

    history = load_history()
    if not history:
        st.info("🎬 No reels yet — go to Studio to generate your first reel!")
    else:
        for item in history:
            video_path = Path(item["path"])
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                st.write(f"**🎬 {item['product']}**")
                st.caption(f"{item['mode']} · {item['time']}")
            with col2:
                if video_path.exists():
                    with open(video_path,"rb") as f:
                        st.download_button(
                            "⬇️ Download",
                            data      = f.read(),
                            file_name = video_path.name,
                            mime      = "video/mp4",
                            key       = f"gal_{item['time']}"
                        )
            with col3:
                st.caption("✓ Ready" if video_path.exists() else "✗ Deleted")
            st.divider()

# =============================================================================
#  STUDIO PAGE
# =============================================================================
else:
    left_col, right_col = st.columns([1,1], gap="large")

    with left_col:

        # Step 0 — Model Selection (Miss's requirement)
        st.subheader("⓪ Select Processing Mode")
        model_mode = st.radio(
            "Processing Mode",
            [
                "🤖 Custom Model — My Trained Keras Model",
                "🌐 AI API — FLUX.1 + rembg (External API)",
            ],
            label_visibility="collapsed"
        )
        if "Custom Model" in model_mode:
            st.info(
                "**Custom Model Mode** — Uses your locally trained `.keras` model "
                "to classify and analyze the product image. "
                "No internet required. Place `beauty_model_pro.keras` in your project folder."
            )
        else:
            st.info(
                "**AI API Mode** — Uses FLUX.1 (HuggingFace) to generate "
                "AI backgrounds and rembg to remove product background. "
                "Internet + HF Token required."
            )
        st.divider()

        # Step 1 — Upload
        st.subheader("① Upload Product Image")

        upload_method = st.radio(
            "Select Image Method",
            ["📁 Browse & Upload", "📂 Enter Image Path"],
            horizontal=True,
            label_visibility="collapsed"
        )

        uploaded   = None
        image_from_path = None

        if upload_method == "📁 Browse & Upload":
            uploaded = st.file_uploader(
                "Any product, any angle",
                type=["jpg","jpeg","png","webp"],
                key="uploader"
            )
            if uploaded:
                st.image(Image.open(uploaded), use_column_width=True)
                img_size = Image.open(uploaded).size
                st.success(f"✓ Image ready — {img_size[0]}×{img_size[1]}px")

        else:  # Enter Image Path
            image_path_input = st.text_input(
                "Image Path",
                placeholder=r"e.g. images_datasets\lipstick_image_dataset\lipstick.jpg"
            )
            if image_path_input:
                path_obj = Path(image_path_input.strip().strip('"'))
                if path_obj.exists():
                    image_from_path = path_obj
                    st.image(str(path_obj), use_column_width=True)
                    st.success(f"✓ Image found — {path_obj.name}")
                else:
                    st.error(f"❌ File not found: {image_path_input}")

        st.divider()

        # Step 2 — Product Details
        st.subheader("③ Product Details")
        product_name = st.text_input("Product Name", placeholder="e.g. LIPSTICK")
        tagline      = st.text_input("Tagline", placeholder="e.g. Bold. Glamorous. Unstoppable")

        st.divider()

        # Step 3 — Select Style
        st.subheader("④ Select Style")
        mode = st.selectbox(
            "Video Mode",
            [
                "🎬 Cinematic — Simple (No API)",
                "🎨 Dynamic — AI Background (FLUX.1)",
                "🌈 Subtle — Gradient Background",
                "🔗 Brand Reel — Join 4 Product Videos",
            ]
        )

        color = (183, 110, 121)

        if "Cinematic" in mode:
            st.info("Cinematic motion + text overlays on your original image. Fast & no API needed.")

        elif "Dynamic" in mode:
            st.write("**Select Vibe:**")
            vibe = st.radio("Vibe", list(VIBES.keys()), horizontal=True, label_visibility="collapsed")
            custom_prompt = st.text_input(
                "Custom Prompt (optional)",
                placeholder="e.g. deep burgundy velvet, dramatic lighting"
            )
            color = VIBES[vibe]["color"]

        elif "Subtle" in mode:
            bg_choice = st.selectbox("Background Style", list(GRADIENT_BGS.keys()))
            color = GRADIENT_BGS[bg_choice]["glow"]

        elif "Brand Reel" in mode:
            st.info("Upload 2-4 product videos to join into one brand reel (~16 seconds)")
            v1 = st.file_uploader("Video 1 — e.g. Powder",    type=["mp4"], key="v1")
            v2 = st.file_uploader("Video 2 — e.g. Lip Pencil",type=["mp4"], key="v2")
            v3 = st.file_uploader("Video 3 — e.g. Concealer", type=["mp4"], key="v3")
            v4 = st.file_uploader("Video 4 — e.g. Lipstick",  type=["mp4"], key="v4")

        st.divider()
        generate = st.button("✦  Generate My Reel  ✦", use_container_width=True, type="primary")

    # ── RIGHT COLUMN — Preview ─────────────────────────────────────────────
    with right_col:
        st.subheader("⑤ Result Preview")

        if not generate:
            st.info("📱 Your result will appear here.\n\nSelect mode → Upload image → Fill details → Click Generate")

        else:
            if not uploaded and not image_from_path:
                st.error("⚠️ Please upload a product image or enter image path!")
            elif "Brand Reel" not in mode and not product_name:
                st.error("⚠️ Please enter product name!")
            elif "Brand Reel" not in mode and not tagline:
                st.error("⚠️ Please enter tagline!")
            else:
                # Get image bytes
                if uploaded:
                    image_bytes = uploaded.getvalue()
                elif image_from_path:
                    image_bytes = image_from_path.read_bytes()
                else:
                    image_bytes = None

                safe_name = (product_name or "brand").lower().replace(" ","_")
                out_path  = None

                # ── CUSTOM MODEL MODE ──────────────────────────────────────
                if "Custom Model" in model_mode:
                    st.subheader("🤖 Custom Model Result")
                    progress = st.progress(0, text="Loading custom model...")

                    if image_bytes is None:
                        st.error("Please provide an image first.")
                    else:
                        try:
                            progress.progress(30, text="🔍 Analyzing image with custom model...")
                            result = run_custom_model(image_bytes)

                            if result[0] is None:
                                # Error message returned
                                st.error(result[2])
                                progress.progress(0)
                            else:
                                label, confidence, all_preds, model_used = result
                                progress.progress(100, text="✅ Analysis complete!")

                                st.success(f"✅ Analysis Complete!")
                                st.image(Image.open(io.BytesIO(image_bytes)), use_column_width=True)

                                st.divider()
                                st.metric("🏷️ Detected Product", label)
                                st.metric("📊 Confidence", f"{confidence:.1f}%")
                                st.caption(f"Model used: `{model_used}`")

                                st.divider()
                                st.write("**All Class Predictions:**")
                                for cls, prob in sorted(all_preds.items(), key=lambda x: -x[1]):
                                    st.progress(int(prob), text=f"{cls}: {prob:.1f}%")

                                st.divider()
                                st.info(
                                    f"💡 **Custom Model says:** This is a **{label}** "
                                    f"with **{confidence:.1f}% confidence**.\n\n"
                                    f"Switch to **AI API Mode** to generate a professional "
                                    f"video reel for this product!"
                                )

                        except Exception as e:
                            st.error(f"Model error: {e}")
                            progress.progress(0)

                # ── AI API MODE ────────────────────────────────────────────
                else:
                    progress = st.progress(0, text="Starting...")

                    try:
                        if "Cinematic" in mode:
                            progress.progress(20, text="🖼️ Preparing image...")
                            img      = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                            base_arr = np.array(img.resize((TARGET_W,TARGET_H),Image.LANCZOS))
                            progress.progress(50, text="🎬 Building cinematic reel...")
                            out_path = OUTPUT_DIR / f"{safe_name}_cinematic.mp4"
                            build_video(base_arr, product_name.upper(), tagline, color, out_path)

                        elif "Dynamic" in mode:
                            final_prompt = custom_prompt.strip() if custom_prompt.strip() else VIBES[vibe]["prompt"]
                            color        = VIBES[vibe]["color"]
                            progress.progress(15, text="🎨 Generating AI background...")
                            bg_img = generate_ai_bg(final_prompt)
                            if bg_img is None:
                                st.error("Background generation failed. Check token/internet.")
                                st.stop()
                            progress.progress(35, text="✂️ Removing product background...")
                            product_img  = remove_bg(image_bytes)
                            progress.progress(55, text="🖼️ Composing scene...")
                            composed_arr = compose_on_bg(product_img, bg_img)
                            progress.progress(70, text="🎬 Building dynamic reel...")
                            safe_vibe = vibe.split()[-1].lower()
                            out_path  = OUTPUT_DIR / f"{safe_name}_dynamic_{safe_vibe}.mp4"
                            build_video(composed_arr, product_name.upper(), tagline, color, out_path)

                        elif "Subtle" in mode:
                            progress.progress(20, text="✂️ Removing product background...")
                            product_img  = remove_bg(image_bytes)
                            progress.progress(45, text="🎨 Applying gradient background...")
                            bg_data      = GRADIENT_BGS[bg_choice]
                            bg_pil       = make_gradient_bg(TARGET_W, TARGET_H, bg_data)
                            composed_arr = compose_on_bg(product_img, bg_pil)
                            color        = bg_data["glow"]
                            progress.progress(65, text="🎬 Building reel...")
                            safe_bg  = bg_choice.lower().replace(" ","_")
                            out_path = OUTPUT_DIR / f"{safe_name}_subtle_{safe_bg}.mp4"
                            build_video(composed_arr, product_name.upper(), tagline, color, out_path)

                        elif "Brand Reel" in mode:
                            uploaded_videos = [
                                v1.getvalue() if v1 else None,
                                v2.getvalue() if v2 else None,
                                v3.getvalue() if v3 else None,
                                v4.getvalue() if v4 else None,
                            ]
                            filled = [v for v in uploaded_videos if v is not None]
                            if len(filled) < 2:
                                st.error("⚠️ Please upload at least 2 product videos!")
                                st.stop()
                            progress.progress(30, text=f"🔗 Joining {len(filled)} videos...")
                            out_path = OUTPUT_DIR / "BeautyReel_Brand_Final.mp4"
                            result   = join_brand_reel(uploaded_videos, out_path)
                            if result is None:
                                st.error("Brand reel joining failed.")
                                st.stop()
                            product_name = product_name or "BRAND REEL"

                        if out_path:
                            progress.progress(100, text="✅ Done!")
                            st.success("✅ Your reel is ready!")

                            save_history(product_name, mode.split("—")[0].strip(), out_path)
                            st.session_state.total_reels += 1
                            st.session_state.total_products = len(set(h["product"] for h in load_history()))

                            with open(out_path,"rb") as f:
                                video_bytes = f.read()

                            st.video(video_bytes)
                            st.download_button(
                                "⬇️  Save to Device",
                                data      = video_bytes,
                                file_name = out_path.name,
                                mime      = "video/mp4",
                                use_container_width = True
                            )

                    except Exception as e:
                        st.error(f"Error: {e}")
                        progress.progress(0)

    # History at bottom of Studio
    st.divider()
    history = load_history()
    if history:
        st.subheader("🕐 Recent Reels")
        hist_cols = st.columns(min(len(history), 5))
        for i, (col, item) in enumerate(zip(hist_cols, history)):
            with col:
                video_path = Path(item["path"])
                st.write(f"**{item['product']}**")
                st.caption(f"{item['mode']}")
                st.caption(f"🕐 {item['time']}")
                if video_path.exists():
                    with open(video_path,"rb") as f:
                        st.download_button(
                            "⬇️",
                            data      = f.read(),
                            file_name = video_path.name,
                            mime      = "video/mp4",
                            key       = f"h{i}"
                        )

# Footer
st.divider()
st.caption("BEAUTYREEL AI")

