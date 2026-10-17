#!/usr/bin/env python3
"""Drive Xenia Canary's keyboard-as-gamepad via Xvfb + xdotool.

Does NOT require a physical controller or visible display. The source version
of the Linux keyboard driver supports --hid=keyboard, --keyboard_mode=1 and
CLI-configurable keybind_dpad_up/down/a/start.

When --xex is NOT provided, the script launches an intentionally invalid XEX
to test WINDOW and HOST EVENT injection only. It MUST NOT claim that a guest
Xbox game received the events in this mode.

With a PRIVATE --xex path available *on the same runner*, it logs the
individual input trials and emulator exit/error behavior, but still requires
a verified title-state signal before claiming buttons reached the game.
Never commit XEX or game binaries into a public repo or Actions artifact.
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

KEYS={"dpad_up":"R","dpad_down":"T","a":"J","start":"G"}

def cmd(args:list[str],seconds:float=8):
    return subprocess.run(args,capture_output=True,text=True,timeout=seconds,
                          errors="replace")

def windows():
    """Enumerate visible windows on the supplied DISPLAY without a window manager."""
    r=cmd(["xdotool","search","--onlyvisible","--name",".*"])
    if r.returncode:
        return []
    found=[]
    for wid in r.stdout.splitlines():
        if not wid.isdigit():
            continue
        n=cmd(["xdotool","getwindowname",wid],seconds=3)
        if n.returncode==0:
            found.append((wid,n.stdout.strip()))
    return found

def replay(binary:Path,outdir:Path,xex:Path|None,wait_before_seconds:float):
    outdir.mkdir(parents=True,exist_ok=True)
    is_real=xex is not None
    if is_real:
        if not xex.is_file() or xex.read_bytes()[:4]!=b"XEX2":
            raise ValueError("Private XEX must exist and start with XEX2")
        game=xex.absolute()
        game_sha=hashlib.sha256(game.read_bytes()).hexdigest()
    else:
        game=outdir/"invalid_header_for_host_input_smoke.xex"
        game.write_bytes(b"NOT_A_REAL_XEX2"+bytes(2048))
        game_sha=None
    # Launch window and initialize keyboard HID. R/T/J/G map to Xbox buttons; function keys F5-F8 were rejected or hijacked by Xenia UI.
    flags=[
        "--gpu=null","--apu=nop","--hid=keyboard",
        "--keyboard_mode=1","--keyboard_user_index=0",
        "--keybind_dpad_up=R","--keybind_dpad_down=T",
        "--keybind_a=J","--keybind_start=G",
        f"--storage_root={outdir/'xenia_storage'}",
        "--log_file=stdout",
        str(game)
    ]
    env=os.environ.copy()
    env["LIBGL_ALWAYS_SOFTWARE"]="1"
    env["GALLIUM_DRIVER"]="llvmpipe"
    env["SDL_AUDIODRIVER"]="dummy"
    (outdir/"runtime").mkdir(exist_ok=True,mode=0o700)
    env["XDG_RUNTIME_DIR"]=str(outdir/"runtime")
    log=outdir/"xenia_keyboard.log"
    report={
        "test_name":"XENIA_CANARY_LINUX_KEYBOARD_INPUT_HARNESS",
        "private_game_xex_supplied":is_real,
        "xex_sha256":game_sha,
        "gpu":"null",
        "hid":"keyboard",
        "keyboard_mode":1,
        "key_map":KEYS,
        "guest_buttons_proven":False,
        "guest_crash_reproduced":False,
        "trials":[],
        "status":"RUNNING",
    }
    with log.open("w",encoding="utf8") as file:
        proc=subprocess.Popen([str(binary.absolute()),*flags],cwd=outdir,
                              env=env,stdout=file,stderr=subprocess.STDOUT,
                              start_new_session=True)
        try:
            deadline=time.monotonic()+min(20,wait_before_seconds)
            found=[]
            while time.monotonic()<deadline:
                found=[(ident,name) for ident,name in windows()
                       if "xenia" in name.lower()]
                if found or proc.poll() is not None: break
                time.sleep(0.45)
            report["visible_xenia_windows"]=[name for _,name in found]
            if not found:
                report["status"]="BLOCKED_XENIA_WINDOW_NOT_DISCOVERED"
            else:
                window_id=found[0][0]
                focus=cmd(["xdotool","windowfocus",window_id],seconds=4)
                report["window_focus_exit"]=focus.returncode
                if focus.returncode:
                    report["status"]="BLOCKED_NO_X11_WINDOW_FOCUS"
                else:
                    # Keep inputs distinct; no overlay render/guest state
                    # assertions are made without actual Xbox game evidence.
                    if is_real:
                        time.sleep(max(0,wait_before_seconds))
                    for label,key in KEYS.items():
                        if proc.poll() is not None:
                            report["trials"].append({"button":label,"sent":False,
                                                   "reason":"emulator_exited"})
                            break
                        down=cmd(["xdotool","keydown","--clearmodifiers",key])
                        time.sleep(0.24)
                        up=cmd(["xdotool","keyup",key])
                        trial={"button":label,"x11_key":key,
                               "host_down_returncode":down.returncode,
                               "host_up_returncode":up.returncode,
                               "sent":down.returncode==0 and up.returncode==0,
                               "emulator_running_after":proc.poll() is None}
                        report["trials"].append(trial)
                        time.sleep(0.45)
                    report["status"]=(
                        "HOST_KEYS_SENT_GUEST_NOT_PROVEN"
                        if len(report["trials"])==4
                        and all(t["sent"] for t in report["trials"])
                        else "HOST_INPUT_PARTIALLY_BLOCKED"
                    )
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
            report["emulator_return_code"]=proc.returncode
    text=log.read_text(encoding="utf8",errors="replace")
    expected_bindings=("controller input DPAD_UP","controller input DPAD_DOWN",
                       "controller input A.","controller input START.")
    # Header logging in current Canary uses "... controller input A." for A;
    # do not confuse an X11 successful key event with a recognized Xenia HID map.
    report["xenia_rejected_keybindings"]="failed to parse binding" in text.lower()
    report["xenia_required_bindings_present"]={
        item: item in text for item in expected_bindings
    }
    if report["xenia_rejected_keybindings"] or not all(report["xenia_required_bindings_present"].values()):
        report["status"]="BLOCKED_XENIA_HID_BINDINGS_UNVERIFIED"
    report["log_bytes"]=len(text.encode("utf8"))
    report["log_sha256"]=hashlib.sha256(text.encode("utf8")).hexdigest()
    report["log_lines_relevant"]=[
        line[:400] for line in text.splitlines()
        if re.search(r"(?i)(vulkan|llvmpipe|Xenia|loading|exception|"
                     r"crash|failed to launch|controller|keyboard|GetFileSignature)",
                     line)
    ][-35:]
    if not is_real:
        report["note"]=(
            "Only X11 input transportation was exercised: invalid XEX cannot"
            " run SM64 or validate any Xbox buttons. This is NOT a no-crash test.")
        game.unlink(missing_ok=True)
    (outdir/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--xex",default=None,type=Path)
    p.add_argument("--wait-before-seconds",type=float,default=4)
    a=p.parse_args()
    replay(a.binary.absolute(),a.output.absolute(),a.xex,a.wait_before_seconds)

if __name__=="__main__":main()
