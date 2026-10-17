#!/usr/bin/env python3
"""Probe whether TEST9's CPU test was blind to PPC64 Xbox execution.

Original CI emulated PPC32 (UC_MODE_32) although the Xbox 360 uses a 64-bit
PowerPC CPU. This is a capability test: unsupported PPC64 emulation returns
INCONCLUSIVE, never "PASS hardware". No ROM or XEX is needed.
"""
import json
import traceback
from unittest.mock import patch

from unicorn import Uc, UcError, UC_ARCH_PPC, UC_MODE_BIG_ENDIAN, UC_MODE_64
from test_test9_ppc_runtime import cpu, LANG, PAD, rd32, rd16

def main():
    info={"arch":"PowerPC","requested_mode":"UC_MODE_64 | UC_MODE_BIG_ENDIAN",
          "hardware_proven":False}
    try:
        instance=Uc(UC_ARCH_PPC,UC_MODE_64|UC_MODE_BIG_ENDIAN)
    except (UcError,ValueError,NotImplementedError) as error:
        info["result"]="INCONCLUSIVE_UNICORN_PPC64_NOT_SUPPORTED"
        info["detail"]=str(error)
        info["errno"]=getattr(error,"errno",None)
        print(json.dumps(info,indent=2))
        return
    def make_ppc64(*_args,**_kwargs):
        return Uc(UC_ARCH_PPC, UC_MODE_64|UC_MODE_BIG_ENDIAN)
    import test_test9_ppc_runtime as tests
    try:
        with patch.object(tests,"Uc",side_effect=make_ppc64):
            u,labels,called_original=cpu(0,0,0)
        info["result"]="PPC64_FIRST_FRAME_SIMULATION_PASS"
        info["rendered_labels_count"]=len(labels)
        info["state_after"]=rd32(u,LANG+0x14)
        info["controller_pressed_after"]=rd16(u,PAD+0x12)
    except Exception as error:
        info["result"]="PPC64_FIRST_FRAME_SIMULATION_FAIL"
        info["detail"]=repr(error)
        info["errno"]=getattr(error,"errno",None)
        info["traceback"]=traceback.format_exc(limit=8)
    print(json.dumps(info,indent=2))
    # The outcome informs diagnosis; do not claim Xbox validation.
if __name__=="__main__":
    main()
