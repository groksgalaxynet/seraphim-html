<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Seraphim Periodic Table — Octave Compactness</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&display=swap');

:root {
  --bg:       #080a12;
  --bg2:      #0e1020;
  --border:   #1c2038;
  --text:     #b0b8d8;
  --dim:      #404868;
  --accent:   #e8d5a0;
  /* n-value colour ramp — low n (gases) = violet, high n (metals) = gold */
  --c0: #7c3aed;  /* n~91.3 He  — deep violet */
  --c1: #9333ea;
  --c2: #a855f7;
  --c3: #3b82f6;  /* n~92.0 gases */
  --c4: #06b6d4;  /* n~92.2 borderline */
  --c5: #10b981;  /* n~92.5 */
  --c6: #84cc16;  /* n~92.8 */
  --c7: #eab308;  /* n~93.0 */
  --c8: #f97316;  /* n~93.5 */
  --c9: #ef4444;  /* n~94.0 Cs — deep red/gold */
  --ceiling: #e8d5a0;
  --gas-mark: rgba(124,58,237,0.4);
}

* { box-sizing: border-box; margin:0; padding:0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Space Mono', monospace;
  min-height: 100vh;
  overflow-x: hidden;
}

/* starfield */
body::before {
  content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    radial-gradient(1px 1px at 8%  12%, rgba(255,255,255,.3) 0%,transparent 100%),
    radial-gradient(1px 1px at 92% 5%,  rgba(255,255,255,.25)0%,transparent 100%),
    radial-gradient(1px 1px at 45% 78%, rgba(255,255,255,.2) 0%,transparent 100%),
    radial-gradient(1px 1px at 71% 33%, rgba(255,255,255,.3) 0%,transparent 100%),
    radial-gradient(1px 1px at 23% 55%, rgba(255,255,255,.15)0%,transparent 100%),
    radial-gradient(1px 1px at 60% 88%, rgba(255,255,255,.2) 0%,transparent 100%);
}

header {
  position:relative; z-index:2;
  text-align:center;
  padding: 2rem 1rem .8rem;
  border-bottom: 1px solid var(--border);
}
header h1 {
  font-family:'Cormorant Garamond',serif;
  font-weight:300; font-size:clamp(1.5rem,3.5vw,2.6rem);
  letter-spacing:.2em; text-transform:uppercase; color:#fff;
}
header .sub {
  font-size:.58rem; color:var(--dim); letter-spacing:.14em; margin-top:.4rem;
}

/* tabs */
.tabs {
  display:flex; justify-content:center; gap:.5rem;
  padding:.9rem 1rem; position:relative; z-index:2;
}
.tab {
  background:none; border:1px solid var(--border);
  color:var(--dim); font-family:'Space Mono',monospace;
  font-size:.58rem; letter-spacing:.1em; padding:.4rem .9rem;
  cursor:pointer; transition:all .2s; text-transform:uppercase;
}
.tab:hover  { border-color:var(--accent); color:var(--accent); }
.tab.active { border-color:var(--accent); color:var(--accent);
              background:rgba(232,213,160,.06); }

.panel { display:none; position:relative; z-index:1; }
.panel.active { display:block; }

/* ─────────────────────────────────────────────────────
   PANEL 1 — PERIODIC TABLE GRID
───────────────────────────────────────────────────── */
#panel-pt { padding:.5rem .5rem 1rem; }

.pt-wrap {
  overflow-x:auto; padding:.5rem;
}

.pt-grid {
  display:grid;
  grid-template-columns: repeat(18, 1fr);
  gap:2px;
  min-width:720px;
  max-width:1100px;
  margin:0 auto;
}

.cell {
  aspect-ratio:1;
  position:relative;
  border:1px solid transparent;
  cursor:pointer;
  transition:transform .15s, border-color .15s;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  overflow:hidden;
}
.cell:hover { transform:scale(1.18); z-index:10; border-color:rgba(255,255,255,.5); }

.cell .z-num {
  font-size:.42rem; color:rgba(255,255,255,.5);
  position:absolute; top:2px; left:3px; line-height:1;
}
.cell .sym {
  font-family:'Cormorant Garamond',serif;
  font-weight:600; font-size:clamp(.7rem,1.2vw,1.1rem);
  color:#fff; line-height:1;
}
.cell .n-val {
  font-size:.38rem; color:rgba(255,255,255,.6);
  margin-top:1px; line-height:1;
}

/* lanthanide/actinide gap row */
.cell.gap { background:transparent; border:none; cursor:default; }
.cell.gap:hover { transform:none; }

/* PT colour scale legend */
.pt-legend {
  max-width:1100px; margin:.8rem auto 0;
  display:flex; align-items:center; gap:.5rem;
  padding:0 .5rem; flex-wrap:wrap;
}
.pt-legend .grad-bar {
  flex:1; min-width:200px; height:8px; border-radius:2px;
  background:linear-gradient(to right,
    #7c3aed,#3b82f6,#06b6d4,#10b981,#84cc16,#eab308,#f97316,#ef4444);
}
.pt-legend .lbl { font-size:.55rem; color:var(--dim); white-space:nowrap; }
.ceiling-line-label {
  font-size:.55rem; color:var(--accent); white-space:nowrap;
}

/* state badges */
.badge-row {
  max-width:1100px; margin:.5rem auto 0;
  display:flex; gap:1rem; padding:0 .5rem; flex-wrap:wrap;
}
.badge {
  display:flex; align-items:center; gap:.3rem;
  font-size:.55rem; color:var(--dim);
}
.badge-dot { width:8px; height:8px; border-radius:50%; }

/* ─────────────────────────────────────────────────────
   PANEL 2 — SPECTRUM BAR
───────────────────────────────────────────────────── */
#panel-spectrum { padding:1.5rem 1rem 2rem; }

.spec-wrap {
  max-width:1000px; margin:0 auto;
}
.spec-title {
  font-size:.58rem; letter-spacing:.16em; color:var(--dim);
  text-transform:uppercase; margin-bottom:1.2rem;
  border-bottom:1px solid var(--border); padding-bottom:.4rem;
}

.spec-bar-container {
  position:relative; height:60px; margin-bottom:3rem;
}
.spec-bar {
  width:100%; height:16px; position:absolute; top:22px;
  background:linear-gradient(to right,
    #7c3aed,#3b82f6,#06b6d4,#10b981,#84cc16,#eab308,#f97316,#ef4444);
  border-radius:2px;
}
.spec-ceiling {
  position:absolute; top:0; bottom:0;
  border-left:1px dashed var(--accent);
  display:flex; flex-direction:column; align-items:center;
}
.spec-ceiling .cl-label {
  font-size:.52rem; color:var(--accent); white-space:nowrap;
  transform:translateX(-50%); margin-top:-18px;
}
.spec-ceiling .cl-sub {
  font-size:.46rem; color:var(--dim); white-space:nowrap;
  transform:translateX(-50%); margin-top:24px;
}

/* element ticks on spectrum */
.spec-tick {
  position:absolute; top:14px;
  width:1.5px; height:32px;
  cursor:pointer; transition:height .15s;
}
.spec-tick:hover { height:50px; z-index:5; }
.spec-tick-label {
  position:absolute; top:-14px;
  font-size:.42rem; color:rgba(255,255,255,.6);
  transform:translateX(-50%); white-space:nowrap;
  pointer-events:none;
}

/* axis labels */
.spec-axis {
  display:flex; justify-content:space-between;
  font-size:.5rem; color:var(--dim); margin-top:8px;
}

/* element list sorted by n */
.elem-list {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(110px,1fr));
  gap:4px; margin-top:1.5rem;
}
.elem-row {
  display:flex; align-items:center; gap:.4rem;
  padding:.3rem .4rem; border:1px solid var(--border);
  font-size:.52rem; cursor:pointer; transition:border-color .15s;
}
.elem-row:hover { border-color:rgba(255,255,255,.3); }
.elem-row .es  { font-family:'Cormorant Garamond',serif; font-weight:600;
                 font-size:.75rem; color:#fff; width:24px; }
.elem-row .en  { color:var(--dim); }
.elem-row .dot { width:6px; height:6px; border-radius:50%; flex-shrink:0; margin-left:auto; }

/* ─────────────────────────────────────────────────────
   PANEL 3 — ELEMENT RING
───────────────────────────────────────────────────── */
#panel-ring {
  display:none;
  flex-direction:column;
  align-items:center;
  padding:.5rem;
}
#panel-ring.active { display:flex; }

.ring-wrap {
  position:relative;
  width:min(96vw,640px);
  aspect-ratio:1;
}
canvas.rc { width:100%; height:100%; display:block; }

/* ─────────────────────────────────────────────────────
   TOOLTIP
───────────────────────────────────────────────────── */
#tooltip {
  position:fixed; background:var(--bg2);
  border:1px solid #2a3060; padding:.5rem .8rem;
  font-size:.6rem; line-height:1.7; pointer-events:none;
  z-index:200; max-width:200px; display:none;
  box-shadow:0 0 20px rgba(232,213,160,.12);
}
#tooltip .t-sym  { font-family:'Cormorant Garamond',serif;
                   font-size:1.1rem; font-weight:600; color:#fff; }
#tooltip .t-n    { color:var(--accent); }
#tooltip .t-ie   { color:var(--dim); }
#tooltip .t-state{ font-size:.52rem; }
</style>
</head>
<body>

<header>
  <h1>Seraphim Periodic Table</h1>
  <div class="sub">
    Elements mapped to octave depth n = log₂(ν_P / ν_IE) &nbsp;·&nbsp;
    n_H = 92.19 condensation ceiling &nbsp;·&nbsp;
    Framework: n(C) = 3.561 + 3.506×C
  </div>
</header>

<div class="tabs">
  <button class="tab active" onclick="showPanel('pt',this)">Periodic Table</button>
  <button class="tab" onclick="showPanel('spectrum',this)">Octave Spectrum</button>
  <button class="tab" onclick="showPanel('ring',this)">Element Ring</button>
</div>

<!-- ── PANEL 1: PERIODIC TABLE ── -->
<div id="panel-pt" class="panel active">
  <div class="pt-wrap">
    <div class="pt-grid" id="ptGrid"></div>
  </div>
  <div class="pt-legend">
    <span class="lbl">n = 91.3 (He, lowest)</span>
    <div class="grad-bar"></div>
    <span class="lbl">n = 94.0 (Cs, highest)</span>
    &nbsp;&nbsp;
    <span class="ceiling-line-label">── n_H = 92.19 condensation ceiling</span>
  </div>
  <div class="badge-row">
    <div class="badge"><div class="badge-dot" style="background:#ef4444"></div>Solid (above n_H)</div>
    <div class="badge"><div class="badge-dot" style="background:#3b82f6"></div>Liquid at STP</div>
    <div class="badge"><div class="badge-dot" style="background:#7c3aed;opacity:.6"></div>Gas (below or near n_H)</div>
    <div class="badge"><div class="badge-dot" style="background:#888"></div>Synthetic / estimated IE</div>
  </div>
</div>

<!-- ── PANEL 2: SPECTRUM ── -->
<div id="panel-spectrum" class="panel">
  <div class="spec-wrap">
    <div class="spec-title">All 118 Elements · Sorted by Octave Depth n</div>
    <div class="spec-bar-container">
      <div class="spec-bar" id="specBar"></div>
      <div class="spec-ceiling" id="specCeiling">
        <span class="cl-label">n_H = 92.19</span>
        <span class="cl-sub">condensation<br>ceiling</span>
      </div>
      <div id="specTicks"></div>
    </div>
    <div class="spec-axis">
      <span>He  n=91.33</span>
      <span>← lower n = less bound = gas →</span>
      <span>n=94.00  Cs</span>
    </div>
    <div class="elem-list" id="elemList"></div>
  </div>
</div>

<!-- ── PANEL 3: RING ── -->
<div id="panel-ring" class="panel">
  <div class="ring-wrap">
    <canvas id="ringCanvas" class="rc"></canvas>
  </div>
</div>

<div id="tooltip"></div>

<script>
// ── Element data (Z, sym, IE eV, period, group) ────────────────────────────
const RAW = [
[1,'H',13.598,1,1],[2,'He',24.587,1,18],[3,'Li',5.392,2,1],[4,'Be',9.323,2,2],
[5,'B',8.298,2,13],[6,'C',11.260,2,14],[7,'N',14.534,2,15],[8,'O',13.618,2,16],
[9,'F',17.423,2,17],[10,'Ne',21.565,2,18],[11,'Na',5.139,3,1],[12,'Mg',7.646,3,2],
[13,'Al',5.986,3,13],[14,'Si',8.152,3,14],[15,'P',10.487,3,15],[16,'S',10.360,3,16],
[17,'Cl',12.968,3,17],[18,'Ar',15.760,3,18],[19,'K',4.341,4,1],[20,'Ca',6.113,4,2],
[21,'Sc',6.561,4,3],[22,'Ti',6.828,4,4],[23,'V',6.746,4,5],[24,'Cr',6.767,4,6],
[25,'Mn',7.434,4,7],[26,'Fe',7.902,4,8],[27,'Co',7.881,4,9],[28,'Ni',7.640,4,10],
[29,'Cu',7.727,4,11],[30,'Zn',9.394,4,12],[31,'Ga',5.999,4,13],[32,'Ge',7.900,4,14],
[33,'As',9.815,4,15],[34,'Se',9.752,4,16],[35,'Br',11.814,4,17],[36,'Kr',14.000,4,18],
[37,'Rb',4.177,5,1],[38,'Sr',5.695,5,2],[39,'Y',6.217,5,3],[40,'Zr',6.634,5,4],
[41,'Nb',6.759,5,5],[42,'Mo',7.092,5,6],[43,'Tc',7.280,5,7],[44,'Ru',7.361,5,8],
[45,'Rh',7.459,5,9],[46,'Pd',8.337,5,10],[47,'Ag',7.576,5,11],[48,'Cd',8.994,5,12],
[49,'In',5.786,5,13],[50,'Sn',7.344,5,14],[51,'Sb',8.608,5,15],[52,'Te',9.010,5,16],
[53,'I',10.451,5,17],[54,'Xe',12.130,5,18],[55,'Cs',3.894,6,1],[56,'Ba',5.212,6,2],
[57,'La',5.577,6,3],[72,'Hf',6.825,6,4],[73,'Ta',7.550,6,5],[74,'W',7.864,6,6],
[75,'Re',7.834,6,7],[76,'Os',8.438,6,8],[77,'Ir',8.967,6,9],[78,'Pt',8.959,6,10],
[79,'Au',9.226,6,11],[80,'Hg',10.438,6,12],[81,'Tl',6.108,6,13],[82,'Pb',7.417,6,14],
[83,'Bi',7.289,6,15],[84,'Po',8.417,6,16],[85,'At',9.318,6,17],[86,'Rn',10.745,6,18],
[87,'Fr',4.073,7,1],[88,'Ra',5.279,7,2],[89,'Ac',5.170,7,3],[104,'Rf',6.020,7,4],
[105,'Db',6.100,7,5],[106,'Sg',6.200,7,6],[107,'Bh',6.300,7,7],[108,'Hs',6.400,7,8],
[109,'Mt',6.500,7,9],[110,'Ds',6.600,7,10],[111,'Rg',6.700,7,11],[112,'Cn',11.970,7,12],
[113,'Nh',7.306,7,13],[114,'Fl',8.628,7,14],[115,'Mc',5.580,7,15],[116,'Lv',7.700,7,16],
[117,'Ts',7.700,7,17],[118,'Og',8.900,7,18],
// Lanthanides row 8
[58,'Ce',5.539,8,4],[59,'Pr',5.473,8,5],[60,'Nd',5.525,8,6],[61,'Pm',5.582,8,7],
[62,'Sm',5.644,8,8],[63,'Eu',5.670,8,9],[64,'Gd',6.150,8,10],[65,'Tb',5.864,8,11],
[66,'Dy',5.939,8,12],[67,'Ho',6.022,8,13],[68,'Er',6.108,8,14],[69,'Tm',6.184,8,15],
[70,'Yb',6.254,8,16],[71,'Lu',5.426,8,17],
// + La in lanthanides
[57,'La',5.577,8,3],
// Actinides row 9
[90,'Th',6.307,9,4],[91,'Pa',5.890,9,5],[92,'U',6.194,9,6],[93,'Np',6.266,9,7],
[94,'Pu',6.026,9,8],[95,'Am',5.974,9,9],[96,'Cm',5.991,9,10],[97,'Bk',6.198,9,11],
[98,'Cf',6.282,9,12],[99,'Es',6.368,9,13],[100,'Fm',6.500,9,14],[101,'Md',6.580,9,15],
[102,'No',6.650,9,16],[103,'Lr',4.900,9,17],
[89,'Ac',5.170,9,3],
];

// deduplicate (La/Ac appear in main table AND lanthanide row — keep row 8/9 for
// lanthanide block, use row 6/7 col 3 as placeholder)
const ELEM_MAP = {};
RAW.forEach(([Z,sym,ie,per,grp]) => {
  if(!ELEM_MAP[Z] || per >= 8) ELEM_MAP[Z] = {Z,sym,ie,per,grp};
});

// constants
const NU_P  = 1.8549e43;
const HBAR  = 1.054571817e-34;
const EV_J  = 1.602176634e-19;
const N_H   = 92.19;
const N_FLIP= 3.561;
const SLOPE = 3.506;

function ieToN(ie) {
  const nu = ie * EV_J / (2 * Math.PI * HBAR);
  return Math.log2(NU_P / nu);
}

const GASES  = new Set([1,2,7,8,9,10,17,18,36,54,86]);
const LIQSTP = new Set([35,80]);
const SYNTH  = new Set([43,61,84,85,87,88,89,91,92,93,94,95,96,97,98,99,100,101,102,103,
                        104,105,106,107,108,109,110,111,112,113,114,115,116,117,118]);

// Build element array (deduplicated, one entry per Z)
const ELEMENTS = [];
const seen = new Set();
RAW.forEach(([Z,sym,ie,per,grp]) => {
  if(seen.has(Z)) return;
  // for PT layout: La goes in period 6 group 3 placeholder AND lanthanides
  // we want one canonical entry
  const n    = ieToN(ie);
  const C    = (n - N_FLIP) / SLOPE;
  const st   = GASES.has(Z)  ? 'gas'
             : LIQSTP.has(Z) ? 'liquid'
             : 'solid';
  const above= n > N_H;
  ELEMENTS.push({Z,sym,ie,n,C,st,above,per,grp});
  seen.add(Z);
});
ELEMENTS.sort((a,b)=>a.Z-b.Z);

const N_MIN = Math.min(...ELEMENTS.map(e=>e.n));  // ~91.33
const N_MAX = Math.max(...ELEMENTS.map(e=>e.n));  // ~93.99

// ── Colour mapping ─────────────────────────────────────────────────────────
function nToColour(n, alpha=1) {
  const t = (n - N_MIN) / (N_MAX - N_MIN);
  // Ramp: violet → blue → cyan → green → yellow → orange → red
  const stops = [
    [0.00, [124, 58,237]],
    [0.15, [ 59,130,246]],
    [0.30, [  6,182,212]],
    [0.45, [ 16,185,129]],
    [0.60, [132,204, 22]],
    [0.72, [234,179,  8]],
    [0.85, [249,115, 22]],
    [1.00, [239, 68, 68]],
  ];
  let lo=stops[0],hi=stops[stops.length-1];
  for(let i=0;i<stops.length-1;i++){
    if(t>=stops[i][0]&&t<=stops[i+1][0]){lo=stops[i];hi=stops[i+1];break;}
  }
  const f=(t-lo[0])/(hi[0]-lo[0]);
  const r=Math.round(lo[1][0]+(hi[1][0]-lo[1][0])*f);
  const g=Math.round(lo[1][1]+(hi[1][1]-lo[1][1])*f);
  const b=Math.round(lo[1][2]+(hi[1][2]-lo[1][2])*f);
  return alpha<1 ? `rgba(${r},${g},${b},${alpha})` : `rgb(${r},${g},${b})`;
}

// ── TOOLTIP ────────────────────────────────────────────────────────────────
const tip = document.getElementById('tooltip');
function showTip(e, ev) {
  const stLabel = e.st==='gas'?'⬆ GAS — below n_H ceiling':
                  e.st==='liquid'?'💧 Liquid at STP':
                  e.above?'● Solid/condensed (above n_H)':'~ Near ceiling';
  const syn = SYNTH.has(e.Z)?'<br><span style="color:#666">Synthetic / estimated IE</span>':'';
  tip.innerHTML=`<div class="t-sym">${e.sym}</div>
    <div style="color:#888;font-size:.5rem">Z=${e.Z}</div>
    <div class="t-n">n = ${e.n.toFixed(4)}</div>
    <div class="t-ie">IE = ${e.ie} eV</div>
    <div class="t-ie">C_eff = ${e.C.toFixed(3)}</div>
    <div class="t-state">${stLabel}</div>${syn}`;
  tip.style.display='block';
  moveTip(ev);
}
function moveTip(ev){
  let x=ev.clientX+14,y=ev.clientY-10;
  if(x+210>window.innerWidth) x=ev.clientX-220;
  tip.style.left=x+'px'; tip.style.top=y+'px';
}
document.addEventListener('mousemove',ev=>{
  if(tip.style.display==='block') moveTip(ev);
});

// ── PANEL SWITCHING ────────────────────────────────────────────────────────
function showPanel(id, btn) {
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('panel-'+id).classList.add('active');
  btn.classList.add('active');
  if(id==='spectrum') buildSpectrum();
  if(id==='ring')     drawRing();
}

// ── BUILD PT GRID ──────────────────────────────────────────────────────────
function buildPT() {
  const grid = document.getElementById('ptGrid');
  // We need a 9-row × 18-col grid
  // rows 1-7 = main table, row 8 = lanthanides (with 3-col gap), row 9 = actinides
  const ROWS = 9;
  const COLS = 18;
  const cells = {}; // "r,c" -> element

  ELEMENTS.forEach(e => {
    const key = `${e.per},${e.grp}`;
    // avoid duplicates (La/Ac in both main and f-block)
    if(!cells[key]) cells[key] = e;
  });

  // Gap rows: rows 8 and 9 shifted to start at col 3 offset visually
  // we insert a small gap label at 6,3 and 7,3

  // Build all rows
  for(let r=1; r<=ROWS; r++) {
    for(let c=1; c<=COLS; c++) {
      const div = document.createElement('div');

      if(r===8 && c===1) {
        // Lanthanide series label
        div.className='cell gap';
        div.style.cssText='display:flex;align-items:center;justify-content:flex-end;';
        div.innerHTML=`<span style="font-size:.45rem;color:#404868;letter-spacing:.05em">LA</span>`;
        grid.appendChild(div);
        continue;
      }
      if(r===8 && c===2) {
        div.className='cell gap'; grid.appendChild(div); continue;
      }
      if(r===9 && c===1) {
        div.className='cell gap';
        div.style.cssText='display:flex;align-items:center;justify-content:flex-end;';
        div.innerHTML=`<span style="font-size:.45rem;color:#404868;letter-spacing:.05em">AC</span>`;
        grid.appendChild(div);
        continue;
      }
      if(r===9 && c===2) {
        div.className='cell gap'; grid.appendChild(div); continue;
      }

      const el = cells[`${r},${c}`];
      if(!el) {
        div.className='cell gap'; grid.appendChild(div); continue;
      }

      const col = nToColour(el.n);
      const alpha = el.st==='gas' ? 0.35 : el.st==='liquid' ? 0.65 : 1.0;
      const bgcol = nToColour(el.n, alpha);

      div.className='cell';
      div.style.background = bgcol;
      // Ceiling highlight
      if(Math.abs(el.n - N_H) < 0.05) {
        div.style.boxShadow='inset 0 0 0 2px rgba(232,213,160,.8)';
      }
      div.innerHTML=`
        <span class="z-num">${el.Z}</span>
        <span class="sym">${el.sym}</span>
        <span class="n-val">${el.n.toFixed(2)}</span>`;

      div.addEventListener('mouseover', ev=>showTip(el,ev));
      div.addEventListener('mouseleave', ()=>tip.style.display='none');
      grid.appendChild(div);
    }
  }
}

// ── BUILD SPECTRUM ─────────────────────────────────────────────────────────
function buildSpectrum() {
  const bar    = document.getElementById('specBar');
  const ticks  = document.getElementById('specTicks');
  const ceiling= document.getElementById('specCeiling');
  const list   = document.getElementById('elemList');

  const W = bar.parentElement.offsetWidth;

  // ceiling line position
  const cpct = (N_H - N_MIN)/(N_MAX - N_MIN)*100;
  ceiling.style.left = cpct+'%';

  // ticks
  ticks.innerHTML='';
  ELEMENTS.forEach(e => {
    const pct = (e.n - N_MIN)/(N_MAX-N_MIN)*100;
    const tick = document.createElement('div');
    tick.className='spec-tick';
    tick.style.left=pct+'%';
    tick.style.background=nToColour(e.n, e.st==='gas'?0.5:0.9);
    const lbl = document.createElement('span');
    lbl.className='spec-tick-label';
    lbl.textContent=e.sym;
    lbl.style.color=nToColour(e.n, e.st==='gas'?0.5:0.85);
    tick.appendChild(lbl);
    tick.addEventListener('mouseover', ev=>showTip(e,ev));
    tick.addEventListener('mouseleave', ()=>tip.style.display='none');
    ticks.appendChild(tick);
  });

  // sorted list
  list.innerHTML='';
  const sorted = [...ELEMENTS].sort((a,b)=>a.n-b.n);
  sorted.forEach(e => {
    const row=document.createElement('div');
    row.className='elem-row';
    row.innerHTML=`<span class="es">${e.sym}</span>
      <span class="en">${e.n.toFixed(3)}</span>
      <span class="dot" style="background:${nToColour(e.n,e.st==='gas'?0.4:1)}"></span>`;
    row.addEventListener('mouseover',ev=>showTip(e,ev));
    row.addEventListener('mouseleave',()=>tip.style.display='none');
    list.appendChild(row);
  });
}

// ── DRAW ELEMENT RING ──────────────────────────────────────────────────────
function drawRing() {
  const canvas=document.getElementById('ringCanvas');
  const dpr=window.devicePixelRatio||1;
  const size=canvas.parentElement.offsetWidth;
  canvas.width=size*dpr; canvas.height=size*dpr;
  canvas.style.width=size+'px'; canvas.style.height=size+'px';
  const ctx=canvas.getContext('2d');
  ctx.scale(dpr,dpr);
  const cx=size/2, cy=size/2;
  const R=size*.38, Ri=size*.27;

  ctx.clearRect(0,0,size,size);

  // background glow at centre
  const grd=ctx.createRadialGradient(cx,cy,0,cx,cy,Ri);
  grd.addColorStop(0,'rgba(20,25,50,0.8)');
  grd.addColorStop(1,'rgba(8,10,18,0)');
  ctx.fillStyle=grd; ctx.fillRect(0,0,size,size);

  // The ring spans n from N_MIN to N_MAX (2.66 oct window)
  // Map each element angle = fraction of full circle by n value
  // But also show the n_H ceiling line
  // Ring: n_MIN at top, goes clockwise

  const N_RANGE = N_MAX - N_MIN;

  function nToAngle(n) {
    // top = -π/2, clockwise
    const frac = (n - N_MIN) / N_RANGE;
    return -Math.PI/2 + frac * 2 * Math.PI;
  }

  // Draw ring arc fill — gradient by n
  const ARC_STEPS = 360;
  for(let i=0;i<ARC_STEPS;i++) {
    const t0 = i/ARC_STEPS, t1=(i+1)/ARC_STEPS;
    const n0 = N_MIN + t0*N_RANGE;
    const a0 = -Math.PI/2 + t0*2*Math.PI;
    const a1 = -Math.PI/2 + t1*2*Math.PI;
    ctx.beginPath();
    ctx.arc(cx,cy,R,a0,a1,false);
    ctx.arc(cx,cy,Ri,a1,a0,true);
    ctx.closePath();
    ctx.fillStyle=nToColour(n0, 0.25);
    ctx.fill();
  }

  // Ring outline
  ctx.beginPath(); ctx.arc(cx,cy,R,0,Math.PI*2);
  ctx.strokeStyle='#1c2038'; ctx.lineWidth=1; ctx.stroke();
  ctx.beginPath(); ctx.arc(cx,cy,Ri,0,Math.PI*2);
  ctx.strokeStyle='#1c2038'; ctx.lineWidth=1; ctx.stroke();

  // n_H ceiling line
  const ceilAngle = nToAngle(N_H);
  ctx.beginPath();
  ctx.moveTo(cx+Ri*Math.cos(ceilAngle), cy+Ri*Math.sin(ceilAngle));
  ctx.lineTo(cx+R*Math.cos(ceilAngle),  cy+R*Math.sin(ceilAngle));
  ctx.strokeStyle='rgba(232,213,160,.9)'; ctx.lineWidth=2;
  ctx.setLineDash([4,4]); ctx.stroke(); ctx.setLineDash([]);

  // ceiling label
  const clx=cx+(R+18)*Math.cos(ceilAngle);
  const cly=cy+(R+18)*Math.sin(ceilAngle);
  ctx.fillStyle='rgba(232,213,160,.9)';
  ctx.font='bold 8.5px Space Mono,monospace';
  ctx.textAlign=clx<cx?'right':'left';
  ctx.textBaseline='middle';
  ctx.fillText('n_H = 92.19', clx, cly);
  ctx.font='7px Space Mono,monospace';
  ctx.fillStyle='rgba(232,213,160,.5)';
  const clx2=cx+(R+28)*Math.cos(ceilAngle);
  const cly2=cy+(R+28)*Math.sin(ceilAngle);
  ctx.fillText('condensation ceiling', clx2, cly2-8);

  // Draw element dots
  canvas._hits=[];
  ELEMENTS.forEach(e => {
    const a = nToAngle(e.n);
    const rMid = (R+Ri)/2;
    const dotR = e.st==='solid'?4:e.st==='liquid'?5:3.5;
    const ex = cx + rMid*Math.cos(a);
    const ey = cy + rMid*Math.sin(a);

    // glow for important elements
    if(e.st==='solid' && e.above) {
      const g=ctx.createRadialGradient(ex,ey,0,ex,ey,dotR*3);
      g.addColorStop(0,nToColour(e.n,0.3)); g.addColorStop(1,'transparent');
      ctx.beginPath(); ctx.arc(ex,ey,dotR*3,0,Math.PI*2);
      ctx.fillStyle=g; ctx.fill();
    }

    ctx.beginPath(); ctx.arc(ex,ey,dotR,0,Math.PI*2);
    ctx.fillStyle=nToColour(e.n, e.st==='gas'?0.5:0.9);
    ctx.strokeStyle='rgba(0,0,0,.4)'; ctx.lineWidth=.5;
    ctx.fill(); ctx.stroke();

    canvas._hits.push({x:ex,y:ey,r:dotR+5,e});
  });

  // Symbol labels — only show labels for notable ones to avoid clutter
  const LABEL_Z = new Set([1,2,6,7,8,10,14,18,26,29,47,79,82,92,55,86,36,54]);
  ELEMENTS.filter(e=>LABEL_Z.has(e.Z)).forEach(e=>{
    const a=nToAngle(e.n);
    const lR = e.above ? R+30 : Ri-20;
    const lx=cx+lR*Math.cos(a), ly=cy+lR*Math.sin(a);
    ctx.font=`bold 8px Cormorant Garamond,serif`;
    ctx.fillStyle=nToColour(e.n,0.85);
    ctx.textAlign=lx<cx?'right':'left';
    ctx.textBaseline=ly<cy?'bottom':'top';
    ctx.fillText(e.sym,lx,ly);
  });

  // Centre text
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillStyle='rgba(176,184,216,.7)';
  ctx.font="italic 11px 'Cormorant Garamond',serif";
  ctx.fillText('118 elements', cx, cy-10);
  ctx.font="8px 'Space Mono',monospace";
  ctx.fillStyle='rgba(64,72,104,.9)';
  ctx.fillText('n window: 2.66 octaves', cx, cy+8);
  ctx.fillText('n_H = 92.19', cx, cy+22);

  // Axis labels around ring
  const axisLabels = [
    {n:N_MIN+0.1, label:'He\n91.33', side:1},
    {n:N_MIN+N_RANGE*.25, label:'noble gases →'},
    {n:N_H, label:''},
    {n:N_MIN+N_RANGE*.75, label:'← metals'},
    {n:N_MAX-0.05, label:'Cs\n93.99'},
  ];

  // n_MIN label
  const aHe=nToAngle(N_MIN);
  ctx.font="7px Space Mono,monospace"; ctx.fillStyle='#7c3aed';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('He n=91.33', cx+(R+42)*Math.cos(aHe), cy+(R+42)*Math.sin(aHe));

  const aCs=nToAngle(N_MAX);
  ctx.fillStyle='#ef4444';
  ctx.fillText('Cs n=93.99', cx+(R+42)*Math.cos(aCs), cy+(R+42)*Math.sin(aCs));

  // Hover interaction
  canvas.onmousemove = ev => {
    const rect=canvas.getBoundingClientRect();
    const mx=ev.clientX-rect.left, my=ev.clientY-rect.top;
    let hit=null;
    for(const h of canvas._hits) {
      if(Math.hypot(mx-h.x,my-h.y)<h.r){hit=h;break;}
    }
    if(hit){ canvas.style.cursor='pointer'; showTip(hit.e,ev); }
    else   { canvas.style.cursor='default'; tip.style.display='none'; }
  };
  canvas.onmouseleave=()=>tip.style.display='none';
}

// ── INIT ───────────────────────────────────────────────────────────────────
window.addEventListener('load', ()=>{
  buildPT();
});
window.addEventListener('resize', ()=>{
  const rp=document.getElementById('panel-ring');
  if(rp.classList.contains('active')) drawRing();
});
</script>
</body>
</html>
