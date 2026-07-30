// ---------------------------------------------
// Live Multi-User Drawing Overlay
// ---------------------------------------------
// Based on Multi-User-HTML5-Shared-Canvas/canvas.html
// Draws on a transparent canvas layered over the t-rex game and
// shares every stroke with everyone else on the channel via PubNub.

(function () {
    'use strict';

    const userId  = `dino-artist-${Math.random()}.${Math.random()}`;
    const pubnub  = PubNub({ userId: userId });
    const channel = 'dino-shared-canvas';
    const users   = {};

    // Logical drawing resolution, matching Runner.defaultDimensions so the
    // strokes composite 1:1 into the game canvas. Coordinates are sent in this
    // space so players with different window sizes see the same picture.
    const WIDTH  = 600;
    const HEIGHT = 150;

    const COLORS = [
        '#ff0000', '#00ff00', '#0000ff',
        '#ffff00', '#00ffff', '#ff00ff', '#ffffff'
    ];

    // Offscreen canvas holding the artwork. The game blits this onto its own
    // canvas right after the sky, so the drawing sits in the background behind
    // the dino, cactuses and clouds.
    const canvas  = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width  = WIDTH;
    canvas.height = HEIGHT;

    // Scratch buffer for the scroll shift. Copying a canvas onto itself with an
    // offset is not reliable, so the shifted copy is staged here first.
    const scratch    = document.createElement('canvas');
    const scratchCtx = scratch.getContext('2d');
    scratch.width    = WIDTH;
    scratch.height   = HEIGHT;

    let input   = null;
    let enabled = true;

    // Sub-pixel scroll debt. The artwork scrolls by physically shifting the
    // canvas pixels left, which can only happen in whole pixels, so fractional
    // movement is carried over to the next frame.
    let scrollDebt = 0;

    // Fraction of the game speed the sky artwork drifts at. Clouds move slowly
    // relative to the ground, and the drawing sits with them in the sky.
    const SCROLL_SPEED_RATIO = 0.05;

    // Build the pointer capture layer, color picker and occupancy counter.
    function setupDom() {
        input = document.createElement('div');
        input.id = 'drawing-input';
        document.body.appendChild(input);

        const colors = document.createElement('div');
        colors.id = 'drawing-colors';
        COLORS.forEach(function (hex, i) {
            const swatch = document.createElement('div');
            swatch.className = 'drawing-color' + (i == 0 ? ' active' : '');
            swatch.setAttribute('hex', hex);
            swatch.style.backgroundColor = hex;
            colors.appendChild(swatch);
        });
        document.body.appendChild(colors);

        colors.addEventListener('click', function (event) {
            const color = event.target.getAttribute('hex');
            if (!color) return;
            getUser(userId).style = color;
            document.querySelectorAll('#drawing-colors .drawing-color')
                .forEach(function (c) { c.classList.remove('active'); });
            event.target.classList.add('active');
        });

        const occupancy = document.createElement('div');
        occupancy.id = 'drawing-occupancy';
        occupancy.textContent = '1';
        document.body.appendChild(occupancy);

        return occupancy;
    }

    // Get user by ID. Can be remote or local user.
    function getUser(id) {
        if (id in users) return users[id];
        users[id] = {
            userId     : id,
            drawing    : false,
            coords     : { x: 0, y: 0 },
            style      : COLORS[0],
            lastCoords : null
        };
        return users[id];
    }

    // Draw line segment between last and current position.
    function draw(id) {
        const user   = getUser(id);
        const coords = user.coords;

        if (!user.drawing) {
            user.lastCoords = null;
            return;
        }

        if (!user.lastCoords) {
            user.lastCoords = { x: coords.x, y: coords.y };
            return;
        }

        context.beginPath();
        context.strokeStyle = user.style;
        context.lineWidth = 2;
        context.lineCap = 'round';
        context.moveTo(user.lastCoords.x, user.lastCoords.y);
        context.lineTo(coords.x, coords.y);
        context.stroke();

        user.lastCoords = { x: coords.x, y: coords.y };
    }

    // Get scaled coordinates in the shared drawing space. The game canvas is
    // scaled and centered by arcade mode, so map through its on-screen rect.
    function getXY(event) {
        const gameCanvas = document.querySelector('.runner-canvas');
        const rect = gameCanvas ? gameCanvas.getBoundingClientRect() : {
            left: 0, top: 0,
            width: document.body.clientWidth,
            height: document.body.clientHeight
        };
        // The canvas stays aligned with the screen; the artwork inside it is
        // what moves, so pointer coordinates map straight across.
        return {
            x: Math.floor(((event.clientX - rect.left) / rect.width) * WIDTH),
            y: Math.floor(((event.clientY - rect.top) / rect.height) * HEIGHT)
        };
    }

    function capture(event) {
        if (!enabled) return;
        event.preventDefault();
        // Keep the pointer off of the game, it jumps on mouse down.
        event.stopPropagation();

        const user = getUser(userId);
        user.coords = getXY(event);
        if (event.type === 'pointerdown') user.drawing = true;
        if (event.type === 'pointerup')   user.drawing = false;
        if (user.drawing || event.type === 'pointerup') {
            draw(userId);
            broadcast(user);
        }
    }

    function broadcast(state) {
        pubnub.publish({
            channel: channel,
            message: {
                userId  : state.userId,
                drawing : state.drawing,
                coords  : state.coords,
                style   : state.style
            }
        });
    }

    function processState(state) {
        if (!state || !state.userId) return;
        // Local strokes are already on the canvas.
        if (state.userId === userId) return;
        const user = getUser(state.userId);
        user.drawing = state.drawing;
        user.coords = state.coords;
        user.style = state.style;
        draw(state.userId);
    }

    async function loadHistory() {
        const history = await pubnub.history({ channel: channel });
        if (!history || !history[0]) return;
        history[0].forEach(processState);
    }

    function setupDrawing() {
        const occupancyEl = setupDom();

        input.addEventListener('pointerdown', capture);
        input.addEventListener('pointermove', capture);
        input.addEventListener('pointerup', capture);

        // Press D to hand the pointer back to the game.
        document.addEventListener('keydown', function (e) {
            if (e.keyCode != 68) return; // D
            enabled = !enabled;
            document.body.classList.toggle('drawing-disabled', !enabled);
        });

        pubnub.subscribe({
            channel: channel,
            messages: processState
        });

        // Number of users online right now.
        pubnub.subscribe({
            channel: `${channel}-pnpres`,
            messages: function (message) {
                if (message && message.occupancy != undefined) {
                    occupancyEl.textContent = message.occupancy;
                }
            }
        });

        loadHistory();
    }

    // Advance the artwork. Called once per frame by the game with the same
    // deltaTime and speed the horizon uses, so the drawing keeps pace with the
    // world moving forward underneath it. The pixels are physically copied to
    // the left and the vacated strip on the right is left transparent, so
    // anything that reaches the left edge is gone for good.
    function update(deltaTime, speed) {
        if (!deltaTime || !speed) return;

        scrollDebt += speed * SCROLL_SPEED_RATIO * (deltaTime / 1000) * 60;
        const shift = Math.floor(scrollDebt);
        if (shift < 1) return;
        scrollDebt -= shift;

        if (shift >= WIDTH) {
            context.clearRect(0, 0, WIDTH, HEIGHT);
        } else {
            scratchCtx.clearRect(0, 0, WIDTH, HEIGHT);
            scratchCtx.drawImage(canvas, -shift, 0);
            context.clearRect(0, 0, WIDTH, HEIGHT);
            context.drawImage(scratch, 0, 0);
        }

        // In-progress strokes must travel with the pixels they already laid
        // down, otherwise the next segment streaks back to a stale position.
        Object.keys(users).forEach(function (id) {
            const last = users[id].lastCoords;
            if (last) last.x -= shift;
        });
    }

    // Paint the artwork onto the game canvas, scaled from drawing space into
    // the game's dimensions.
    function render(ctx, width, height) {
        ctx.drawImage(canvas, 0, 0, width, height);
    }

    // The game's update loop blits this onto its canvas, just after the sky and
    // before the horizon, clouds and characters are drawn.
    window['SharedDrawing'] = {
        canvas : canvas,
        update : update,
        render : render
    };

    document.addEventListener('DOMContentLoaded', setupDrawing);
})();
