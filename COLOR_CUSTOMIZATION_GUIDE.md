# 🎨 TagAlign AI - Complete Color Customization Guide

This guide shows you **exactly** where to change colors in your application. Each section includes the file location, line numbers, and what each color controls.

---

## 📁 File Overview

Your app has 3 main files that control colors:
1. **app.py** - Home page and Config page colors
2. **dashboard.py** - Dashboard page layout and styling
3. **stats.py** - Chart colors and visual analytics

---

## 🏠 HOME & CONFIG PAGES (app.py)

### Background Gradient
**Location:** `app.py`, lines 95-101

```css
.stApp {
    background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 50%, #fdba74 100%);
}
```

**What it controls:** The main background color of Home and Config pages

**How to change:**
- `#fef3c7` = Top-left corner color (currently light cream)
- `#fed7aa` = Middle color (currently light orange)
- `#fdba74` = Bottom-right color (currently medium orange)

**Example alternatives:**
- Pink theme: `#fce7f3 0%, #fbcfe8 50%, #f9a8d4 100%`
- Blue theme: `#dbeafe 0%, #a5ccfcff 50%, #93c5fd 100%`
- Green theme: `#d1fae5 0%, #a7f3d0 50%, #6ee7b7 100%`

---

### Sidebar Colors
**Location:** `app.py`, lines 107-111

```css
[data-testid="stSidebar"] {
    background: rgba(120, 53, 15, 0.85) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid #fb923c;
}
```

**What it controls:** The left navigation sidebar

**How to change:**
- `rgba(120, 53, 15, 0.85)` = Background color (currently brown with 85% opacity)
  - Format: `rgba(RED, GREEN, BLUE, OPACITY)`
  - Example pink: `rgba(219, 39, 119, 0.85)`
  - Example blue: `rgba(37, 99, 235, 0.85)`
- `#fb923c` = Border color (currently orange)

---

### Hero Title (Big "TagAlign AI" text)
**Location:** `app.py`, lines 112-117

```css
.hero-title {
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

**What it controls:** The gradient text effect on the main title

**How to change:**
- `#ffffff` = Start color (currently white)
- `#e2e8f0` = Middle color (currently light gray)
- `#38bdf8` = End color (currently light blue)

**Example alternatives:**
- Orange gradient: `#fb923c 0%, #fdba74 50%, #fef3c7 100%`
- Pink gradient: `#ec4899 0%, #f9a8d4 50%, #fce7f3 100%`

---

### Subtitle Text
**Location:** `app.py`, lines 118-122

```css
.hero-subtitle {
    color: #fb923c !important;
}
```

**What it controls:** The small text under the main title

**How to change:** Replace `#fb923c` with any color code

---

### All Text Colors
**Location:** `app.py`, lines 123-125

```css
.floating-title { color: #78350f !important; }
.floating-desc { color: #78350f !important; }
```

**What it controls:** Regular text throughout Home and Config pages

**How to change:** Replace `#78350f` (dark brown) with your preferred text color
- For dark text: `#000000` (black), `#1f2937` (dark gray)
- For colored text: `#db2777` (pink), `#2563eb` (blue)

---

### Highlight Colors (Emphasized Words)
**Location:** `app.py`, lines 126-127

```css
.highlight-purple { color: #fb923c !important; }
.highlight-pink { color: #ea580c !important; }
```

**What it controls:** Colored words in descriptions (like "semantic footprints")

---

### Buttons
**Location:** `app.py`, lines 142-148

```css
div.stButton > button:first-child {
    background: linear-gradient(135deg, #fb923c 0%, #fdba74 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 0px #ea580c, 0 15px 25px rgba(251, 146, 60, 0.3);
}
```

**What it controls:** All buttons (Proceed, Run Analysis, etc.)

**How to change:**
- `#fb923c` and `#fdba74` = Button gradient colors
- `#ffffff` = Text color on button
- `#ea580c` = Shadow color under button

---

### Input Boxes (Hashtags & URLs)
**Location:** `app.py`, lines 135-141

```css
.cube-item {
    background: rgba(255,255,255,0.8);
    border: 1.5px solid rgba(251, 146, 60, 0.5);
}
.cube-item-text { color: #78350f !important; }
```

**What it controls:** The boxes showing hashtags and URLs

**How to change:**
- `rgba(255,255,255,0.8)` = Box background (currently white with 80% opacity)
- `rgba(251, 146, 60, 0.5)` = Border color (currently orange with 50% opacity)
- `#78350f` = Text color inside boxes

---

### Floating Charts (Animated decorations)
**Location:** `app.py`, lines 156-159

```css
.floating-chart-3d {
    background: rgba(120, 53, 15, 0.6);
    border: 1px solid #fb923c;
}
.chart-bar { background: linear-gradient(to top, #fb923c, #fdba74); }
```

**What it controls:** The animated chart decorations on the home page

---

## 📊 DASHBOARD PAGE (dashboard.py)

### Dashboard Background
**Location:** `dashboard.py`, lines 127-130

```css
.stApp {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%);
}
```

**What it controls:** Background of the analytics dashboard

**How to change:** Same as Home page background (see above)

---

### KPI Cards (Metric boxes at top)
**Location:** `dashboard.py`, lines 131-137

```css
.stMetric {
    background: rgba(255, 255, 255, 0.98);
    border: 2px solid rgba(251, 146, 60, 0.3);
    box-shadow: 0 4px 12px rgba(251, 146, 60, 0.1);
}
```

**What it controls:** The 5 metric cards at the top (Total Posts, Brand Alignment, etc.)

**How to change:**
- `rgba(255, 255, 255, 0.98)` = Card background (currently white)
- `rgba(251, 146, 60, 0.3)` = Border color (currently orange with 30% opacity)
- `rgba(251, 146, 60, 0.1)` = Shadow color

---

### Dashboard Text Colors
**Location:** `dashboard.py`, lines 138-148

```css
.stMetric label {
    color: #78350f !important;
}
h1, h2, h3, h4 {
    color: #78350f !important;
}
.stMarkdown {
    color: #78350f !important;
}
```

**What it controls:** All text in the dashboard

**How to change:** Replace `#78350f` with your preferred text color

---

### Alert Boxes (Threat warnings)
**Location:** `dashboard.py`, lines 149-151

```css
.stAlert {
    background: rgba(255, 255, 255, 0.98);
}
```

**What it controls:** Red and yellow warning boxes

**Note:** The red/yellow colors are controlled by Streamlit's `st.error()` and `st.warning()` functions and cannot be easily changed via CSS.

---

## 📈 CHARTS & VISUALIZATIONS (stats.py)

### Main Color Palette
**Location:** `stats.py`, lines 6-13

```python
COLORS = {
    'orange': '#fb923c',           # Main orange for hijacked
    'light_orange': '#fdba74',     # Light orange for aligned
    'dark_text': '#422006',        # Dark brown text (bold and readable)
    'light_bg': 'rgba(255, 255, 255, 1)',      # Pure white background
    'chart_bg': 'rgba(254, 252, 232, 0.9)',    # Very light cream for charts
    'white': '#ffffff'
}
```

**What it controls:** ALL chart colors throughout the dashboard

**How to change:** This is the MASTER color palette. Change these values to update all charts at once!

**Example pink/blue theme:**
```python
COLORS = {
    'orange': '#ec4899',           # Pink for hijacked
    'light_orange': '#93c5fd',     # Light blue for aligned
    'dark_text': '#1e293b',        # Dark slate text
    'light_bg': 'rgba(255, 255, 255, 1)',
    'chart_bg': 'rgba(241, 245, 249, 0.9)',
    'white': '#ffffff'
}
```

---

### Pie Chart Colors
**Location:** `stats.py`, lines 127-129

```python
colors = [COLORS['light_orange'], COLORS['orange']]
```

**What it controls:** The two slices in the Brand Alignment pie chart
- First color = Aligned posts
- Second color = Hijacked posts

---

### Heatmap Colors
**Location:** `stats.py`, lines 163-171

```python
if rate >= 50:
    colors.append('#ea580c')  # Dark orange
elif rate >= 30:
    colors.append('#fb923c')  # Medium orange
else:
    colors.append('#fdba74')  # Light orange
```

**What it controls:** The horizontal bars in the Campaign Integrity Heatmap

**How to change:** Replace the color codes:
- `#ea580c` = High risk color (currently dark orange)
- `#fb923c` = Medium risk color (currently medium orange)
- `#fdba74` = Low risk color (currently light orange)

---

### Bar Chart Colors
**Location:** `stats.py`, lines 221-223 and 228-230

```python
marker_color=COLORS['light_orange'],  # Aligned posts
marker_color=COLORS['orange'],        # Hijacked posts
```

**What it controls:** The Engagement Quality Analysis bar chart

---

### Chart Text Boldness
**Location:** Throughout `stats.py`, look for `weight=900` or `weight=800`

**Examples:**
- Line 132: `textfont=dict(size=16, color='#422006', family='Inter', weight=900)`
- Line 180: `textfont=dict(size=15, color='white', family='Inter', weight=900)`

**How to change:**
- `weight=900` = Extra bold
- `weight=800` = Bold
- `weight=700` = Semi-bold
- `weight=600` = Medium
- `weight=400` = Normal

---

## 🎯 Quick Color Change Recipes

### Recipe 1: Pink & Blue Theme
1. In `stats.py` line 7-8, change:
   ```python
   'orange': '#ec4899',        # Pink
   'light_orange': '#93c5fd',  # Light blue
   ```

2. In `app.py` line 96, change:
   ```css
   background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 50%, #f9a8d4 100%);
   ```

3. In `dashboard.py` line 128, change:
   ```css
   background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #bfdbfe 100%);
   ```

---

### Recipe 2: Green & Teal Theme
1. In `stats.py` line 7-8, change:
   ```python
   'orange': '#14b8a6',        # Teal
   'light_orange': '#6ee7b7',  # Light green
   ```

2. In `app.py` line 96, change:
   ```css
   background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 50%, #6ee7b7 100%);
   ```

---

### Recipe 3: Purple & Violet Theme
1. In `stats.py` line 7-8, change:
   ```python
   'orange': '#a855f7',        # Purple
   'light_orange': '#c4b5fd',  # Light violet
   ```

2. In `app.py` line 96, change:
   ```css
   background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 50%, #d8b4fe 100%);
   ```

---

## 🔍 Color Code Format Guide

### Hex Colors (most common)
- Format: `#RRGGBB`
- Example: `#fb923c` (orange)
- Red: `#ef4444`, Blue: `#3b82f6`, Green: `#22c55e`, Pink: `#ec4899`

### RGBA Colors (with transparency)
- Format: `rgba(RED, GREEN, BLUE, OPACITY)`
- RED, GREEN, BLUE: 0-255
- OPACITY: 0.0 (invisible) to 1.0 (solid)
- Example: `rgba(251, 146, 60, 0.5)` = 50% transparent orange

---

## 🛠️ How to Test Your Changes

1. **Save the file** after making changes
2. **Refresh your browser** (F5 or Ctrl+R)
3. If colors don't update, do a **hard refresh**:
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

---

## 💡 Pro Tips

1. **Start with stats.py** - The COLORS dictionary controls most chart colors
2. **Use consistent colors** - Pick 2-3 main colors and stick with them
3. **Test contrast** - Make sure text is readable on backgrounds
4. **Use opacity** - `rgba()` colors with opacity (0.5-0.9) look modern
5. **Match themes** - Keep Home, Config, and Dashboard colors similar

---

## 🎨 Recommended Color Palettes

### Warm (Current)
- Background: Light cream/orange
- Primary: Orange `#fb923c`
- Secondary: Light orange `#fdba74`
- Text: Dark brown `#78350f`

### Cool
- Background: Light blue
- Primary: Blue `#3b82f6`
- Secondary: Light blue `#93c5fd`
- Text: Dark slate `#1e293b`

### Vibrant
- Background: Light pink
- Primary: Hot pink `#ec4899`
- Secondary: Purple `#a855f7`
- Text: Dark purple `#581c87`

### Professional
- Background: Light gray
- Primary: Dark blue `#1e40af`
- Secondary: Teal `#14b8a6`
- Text: Black `#000000`

---

## 📞 Need Help?

If you want to change a specific element and can't find it in this guide:
1. Look for the element's text in the code (use Ctrl+F)
2. Check nearby lines for `color:`, `background:`, or `marker_color=`
3. The color will be either a hex code (`#fb923c`) or rgba value

---

**Last Updated:** May 28, 2026
**Your Current Theme:** Orange/Light Blue with Dark Brown Text
