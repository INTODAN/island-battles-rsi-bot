// Plays a list of league maps, one after another, in a lobby page that is set up
// for it: you on Blue with "My localhost bot" on the port of the bot under test,
// the opponent seated on Red. Paste into the lobby tab (javascript), after:
//   window.__runMaps = ['claw', 'delta', ...];
// It needs scripts/serve_maps.py on 127.0.0.1:41499. Read the results with
//   JSON.stringify(window.__run)   // {results: [[map, "Blue wins ..."], ...], done}
// The game's result line is the lobby's; it never pauses and leaves the last
// game on screen. To keep each game's demo, set window.__demoUrl to a local
// receiver (such as http://127.0.0.1:41498/) before pasting: after each game the
// page's own player token fetches the demo, which is POSTed there as
// <map>.json. Demos carry players' names and logs: keep them out of git. See the
// bot-league-iteration skill, "The check against real opponents".
(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const btn = (t) => [...document.querySelectorAll('button')].find((b) => b.innerText.trim() === t && b.offsetParent !== null);
  const main = () => document.querySelector('main').innerText;
  if (window.__run && !window.__run.done) return 'already running';
  // The game's player token, as the page itself sends it, for the demo request.
  if (!window.__fetchWrapped) {
    const original = window.fetch;
    let auth = null;
    window.fetch = function (input, init) {
      try {
        const url = typeof input === 'string' ? input : input.url;
        const headers = init && init.headers;
        const value = headers && (headers instanceof Headers ? headers.get('Authorization') : headers.Authorization || headers.authorization);
        if (url.includes('/game/from-lobby/') && value) auth = value;
      } catch (e) { /* not a request to the game */ }
      return original.apply(this, arguments);
    };
    window.__fetchWrapped = true;
    window.__gameAuthorization = () => auth;
  }
  async function saveDemo(name) {
    const lobby = JSON.parse(sessionStorage.getItem('lobby-playground')).room.lobby_id;
    const auth = window.__gameAuthorization();
    if (!auth) return 'no token seen';
    const response = await fetch('https://island-battles.elidan.org/game/from-lobby/' + lobby + '/demo', { headers: { Authorization: auth } });
    if (!response.ok) return 'demo ' + response.status;
    const saved = await fetch(window.__demoUrl + name + '.json', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: await response.text() });
    return 'saved ' + saved.status;
  }
  const st = (window.__run = { results: [], log: [], queue: (window.__runMaps || []).slice(), done: false });
  async function setMap(name) {
    const text = await fetch('http://127.0.0.1:41499/' + name + '.json').then((r) => r.text());
    const back = btn('Back to lobby');
    if (back) { back.click(); await sleep(3000); }
    btn('Change map').click();
    await sleep(1000);
    const form = [...document.querySelectorAll('form')].find((f) => f.querySelector('select option[value="file"]') && f.offsetParent !== null);
    const sel = form.querySelector('select');
    if (sel.value !== 'file') { sel.value = 'file'; sel.dispatchEvent(new Event('change', { bubbles: true })); await sleep(500); }
    const input = form.querySelector('input[type=file]');
    const dt = new DataTransfer();
    dt.items.add(new File([text], name + '.json', { type: 'application/json' }));
    input.files = dt.files;
    input.dispatchEvent(new Event('change', { bubbles: true }));
    await sleep(1500);
    [...form.querySelectorAll('button')].find((b) => b.innerText.trim() === 'Save').click();
    // The lobby can take several seconds to show the new map.
    let m;
    for (let i = 0; i < 10; i++) {
      await sleep(1500);
      m = (main().match(/Map: ([^ ]+)/) || [])[1];
      if (m === name) return;
    }
    throw new Error('map is ' + m + ' not ' + name);
  }
  async function playOne(name) {
    await setMap(name);
    const ready = btn('Mark ready');
    if (ready) { ready.click(); await sleep(2500); }
    // The start button can stay disabled for a moment after getting ready: try until the game is on.
    for (let i = 0; i < 20 && btn('Start lobby'); i++) {
      const start = btn('Start lobby');
      if (!start.disabled) start.click();
      await sleep(1500);
    }
    await sleep(5000);
    for (let i = 0; i < 400; i++) {
      const t = main();
      const sec = t.slice(t.indexOf('YOUR BOT'), t.indexOf('YOUR BOT') + 200);
      if (sec.includes('Game over')) {
        const result = sec.split('\n').map((x) => x.trim()).filter((x) => x)[2];
        if (window.__demoUrl) {
          try { st.log.push([name, 'demo', await saveDemo(name)]); } catch (e) { st.log.push([name, 'demo', e.message]); }
        }
        return result;
      }
      await sleep(3000);
    }
    return 'timeout';
  }
  (async () => {
    while (st.queue.length) {
      const name = st.queue.shift();
      // A map that fails to set up is tried again, after the lobby has had time to settle.
      let result;
      for (let attempt = 0; attempt < 3; attempt++) {
        try { result = await playOne(name); break; }
        catch (e) { result = 'error: ' + e.message; st.log.push([name, attempt, e.message]); await sleep(8000); }
      }
      st.results.push([name, result]);
    }
    st.done = true;
  })();
  return 'started ' + st.queue.length + ' maps';
})();
