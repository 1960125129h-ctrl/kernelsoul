"""
Kernelsoul - FastAPI API Server
Exposes REST + SSE streaming endpoints for the V4 Engine.
"""
import sys, os, json, uuid as _uuid

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core_engine import V4Engine

ENGINE = V4Engine(PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Kernelsoul API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _state_dict():
    s = ENGINE.state_mgr.state
    hp_pct = int(s.hp / max(s.max_hp or 1, 1) * 100)
    ep_pct = int(getattr(s, "energy", 100) / 100 * 100)
    return {
        "hp": s.hp, "max_hp": s.max_hp, "hp_pct": hp_pct,
        "ep": getattr(s, "energy", 0), "ep_pct": ep_pct,
        "emotion": s.emotion,
        "rounds": ENGINE.session_meta.round_count,
    }


def _char_list():
    d = os.path.join(PROJECT_ROOT, "characters")
    chars = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            fp = os.path.join(d, name)
            if name.startswith("."):
                continue
            if os.path.isdir(fp) and os.path.exists(os.path.join(fp, "character_data.json")):
                try:
                    with open(os.path.join(fp, "character_data.json"), encoding="utf-8") as f:
                        cd = json.load(f)
                    chars.append({"id": name, "name": cd.get("name", name)})
                except Exception:
                    chars.append({"id": name, "name": name})
            elif name.endswith(".json"):
                cid = name[:-5]
                try:
                    with open(fp, encoding="utf-8") as f:
                        raw = json.load(f)
                    n = raw.get("data", raw).get("name", cid)
                except Exception:
                    n = cid
                chars.append({"id": cid, "name": n})
    return chars


@app.get("/api/characters")
def get_chars():
    return JSONResponse(_char_list())


@app.post("/api/switch")
def switch_char(data: dict):
    cid = data.get("char_id", "")
    if not cid:
        return JSONResponse({"error": "No char_id"}, status_code=400)
    try:
        ENGINE.state_mgr.save()
        ns = f"session_{_uuid.uuid4().hex[:8]}"
        ENGINE.char = cid
        ENGINE.session = ns
        ENGINE.paths.bind(char=cid, session=ns)
        from state_manager import StateManager
        from memory_manager import MemoryManager
        ENGINE.state_mgr = StateManager(ENGINE.paths)
        ENGINE.memory = MemoryManager(ENGINE.paths)
        ENGINE.session_meta = ENGINE.load_session_meta()
        ENGINE.character = ENGINE.load_character_card(cid)
        if hasattr(ENGINE, "worldbook_retriever"):
            ENGINE.worldbook_retriever.load_from_character(ENGINE.character)
        if hasattr(ENGINE, "plugins") and ENGINE.plugins:
            ENGINE.plugins.reset_world(ENGINE.character)
        if hasattr(ENGINE, "evo_trigger"):
            ENGINE.evo_trigger.load_rules(ENGINE.character)
        ENGINE.config.system["last_character"] = cid
        ENGINE.config.save_system()
        return JSONResponse({"status": "ok", "char": cid, "state": _state_dict()})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/state")
def get_state():
    if not ENGINE.char:
        return JSONResponse({"error": "No character loaded"}, status_code=400)
    return JSONResponse(_state_dict())


@app.get("/api/sessions")
def list_sessions():
    if not ENGINE.char:
        return JSONResponse([])
    s = ENGINE.list_sessions() if hasattr(ENGINE, "list_sessions") else []
    return JSONResponse(s)


@app.post("/api/session/switch")
def switch_sess(data: dict):
    sid = data.get("session_id", "")
    try:
        ENGINE.switch_session(sid)
        return JSONResponse({"status": "ok", "session": sid, "state": _state_dict()})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/session/new")
def new_sess():
    try:
        ns = ENGINE.new_session() if hasattr(ENGINE, "new_session") else None
        return JSONResponse({"status": "ok", "session": ns or "?"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/history")
def get_history(limit: int = 50):
    if not ENGINE.memory:
        return JSONResponse([])
    rounds = ENGINE.memory.recent_rounds(limit)
    return JSONResponse([r for r in rounds if isinstance(r, dict)])


@app.post("/api/chat/stream")
async def chat_stream(data: dict):
    msg = data.get("message", "").strip()
    if not msg:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    if ENGINE.plugins:
        ENGINE.plugins.fire_hook("on_user_input", msg)
        filtered = ENGINE.plugins.filter_hook("on_user_input", msg)
    else:
        filtered = msg

    sp, up = ENGINE.build_prompt(filtered)

    async def event_stream():
        yield json.dumps({"type": "meta", "user": msg}) + "\n\n"
        full = ""
        for token in ENGINE.bridge.generate_stream(sp, up):
            if token.startswith("[ERROR]"):
                yield json.dumps({"type": "error", "text": token}) + "\n\n"
                return
            full += token
            yield json.dumps({"type": "token", "text": token}) + "\n\n"

        if ENGINE.plugins:
            ENGINE.plugins.fire_hook("on_ai_response", full)
        ENGINE.state_mgr.save()
        ENGINE.session_meta.increment_rounds()
        ENGINE.session_meta.touch()
        from session_meta import save_meta
        save_meta(ENGINE.paths.meta_path(), ENGINE.session_meta)
        yield json.dumps({"type": "done", "state": _state_dict()}) + "\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/render_mode")
def set_render_mode(data: dict):
    mode = data.get("mode", "direct")
    if ENGINE.semantic_renderer and hasattr(ENGINE, "semantic_renderer"):
        ok = ENGINE.semantic_renderer.switch_mode(mode)
        if not ok:
            return JSONResponse({"error": f"Invalid mode: {mode}. Use: direct, semantic, hybrid"}, status_code=400)
        ENGINE.render_mode = mode
        return JSONResponse({"status": "ok", "render_mode": mode})
    return JSONResponse({"error": "Semantic renderer not available"}, status_code=503)


@app.get("/api/render_mode")
def get_render_mode():
    mode = getattr(ENGINE, "render_mode", "direct")
    axes = getattr(ENGINE.semantic, "axis_names", []) if hasattr(ENGINE, "semantic") else []
    return JSONResponse({"render_mode": mode, "axes_available": axes})


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "Kernelsoul"}


if __name__ == "__main__":
    port = int(os.environ.get("V4_PORT", "8000"))
    host = os.environ.get("V4_HOST", "127.0.0.1")
    print(f"Kernelsoul API -> http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)