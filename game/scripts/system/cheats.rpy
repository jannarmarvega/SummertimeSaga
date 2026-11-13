## Cheat menu: money, stats, map unlocks and choice hints.
## Opened with the "CHEATS" button shown under the top bar during play.

init python:
    import re

    if persistent.cheat_hints is None:
        persistent.cheat_hints = True

    CHEAT_LOCATIONS = [
        "loc_aunt_unlocked", "loc_bank_unlocked", "loc_beach_unlocked", "loc_church_unlocked",
        "loc_clinic_unlocked", "loc_court_unlocked", "loc_dealership_unlocked", "loc_donuts_unlocked",
        "loc_forest_unlocked", "loc_gym_unlocked", "loc_hill_unlocked", "loc_lair_unlocked",
        "loc_library_unlocked", "loc_mall_unlocked", "loc_mia_unlocked", "loc_park_unlocked",
        "loc_pier_unlocked", "loc_pizza_unlocked", "loc_police_unlocked", "loc_pool_unlocked",
        "loc_school_unlocked", "loc_tattoo_unlocked", "loc_trailer_unlocked", "loc_treehouse_unlocked",
        "loc_warehouse_unlocked",
        ]

    def cheat_add_money(amount):
        inventory.money = max(0, inventory.money + amount)

    def cheat_set_stat(attr, value):
        setattr(pStats, attr, max(0, min(10, value)))

    def cheat_unlock_map():
        for name in CHEAT_LOCATIONS:
            setattr(store, name, True)
        renpy.notify("All map locations unlocked")

    def cheat_map_unlocked():
        return all(getattr(store, name, False) for name in CHEAT_LOCATIONS)

    ## --- Choice hints -------------------------------------------------------
    ## Choices hidden by a failed stat/money check are shown greyed out with
    ## their requirement. The game's choice screen already renders captions
    ## starting with "<>" as inactive, so locked choices can't be picked.

    _CHEAT_HINT_NAMES = [
        (r"pStats\.(?:str|strength)\(\)", "Strength"),
        (r"pStats\.(?:int|intelligence)\(\)", "Intelligence"),
        (r"pStats\.(?:dex|dexterity)\(\)", "Dexterity"),
        (r"pStats\.(?:chr|charisma)\(\)", "Charisma"),
        (r"inventory\.money", "Money"),
        ]

    def cheat_requirement(condition):
        """
        Returns the stat/money requirement text for a condition, or "" when the
        choice is hidden for another reason (story progress), so story-gated
        choices stay hidden.
        """
        if re.search(r"\sor\s|\bnot\s*\(", condition):
            return ""
        parts = []
        for clause in re.split(r"\s+and\s+", condition):
            found = False
            for pattern, name in _CHEAT_HINT_NAMES:
                m = re.search(pattern + r"\s*(>=|>|==)\s*(\d+)", clause)
                if m:
                    found = True
                    op, num = m.group(1), int(m.group(2))
                    if op == ">":
                        num += 1
                    if not _cheat_safe_eval(clause):
                        parts.append("{} {}".format(name, num) if name != "Money" else "${}".format(num))
            if not found and not _cheat_safe_eval(clause):
                return ""
        return ", ".join(parts)

    def _cheat_safe_eval(condition):
        try:
            return bool(renpy.python.py_eval(condition))
        except Exception:
            return False

    ## --- Best / avoid analysis ----------------------------------------------
    ## Looks at the script each choice runs (and the labels it jumps/calls into,
    ## a couple of levels deep). Choices that advance quests, relationships,
    ## stats, items or money are "BEST"; choices that lead to a fail/lose label
    ## are "AVOID".

    _CHEAT_PROGRESS = re.compile(
        r"\.(trigger|set|finish|add_event|complete_events|increase|get_item|max_all)\(|"
        r"quest_complete\(|completed_quests\.append|inventory\.money\s*\+=|_unlocked\s*=\s*True")
    _CHEAT_FAIL = re.compile(r"(fail|failure|lose|game_?over|caught)", re.I)
    _cheat_analysis_cache = {}

    def _cheat_scan(nodes, depth, seen, budget):
        """Returns (progress, fail) for a list of AST nodes."""
        import renpy.ast as A
        progress = fail = False
        for node in nodes or []:
            if budget[0] <= 0:
                break
            budget[0] -= 1
            if isinstance(node, A.Python):
                if _CHEAT_PROGRESS.search(getattr(node.code, "source", "") or ""):
                    progress = True
            elif isinstance(node, A.If):
                for _cond, block in node.entries:
                    p, f = _cheat_scan(block, depth, seen, budget)
                    progress = progress or p
                    fail = fail or f
            elif isinstance(node, (A.Jump, A.Call)):
                target = node.target if isinstance(node, A.Jump) else node.label
                if getattr(node, "expression", False) or not isinstance(target, basestring):
                    continue
                if _CHEAT_FAIL.search(target):
                    fail = True
                elif depth > 0 and target not in seen and renpy.has_label(target):
                    seen.add(target)
                    label_node = renpy.game.script.lookup(target)
                    p, f = _cheat_scan(getattr(label_node, "block", []), depth - 1, seen, budget)
                    progress = progress or p
                    fail = fail or f
            elif isinstance(node, A.Menu):
                # A nested menu's outcomes are judged when that menu is shown.
                continue
            elif hasattr(node, "block") and isinstance(node.block, list):
                p, f = _cheat_scan(node.block, depth, seen, budget)
                progress = progress or p
                fail = fail or f
        return progress, fail

    def _cheat_analyze_current_menu():
        try:
            name = renpy.game.context().current
            if name in _cheat_analysis_cache:
                return _cheat_analysis_cache[name]
            node = renpy.game.script.lookup(name)
            result = {}
            for i, (_label, _cond, block) in enumerate(getattr(node, "items", [])):
                if block is not None:
                    # depth 0: judge each choice by its own block only. Following
                    # jumps lands in hub labels that "progress" everything.
                    result[i] = _cheat_scan(block, 0, set(), [400])
            _cheat_analysis_cache[name] = result
            return result
        except Exception:
            return {}

    _CHEAT_BEST = u"{color=#7CFC00}{b}BEST >{/b}{/color} "
    _CHEAT_AVOID = u"{color=#ff6060}{b}AVOID >{/b}{/color} "

    _cheat_original_menu = renpy.exports.menu

    def _cheat_menu(items, *args, **kwargs):
        if persistent.cheat_hints and any(_cheat_safe_eval(c) for _l, c, v in items if v is not None):
            analysis = _cheat_analyze_current_menu()
            visible = [v for _l, c, v in items if v is not None and _cheat_safe_eval(c)]
            progressing = [v for v in visible if analysis.get(v, (False, False))[0] and not analysis.get(v, (False, False))[1]]
            # Only mark BEST when it actually separates the options.
            mark_best = 0 < len(progressing) < len(visible)

            new_items = []
            for label, condition, value in items:
                if value is not None:
                    progress, fail = analysis.get(value, (False, False))
                    if not _cheat_safe_eval(condition):
                        req = cheat_requirement(condition)
                        if req:
                            tag = _CHEAT_BEST if progress and not fail else ""
                            label = u"<>{}LOCKED: {} (needs {})".format(tag, label, req)
                            condition = "True"
                    elif fail:
                        label = _CHEAT_AVOID + label
                    elif mark_best and value in progressing:
                        label = _CHEAT_BEST + label
                new_items.append((label, condition, value))
            items = new_items
        return _cheat_original_menu(items, *args, **kwargs)

    renpy.exports.menu = _cheat_menu

    config.overlay_screens.append("cheat_button")

style cheat_frame:
    background "#101425ee"
    xpadding 30
    ypadding 20

style cheat_text:
    color "#ffffff"
    size 22

style cheat_button:
    background "#3a2a6a"
    hover_background "#6a4ac0"
    insensitive_background "#2a2a2a"
    xpadding 14
    ypadding 8
    xminimum 60

style cheat_button_text:
    color "#ffffff"
    hover_color "#ffffff"
    insensitive_color "#777777"
    size 22
    xalign 0.5

screen cheat_button:
    zorder 50
    if renpy.get_screen("ui") and not renpy.get_screen("cheat_menu"):
        textbutton "CHEATS":
            style "cheat_button"
            text_style "cheat_button_text"
            xpos 1014 xanchor 1.0 ypos 84
            action Show("cheat_menu")

screen cheat_stat_row(label, attr):
    $ value = getattr(pStats, attr)
    hbox:
        spacing 12
        text label style "cheat_text" min_width 170 yalign 0.5
        textbutton "-" style "cheat_button" text_style "cheat_button_text" action Function(cheat_set_stat, attr, value - 1) sensitive value > 0
        text "[value]" style "cheat_text" min_width 40 text_align 0.5 yalign 0.5
        textbutton "+" style "cheat_button" text_style "cheat_button_text" action Function(cheat_set_stat, attr, value + 1) sensitive value < 10
        textbutton "MAX" style "cheat_button" text_style "cheat_button_text" action Function(cheat_set_stat, attr, 10)

screen cheat_menu:
    modal True
    zorder 200

    add "#000a"

    frame:
        style "cheat_frame"
        xalign 0.5 yalign 0.5

        vbox:
            spacing 14

            text "{b}Cheat Menu{/b}" style "cheat_text" size 32 xalign 0.5

            text "{b}Money:{/b} $[inventory.money]" style "cheat_text"
            hbox:
                spacing 8
                textbutton "+100" style "cheat_button" text_style "cheat_button_text" action Function(cheat_add_money, 100)
                textbutton "+1,000" style "cheat_button" text_style "cheat_button_text" action Function(cheat_add_money, 1000)
                textbutton "+10,000" style "cheat_button" text_style "cheat_button_text" action Function(cheat_add_money, 10000)
                textbutton "-1,000" style "cheat_button" text_style "cheat_button_text" action Function(cheat_add_money, -1000)

            null height 6
            text "{b}Stats{/b}" style "cheat_text"
            use cheat_stat_row("Strength", "_str")
            use cheat_stat_row("Intelligence", "_int")
            use cheat_stat_row("Dexterity", "_dex")
            use cheat_stat_row("Charisma", "_chr")
            textbutton "Max all stats" style "cheat_button" text_style "cheat_button_text" action Function(pStats.max_all)

            null height 6
            hbox:
                spacing 8
                if cheat_map_unlocked():
                    textbutton "Map: all unlocked" style "cheat_button" text_style "cheat_button_text" action None
                else:
                    textbutton "Unlock all map locations" style "cheat_button" text_style "cheat_button_text" action Function(cheat_unlock_map)
                textbutton ("Choice hints: ON" if persistent.cheat_hints else "Choice hints: OFF") style "cheat_button" text_style "cheat_button_text" action ToggleField(persistent, "cheat_hints")
                textbutton ("Mini-game skips: ON" if cheat_mode else "Mini-game skips: OFF") style "cheat_button" text_style "cheat_button_text" action ToggleVariable("cheat_mode")

            null height 6
            textbutton "Close" style "cheat_button" text_style "cheat_button_text" xalign 0.5 action Hide("cheat_menu")
