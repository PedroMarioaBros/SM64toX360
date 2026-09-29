    .text
    .align 2
    .globl pregame_selector
    .type pregame_selector,@function
pregame_selector:
    mflr 0
    stwu 1, -0x80(1)
    stw 0, 0x78(1)
    stw 30, 0x70(1)
    stw 31, 0x74(1)

    # .mlang base
    lis 30, 0x8304

    # Make print_generic_string_fade fully opaque during pregame.
    lis 11, 0x82e5
    li 10, 255
    stb 10, 0x2f88(11)
    li 10, 0
    stb 10, 0x2f8b(11)

    lwz 31, 0x14(30)       # 0 credits, 1 language selector, 2 done
    cmpwi 31, 0
    beq credits_page
    cmpwi 31, 1
    beq language_page
    li 3, 1
    b finish

credits_page:
    li 3, 92
    li 4, 210
    lwz 5, 0x80(30)
    .long 0x48000001
    li 3, 58
    li 4, 180
    lwz 5, 0x84(30)
    .long 0x48000001
    li 3, 50
    li 4, 155
    lwz 5, 0x88(30)
    .long 0x48000001
    li 3, 42
    li 4, 125
    lwz 5, 0x8c(30)
    .long 0x48000001
    li 3, 51
    li 4, 105
    lwz 5, 0x90(30)
    .long 0x48000001
    li 3, 76
    li 4, 75
    lwz 5, 0x94(30)
    .long 0x48000001
    li 3, 51
    li 4, 55
    lwz 5, 0x90(30)
    .long 0x48000001
    li 3, 105
    li 4, 22
    lwz 5, 0x98(30)
    .long 0x48000001

    bl read_pressed
    andi. 0, 3, 0x8000
    beq return_zero
    li 10, 1
    stw 10, 0x14(30)
    li 10, 0
    stw 10, 0x18(30)
    b return_zero

language_page:
    li 3, 76
    li 4, 195
    lwz 5, 0x9c(30)
    .long 0x48000001
    li 3, 118
    li 4, 145
    lwz 5, 0xa0(30)
    .long 0x48000001
    li 3, 118
    li 4, 115
    lwz 5, 0xa4(30)
    .long 0x48000001
    li 3, 118
    li 4, 85
    lwz 5, 0xa8(30)
    .long 0x48000001

    lwz 31, 0x18(30)
    li 3, 96
    cmpwi 31, 0
    beq star_pt
    cmpwi 31, 1
    beq star_es
    li 4, 85
    b draw_star
star_pt:
    li 4, 145
    b draw_star
star_es:
    li 4, 115
draw_star:
    lwz 5, 0xb0(30)
    .long 0x48000001
    li 3, 104
    li 4, 30
    lwz 5, 0xac(30)
    .long 0x48000001

    bl read_pressed
    mr 9, 3

    andi. 0, 9, 0x0800
    beq check_down
    cmpwi 31, 0
    bne up_dec
    li 31, 2
    b store_selection
up_dec:
    addi 31, 31, -1
    b store_selection

check_down:
    andi. 0, 9, 0x0400
    beq check_confirm
    cmpwi 31, 2
    bne down_inc
    li 31, 0
    b store_selection
down_inc:
    addi 31, 31, 1

store_selection:
    stw 31, 0x18(30)

check_confirm:
    andi. 0, 9, 0x8000
    beq return_zero

    mr 3, 31
    .long 0x48000005       # apply_language
    li 10, 2
    stw 10, 0x14(30)

    lis 11, 0x82e5
    li 10, 0
    stb 10, 0x2f88(11)
    stb 10, 0x2f8b(11)

    .long 0x48000009       # intro_play_its_a_me_mario
    li 3, 1
    b finish

return_zero:
    li 3, 0
finish:
    lwz 30, 0x70(1)
    lwz 31, 0x74(1)
    lwz 0, 0x78(1)
    addi 1, 1, 0x80
    mtlr 0
    blr

read_pressed:
    lis 11, 0x823d
    lwz 10, -0x7670(11)    # gPlayer1Controller
    cmpwi 10, 0
    beq no_controller
    lhz 3, 0x12(10)        # buttonPressed
    blr
no_controller:
    li 3, 0
    blr

    .globl logo_gate
logo_gate:
    lis 11, 0x8304
    lwz 10, 0x14(11)
    cmpwi 10, 2
    beq logo_original
    li 3, 0
    blr
logo_original:
    mflr 12
    .long 0x4800000d       # branch to geo_intro_super_mario_64_logo + 4

    .globl tm_gate
tm_gate:
    lis 11, 0x8304
    lwz 10, 0x14(11)
    cmpwi 10, 2
    beq tm_original
    li 3, 0
    blr
tm_original:
    mflr 12
    .long 0x48000011       # branch to geo_intro_tm_copyright + 4

    .size pregame_selector, .-pregame_selector
