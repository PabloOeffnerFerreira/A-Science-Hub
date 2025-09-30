from __future__ import annotations

# Very lightweight grouping for a simple chart
AMINO_ACID_GROUPS = {
    'Phe': 'Hydrophobic', 'Leu': 'Hydrophobic', 'Ile': 'Hydrophobic', 'Met': 'Hydrophobic',
    'Val': 'Hydrophobic', 'Ser': 'Polar', 'Pro': 'Hydrophobic', 'Thr': 'Polar',
    'Ala': 'Hydrophobic', 'Tyr': 'Polar', 'STOP': 'Stop Codon', 'His': 'Charged',
    'Gln': 'Polar', 'Asn': 'Polar', 'Lys': 'Charged', 'Asp': 'Charged',
    'Glu': 'Charged', 'Cys': 'Polar', 'Trp': 'Hydrophobic', 'Arg': 'Charged',
    'Gly': 'Hydrophobic'
}

SITES = {
    "EcoRI (GAATTC)": "GAATTC",
    "BamHI (GGATCC)": "GGATCC",
    "HindIII (AAGCTT)": "AAGCTT",
    "NotI (GCGGCCGC)": "GCGGCCGC",
    "Custom": ""
}

AA_MASS = {
    # average residue masses (approx, without water)
    "A": 89.09, "R": 174.20, "N": 132.12, "D": 133.10, "C": 121.15,
    "E": 147.13, "Q": 146.15, "G": 75.07, "H": 155.16, "I": 131.17,
    "L": 131.17, "K": 146.19, "M": 149.21, "F": 165.19, "P": 115.13,
    "S": 105.09, "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15
}


DNA_W = {"A": 313.21, "T": 304.2, "G": 329.21, "C": 289.18, "U": 290.17}
PROT_W = {
    "A": 89.09, "R": 174.2, "N": 132.12, "D": 133.1, "C": 121.15,
    "E": 147.13, "Q": 146.15, "G": 75.07, "H": 155.16, "I": 131.17,
    "L": 131.17, "K": 146.19, "M": 149.21, "F": 165.19, "P": 115.13,
    "S": 105.09, "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15
}

# 3-letter → 1-letter
AA1 = {
    "Ala":"A","Arg":"R","Asn":"N","Asp":"D","Cys":"C","Gln":"Q","Glu":"E","Gly":"G",
    "His":"H","Ile":"I","Leu":"L","Lys":"K","Met":"M","Phe":"F","Pro":"P","Ser":"S",
    "Thr":"T","Trp":"W","Tyr":"Y","Val":"V","STOP":"*"
}


# ---- embedded HTML for the WebEngine dialog ----
HTML_VIEWER = """<!doctype html>
<html><head><meta charset="utf-8"/>
<title>AlphaFold 3D</title>
<style>
  html,body{height:100%;margin:0;background:#111;color:#ddd;font-family:system-ui}
  #tb{height:44px;display:flex;gap:10px;align-items:center;padding:8px;border-bottom:1px solid #333;background:#1a1a1a}
  #v{height:calc(100% - 44px)}
  select,label,button{font-size:13px}
</style>
<script src="https://unpkg.com/ngl@latest/dist/ngl.js"></script>
<script>
  // Hide the deprecated useLegacyLights warning from Three.js/NGL
  (function() {
    const origWarn = console.warn;
    console.warn = function (...args) {
      if (args[0]?.includes("useLegacyLights")) return;
      origWarn.apply(console, args);
    };
  })();
</script>
</head>
<body>
<div id="tb">
  <label>Representation</label>
  <select id="rep">
    <option value="cartoon">cartoon</option>
    <option value="licorice">licorice</option>
    <option value="ball+stick">ball+stick</option>
    <option value="spacefill">spacefill</option>
    <option value="backbone">backbone</option>
  </select>
  <label><input id="plddt" type="checkbox" checked> color by pLDDT</label>
  <button id="apply">Apply</button>
  <span id="st" style="margin-left:auto;opacity:.7"></span>
</div>
<div id="v"></div>
<script>
let stage, comp;
function init(){
  stage = new NGL.Stage("v",{backgroundColor:"black"});
  window.addEventListener("resize",()=>stage.handleResize());
  document.getElementById("apply").addEventListener("click", apply);
}
function apply(){
  if(!comp) return;
  const rep = document.getElementById("rep").value;
  const by = document.getElementById("plddt").checked;
  comp.removeAllRepresentations();
  const p = by ? {colorScheme:"bfactor"} : {};
  comp.addRepresentation(rep, p);
  comp.autoView();
}
function loadFromText(txt, ext){
  document.getElementById("st").textContent="Loading…";
  if(comp){ comp.dispose(); comp=null; }
  const blob = new Blob([txt], {type:"text/plain"});
  stage.loadFile(blob, { ext: ext }).then(c=>{
    comp=c; apply(); document.getElementById("st").textContent="Loaded";
  }).catch(e=>{
    console.error(e); document.getElementById("st").textContent="Error";
  });
}
window.addEventListener("DOMContentLoaded", init);
</script>
</body></html>
"""
