(function() {
// 1. FIX MOBILE VIEWPORT & CANVAS SCALING
const mobileStyle = document.createElement('style');
mobileStyle.innerHTML = body, html { overflow-x: auto !important; width: 100% !important; margin: 0 !important; padding: 0 !important; } canvas { max-width: 100% !important; height: auto !important; touch-action: manipulation; } div, section { max-width: 100% !important; box-sizing: border-box !important; };
document.head.appendChild(mobileStyle);

// 2. FIX MOBILE CONTROLS (Tap screen to start/jump)
window.addEventListener('touchstart', function(e) {
// Don't trigger jump if tapping inside our control panel
if (e.target.closest('#mobile-dino-master-panel')) return;

// Simulate Spacebar press for game engine
const spaceDown = new KeyboardEvent('keydown', { keyCode: 32, which: 32, code: 'Space', key: ' ', bubbles: true });
const spaceUp = new KeyboardEvent('keyup', { keyCode: 32, which: 32, code: 'Space', key: ' ', bubbles: true });
document.dispatchEvent(spaceDown);
setTimeout(() => document.dispatchEvent(spaceUp), 100);
}, { passive: true });

// 3. IMAGE OVERLAY TOOL
const oldPanel = document.getElementById('mobile-dino-master-panel');
if (oldPanel) oldPanel.remove();

const panel = document.createElement('div');
panel.id = 'mobile-dino-master-panel';
panel.style.cssText = position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); z-index: 9999999; background: #18181c; padding: 12px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.8); font-family: sans-serif; color: #fff; display: flex; flex-direction: column; gap: 8px; width: 90%; max-width: 320px; border: 1px solid #444; text-align: center;;

panel.innerHTML = &lt;div style="font-weight: bold; font-size: 13px; color: #4caf50;"&gt;📱 Mobile Game Fix + Overlay&lt;/div&gt; &lt;div style="font-size: 10px; color: #aaa;"&gt;Tap anywhere on screen to make Dino jump!&lt;/div&gt; &lt;input type="file" id="m-file" accept="image/*" style="font-size: 11px; color: #ccc;"&gt; &lt;button id="m-btn" style=" background: #4CAF50; color: white; border: none; padding: 8px; border-radius: 6px; font-weight: bold; font-size: 12px; cursor: pointer; "&gt;Draw Picture&lt;/button&gt; &lt;div id="m-status" style="font-size: 10px; color: #888;"&gt;Select an image...&lt;/div&gt;;
document.body.appendChild(panel);

let imgData = null;
let isActive = false;
let overlayEls = [];

function updateOverlays() {
const canvases = document.querySelectorAll('canvas');
canvases.forEach((canvas, i) => {
let img = overlayEls[i];
if (!img) {
img = document.createElement('img');
img.style.cssText = 'position: absolute; pointer-events: none; z-index: 999; opacity: 0.8; display: none;';
document.body.appendChild(img);
overlayEls[i] = img;
}
if (isActive && imgData) {
const rect = canvas.getBoundingClientRect();
img.src = imgData;
img.style.left = ${rect.left + window.scrollX}px; img.style.top = ``${rect.top + window.scrollY}px;
img.style.width = ${rect.width}px; img.style.height = ``${rect.height}px;
img.style.display = 'block';
} else {
img.style.display = 'none';
}
});
}

setInterval(() => { if (isActive) updateOverlays(); }, 100);

document.getElementById('m-file').addEventListener('change', (e) => {
const file = e.target.files[0];
if (!file) return;
const reader = new FileReader();
reader.onload = (evt) => {
imgData = evt.target.result;
document.getElementById('m-status').innerText = 'Ready! Tap Draw Picture.';
document.getElementById('m-status').style.color = '#ffca28';
};
reader.readAsDataURL(file);
});

document.getElementById('m-btn').addEventListener('click', () => {
if (!imgData) {
document.getElementById('m-status').innerText = 'Select a photo first!';
return;
}
isActive = !isActive;
updateOverlays();
document.getElementById('m-btn').innerText = isActive ? 'Remove Picture' : 'Draw Picture';
document.getElementById('m-btn').style.background = isActive ? '#f44336' : '#4CAF50';
});