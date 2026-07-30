(function() {
// 1. FIX MOBILE VIEWPORT & CANVAS SCALING
const mobileStyle = document.createElement('style');
mobileStyle.innerHTML = "body, html { overflow-x: auto !important; width: 100% !important; margin: 0 !important; padding: 0 !important; } canvas { max-width: 100% !important; height: auto !important; touch-action: manipulation; } div, section { max-width: 100% !important; box-sizing: border-box !important; }";
document.head.appendChild(mobileStyle);

// 2. FIX MOBILE CONTROLS (Tap screen to start/jump)
// keyCode/which are read-only getters on KeyboardEvent, so the constructor
// options are ignored. Define them on the instance instead, otherwise the
// game engine sees keyCode 0 and never matches Runner.keycodes.JUMP.
function spaceKeyEvent(type) {
const e = new KeyboardEvent(type, { code: 'Space', key: ' ', bubbles: true });
Object.defineProperty(e, 'keyCode', { get: () => 32 });
Object.defineProperty(e, 'which', { get: () => 32 });
return e;
}

window.addEventListener('touchstart', function() {
// Simulate Spacebar press for game engine
document.dispatchEvent(spaceKeyEvent('keydown'));
setTimeout(() => document.dispatchEvent(spaceKeyEvent('keyup')), 100);
}, { passive: true });
})();
