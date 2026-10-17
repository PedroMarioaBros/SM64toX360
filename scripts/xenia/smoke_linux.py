#!/usr/bin/env python3
"""Verify Xenia Canary Linux startup with no proprietary game executable.

This intentionally DOES NOT run an Xbox game, inject controller input or claim
hardware compatibility. It probes whether a pinned official AppImage can start
on a virtual X11 display using its Vulkan-dependent null graphics backend.
Writes machine-readable JSON and per-run logs to a chosen output directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

XENIA_RELEASE_TAG="dac2794"
XENIA_LINUX_RELEASE_URL=(
    "https://github.com/xenia-canary/xenia-canary/releases/download/"
    "dac2794/xenia_canary_linux.AppImage"
)

def run_probe(executable:Path,outdir:Path,label:str,extra:list[str],seconds:int)->dict:
    # Run in Xvfb as Linux builds may still initialize SDL2/X11 with --gpu=null.
    cmd=[
        "xvfb-run","-a","-s","-screen 0 1280x720x24",
        str(executable),
        "--gpu=null","--apu=nop","--hid=nop",
        f"--storage_root={outdir / ('profile_'+label)}",
        "--log_file=stdout",
        *extra,
    ]
    log_file=outdir/f"{label}.log"
    started=time.monotonic()
    env=os.environ.copy()
    env["LIBGL_ALWAYS_SOFTWARE"]="1"
    env["GALLIUM_DRIVER"]="llvmpipe"
    env["XDG_RUNTIME_DIR"]=str(outdir / "runtime")
    (outdir/"runtime").mkdir(exist_ok=True,mode=0o700)
    env["SDL_AUDIODRIVER"]="dummy"
    result={"case":label,"timeout_seconds":seconds,"executable":str(executable),
            "game_binary_provided":False,"graphics":"null","controller":"nop"}
    try:
        p=subprocess.run(cmd,cwd=outdir,env=env,capture_output=True,text=True,
                         timeout=seconds,errors="replace")
        data=(p.stdout or "")+"\n--- STDERR ---\n"+(p.stderr or "")
        result["exit_code"]=p.returncode
        result["timed_out"]=False
    except subprocess.TimeoutExpired as e:
        a=e.stdout.decode("utf-8","replace") if isinstance(e.stdout,bytes) else (e.stdout or "")
        b=e.stderr.decode("utf-8","replace") if isinstance(e.stderr,bytes) else (e.stderr or "")
        data=a+"\n--- STDERR ---\n"+b
        result["exit_code"]=None
        result["timed_out"]=True
    except (OSError,ValueError) as e:
        data=str(e)
        result["launch_error"]=str(e)
        result["exit_code"]=None
        result["timed_out"]=False
    result["elapsed_sec"]=round(time.monotonic()-started,2)
    log_file.write_text(data,encoding="utf-8")
    result["log_file"]=str(log_file)
    result["log_sha256"]=hashlib.sha256(data.encode("utf-8")).hexdigest()
    result["log_bytes"]=len(data.encode("utf-8"))
    result["log_tail"]=data[-1500:]
    result["log_error_keywords"]=[
        word for word in ("Vulkan","VK_ERROR","FATAL","error","Failed","Unhandled")
        if word.lower() in data.lower()
    ]
    return result

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--binary",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    target=args.binary.absolute()
    out=args.output.absolute()
    out.mkdir(exist_ok=True,parents=True)
    report={
        "purpose":"XENIA_LINUX_EMULATOR_SMOKE_ONLY",
        "source_release":XENIA_LINUX_RELEASE_URL,
        "game_xex_executed":False,
        "controller_buttons_injected":False,
        "xbox_crashes_reproduced":False,
        "gpu_backend":"null (may still demand a Vulkan software driver)",
        "testing_scope":"environment preflight, not SM64 or Xbox gameplay",
        "status":"RUNNING",
    }
    if not target.is_file():
        report["status"]="BLOCKED_APPIMAGE_EXTRACT_FAILED"
    else:
        report["executable_bytes"]=target.stat().st_size
        report["executable_sha256"]=hashlib.sha256(target.read_bytes()).hexdigest()
        invalid=out/"invalid_header.xex"
        invalid.write_bytes(b"INVALID_NOT_A_REAL_XEX2"+bytes(1024))
        report["cases"]=[
            run_probe(target,out,"options",["--help"],15),
            run_probe(target,out,"invalid_xex", [str(invalid)],25)
        ]
        # Return actual outcomes, not a false hardware 'PASS'.
        if all("launch_error" not in c for c in report["cases"]):
            report["status"]="PROBED_CHECK_LOGS_AND_EXIT_CODES"
        else:
            report["status"]="ENVIRONMENT_LAUNCH_ERROR"
        invalid.unlink(missing_ok=True)
    (out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    # Don't claim user-game success and don't fail CI for an expected invalid XEX.

if __name__=="__main__": main()
