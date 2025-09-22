from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from datamodels.pyd_models import SolubilityParams, UserRequest, ProtProtInteraction
from datetime import datetime
from model.model import MammalCore

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mammal = MammalCore()

@app.get("/")
async def home():
    call = mammal.echo()
    # return {"message": f"{call}"}
    return HTMLResponse(INDEX_HTML)

@app.post("/solubility")
async def predict_solubility(req: SolubilityParams):
    pred = mammal.solubility(req)
    return {"prediction": pred}

@app.post("/ppi")
async def predict_solubility(req: ProtProtInteraction):
    pred = mammal.prot_prot_interactions(req)
    return {"prediction": pred}
@app.get("/health")
async def health():
    return {"health": "true"}
@app.post("/api/user")
async def process_user(req: UserRequest):
    
    name = req.name
    print(f"Received name: {name}")

    response_message = f"Hello from Python, {name}! Your request was received at {datetime.now().strftime('%-I:%M:%S %p')}."

    return {"message": response_message}

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Modal Demo</title>
<style>
  :root { --bg:#0b1020; --card:#121a33; --text:#e7ecff; --muted:#9fb0ff; --accent:#6ea8fe; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
         background: linear-gradient(180deg, #0b1020, #0c1328); color: var(--text); }
  .container { max-width: 720px; margin: 80px auto; padding: 24px; text-align:center; }
  h1 { font-weight: 700; letter-spacing: 0.2px; }
  .btn { background: var(--accent); color: #0b1020; border: none; padding: 12px 16px; border-radius: 10px; cursor: pointer; font-weight: 600; }
  .btn:disabled { opacity: .6; cursor: not-allowed; }
  .card { background: var(--card); border: 1px solid #1e2a52; padding: 20px; border-radius: 14px; margin-top: 20px; text-align:left; }
  .muted { color: var(--muted); }
  /* Modal */
  .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.55); opacity: 0; pointer-events: none; transition: opacity .2s ease; }
  .modal-backdrop.open { opacity: 1; pointer-events: auto; }
  .modal { position: fixed; inset: 0; display: grid; place-items: center; padding: 20px; }
  .modal-panel { width: 100%; max-width: 520px; background: var(--card); border: 1px solid #22305f;
                 border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,.35); transform: translateY(16px) scale(.98);
                 transition: transform .2s ease, opacity .2s ease; opacity: 0; }
  .open .modal-panel { transform: translateY(0) scale(1); opacity: 1; }
  .modal-header { padding: 18px 20px; border-bottom: 1px solid #22305f; display:flex; justify-content:space-between; align-items:center; }
  .modal-title { font-size: 18px; font-weight: 700; }
  .close { background: transparent; border: none; color: var(--muted); font-size: 22px; cursor: pointer; }
  .modal-body { padding: 18px 20px; display: grid; gap: 12px; }
  label { font-size: 14px; color: var(--muted); }
  input[type="text"] { width: 100%; padding: 12px 14px; border-radius: 10px; border: 1px solid #2a3a72;
                       background: #0f1730; color: var(--text); outline: none; }
  .actions { padding: 16px 20px; border-top: 1px solid #22305f; display:flex; gap:12px; justify-content:flex-end; }
  .ghost { background: transparent; border: 1px solid #2a3a72; color: var(--muted); }
  .spinner { display:inline-block; width:16px; height:16px; border:2px solid #cfe0ff; border-top-color:transparent;
             border-radius:50%; animation: spin .8s linear infinite; vertical-align:-3px; margin-right:8px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .error { color: #ffb3b3; font-size: 14px; }
</style>
</head>
<body>
  <div class="container">
    <h1> MAMMAL Demo Frontend </h1>
    <p class="muted">Click the button to open the modal, send a request to the backend, and display the response below.</p>
    <button class="btn" id="open">Open Modal</button>

    <div class="card" id="resultCard" style="display:none;">
      <div class="muted">Response</div>
      <pre id="result" style="white-space:pre-wrap; word-break:break-word; margin:8px 0 0;"></pre>
    </div>
  </div>

  <!-- Modal -->
  <div class="modal">
    <div class="modal-backdrop" id="backdrop"></div>
    <div class="modal-panel" id="panel" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
      <div class="modal-header">
        <div class="modal-title" id="modalTitle">Send to Backend</div>
        <button class="close" id="close" aria-label="Close">×</button>
      </div>
      <div class="modal-body">
        <label for="textInput">Enter text</label>
        <input id="textInput" type="text" placeholder="Type something…" />
        <div class="error" id="error" style="display:none;"></div>
      </div>
      <div class="actions">
        <button class="btn ghost" id="cancel">Cancel</button>
        <button class="btn" id="send"><span id="spin" style="display:none;" class="spinner"></span>Send</button>
      </div>
    </div>
  </div>

<script>
(function () {
  const openBtn = document.getElementById('open');
  const closeBtn = document.getElementById('close');
  const cancelBtn = document.getElementById('cancel');
  const backdrop = document.getElementById('backdrop');
  const panel = document.getElementById('panel');
  const sendBtn = document.getElementById('send');
  const spin = document.getElementById('spin');
  const input = document.getElementById('textInput');
  const err = document.getElementById('error');
  const result = document.getElementById('result');
  const resultCard = document.getElementById('resultCard');

const modal = document.querySelector('.modal');
function openModal() {
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
  setTimeout(() => document.getElementById('textInput').focus(), 50);
}
function closeModal() {
  modal.classList.remove('open');
  document.body.style.overflow = '';
  const err = document.getElementById('error');
  err.style.display = 'none';
  err.textContent = '';
}
document.getElementById('open').addEventListener('click', openModal);
document.getElementById('close').addEventListener('click', closeModal);
document.getElementById('cancel').addEventListener('click', closeModal);
document.getElementById('backdrop').addEventListener('click', (e) => {
  if (e.target.id === 'backdrop') closeModal();
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

  async function send() {
    const text = input.value.trim();
    err.style.display = 'none';
    err.textContent = '';
    if (!text) {
      err.textContent = 'Please enter a value.';
      err.style.display = 'block';
      return;
    }
    sendBtn.disabled = true;
    spin.style.display = 'inline-block';
    try {
      const res = await fetch('/api/echo', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error((data && data.detail) || 'Request failed');
      }
      result.textContent = data.result;
      resultCard.style.display = 'block';
      closeModal();
    } catch (e) {
      err.textContent = e.message || 'Something went wrong.';
      err.style.display = 'block';
    } finally {
      sendBtn.disabled = false;
      spin.style.display = 'none';
    }
  }
  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });
})();
</script>
</body>
</html>"""