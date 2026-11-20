## Task roadmap: shows where to go next.
##
## Reads the game's own progress (state machines, character event queues and
## phone side quests) and turns it into a list of tasks, each tied to a town
## map location. Used by:
##   - the ROADMAP button (any screen with the top bar) -> full task list
##   - the town map -> markers on locations with tasks, a "NEXT" banner and a
##     hover panel with that location's tasks and opening hours.
##
## Everything here is read-only except roadmap_finish(), which the task list
## calls when you click a task and confirm "Finish" (auto-complete cheat).
## All lookups are wrapped so a missing variable can't crash the game.

init -1 python:

    if persistent.roadmap_markers is None:
        persistent.roadmap_markers = True

    ## ---------------------------------------------------------------------
    ## Map locations: name (as the map hover shows it), unlock variable,
    ## opening rule, icon position and size (for marker placement).
    ## Opening rules mirror the town_map screen buttons.
    ## ---------------------------------------------------------------------
    RM_LOCATIONS = [
        ("Home",              None,                      "always",      837, 613,  97,  79),
        ("Erik's House",      None,                      "day_evening", 728, 593,  89,  98),
        ("School",            "loc_school_unlocked",     "day",         407, 233, 215, 218),
        ("Basket Ball Court", "loc_court_unlocked",      "not_night",   417, 220,  57,  81),
        ("Diane's House",     "loc_aunt_unlocked",       "day_evening", 468,  62,  75, 108),
        ("Mia's House",       "loc_mia_unlocked",        "not_night",   621, 592,  84, 115),
        ("Gym",               "loc_gym_unlocked",        "not_night",   851, 320, 135, 130),
        ("Library",           "loc_library_unlocked",    "day",         697, 323, 134, 116),
        ("Park",              "loc_park_unlocked",       "not_night",   310, 179, 102,  93),
        ("Pool",              "loc_pool_unlocked",       "day_evening", 462, 578, 110, 131),
        ("Mall",              "loc_mall_unlocked",       "day",         791,  79, 203, 138),
        ("Bank",              "loc_bank_unlocked",       "day",         708, 198, 113, 120),
        ("Pizzeria",          "loc_pizza_unlocked",      "day",          98, 338, 118, 106),
        ("Car Dealership",    "loc_dealership_unlocked", "day_weekday", 104, 176, 134,  84),
        ("Pier",              "loc_pier_unlocked",       "not_night",    58, 529,  77, 130),
        ("Forest",            "loc_forest_unlocked",     "not_night",     0, 107,  95, 182),
        ("Church",            "loc_church_unlocked",     "church",      588,  48,  51, 113),
        ("Police Station",    "loc_police_unlocked",     "day",         834, 227, 120,  89),
        ("Tattoo Parlor",     "loc_tattoo_unlocked",     "day",         259,  47,  82,  99),
        ("Beach",             "loc_beach_unlocked",      "not_night",   204, 570, 108,  97),
        ("Hill",              "loc_hill_unlocked",       "not_night",   692,  -3, 143, 113),
        ("Clinic",            "loc_clinic_unlocked",     "not_night",   342, 499, 100, 113),
        ("Trailer Park",      "loc_trailer_unlocked",    "not_night",     3, 294,  62,  95),
        ("Treehouse",         "loc_treehouse_unlocked",  "not_night",   805, 512,  48,  59),
        ("Donut Shop",        "loc_donuts_unlocked",     "not_night",   982, 222,  38, 103),
        ("Warehouse",         "loc_warehouse_unlocked",  "not_night",   110,  58, 110, 110),
        # Aqua storyline; its map icon only exists when the private art is installed.
        ("Lair",              "loc_lair_unlocked",       "not_night",    10, 675,  90,  80),
        ]
    RM_LOC = dict((l[0], l) for l in RM_LOCATIONS)
    RM_LOC_ORDER = dict((l[0], i) for i, l in enumerate(RM_LOCATIONS))

    RM_HOURS = {
        "always":      "Always open",
        "day":         "Open morning & afternoon",
        "day_evening": "Open morning to evening",
        "not_night":   "Open morning to evening",
        "day_weekday": "Open weekday mornings & afternoons",
        "church":      "Open morning to evening",
        }

    ## ---------------------------------------------------------------------
    ## Steps: key -> (who, location, room, what to do, when)
    ## Keys are state names (S_...), event names, or quest names.
    ## A step with location None is shown without a map marker.
    ## ---------------------------------------------------------------------
    SLEEP = "Go to bed in your bedroom to move the story forward."
    RM_STEPS_ORDERED = [
        # --- Mom -----------------------------------------------------------
        ("S_mom_start", ("Mom", "Home", "Kitchen", "Have breakfast with Mom.", "Morning")),
        ("S_mom_relaxing", ("Mom", "School", "", "Go to school for your first day back.", "Morning")),
        ("S_mom_overheard", ("Mom", "Home", "", "Head back home, Mom is on the phone.", "")),
        ("S_mom_debt_call", ("Mom", "Home", "Kitchen", "Talk to Mom about the money problems.", "Morning")),
        ("S_mom_lawn_delay", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_lawn_help", ("Mom", "Home", "Entrance", "Talk to Mom about mowing the lawn.", "Daytime")),
        ("S_mom_fill_mower", ("Mom", "Home", "Garage", "Fill the lawnmower with gas. No gas can? Buy one at CONSUM-R in the Mall.", "Daytime")),
        ("S_mom_mow_lawn", ("Mom", "Home", "Front yard", "Mow the lawn.", "Daytime")),
        ("S_mom_clothes_dirty", ("Mom", "Home", "Entrance", "Go inside, your clothes need washing.", "")),
        ("S_mom_wash_clothes", ("Mom", "Home", "Basement", "Wash your clothes in the basement.", "")),
        ("S_mom_sleeping", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_doorbell", ("Mom", "Home", "Entrance", "Someone is at the door. Go check it.", "Morning")),
        ("S_mom_debt_collectors", ("Mom", "Home", "Entrance", "Deal with the men at the door.", "")),
        ("S_mom_mrsj_visit_delay", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_mrsj_visit", ("Mom", "Home", "Front yard", "Go outside, Mrs. Johnson is visiting Mom.", "Daytime")),
        ("S_mom_pipe_delay", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_pipe_help", ("Mom", "Home", "Entrance", "Talk to Mom about the broken pipe.", "")),
        ("S_mom_sis_check", ("Mom", "Home", "Bathroom", "Check on your sister in the bathroom.", "")),
        ("S_mom_close_valve", ("Mom", "Home", "Basement", "Close the water valve in the basement.", "")),
        ("S_mom_pipe_check", ("Mom", "Home", "Bathroom", "Look at the pipe. You need a wrench (CONSUM-R, Mall, $50).", "")),
        ("S_mom_fix_pipe", ("Mom", "Home", "Bathroom", "Fix the pipe with the wrench.", "Daytime")),
        ("S_mom_sis_boobs_afterthoughts", ("Mom", "Home", "Upstairs hallway", "Walk through the upstairs hallway.", "")),
        ("S_mom_shower_delay", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_shower_peek", ("Mom", "Home", "Bathroom", "Go to the upstairs bathroom.", "Morning")),
        ("S_mom_shower_peek_after", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_bad_guys_driveby", ("Mom", "Home", "", "Leave the house and open the town map.", "")),
        ("S_mom_chores_delay", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_vacuum_help", ("Mom", "Home", "Entrance", "Help Mom vacuum. If she isn't there, sleep and try the next day.", "Daytime")),
        ("S_mom_dishes_help", ("Mom", "Home", "Kitchen", "Help Mom wash the dishes. If she isn't there, try the next day.", "Daytime")),
        ("S_mom_laundry_help", ("Mom", "Home", "Basement", "Help Mom with the laundry. If she isn't there, try the next day.", "Afternoon")),
        ("S_mom_lotion_adventure", ("Mom", "Home", "Basement", "Talk to Mom in the basement.", "Daytime")),
        ("S_mom_search_panties", ("Mom", "Home", "Mom's bedroom", "Look for Mom's panties.", "")),
        ("S_mom_panties_masturbation", ("Mom", "Home", "Mom's bedroom", "Go to Mom's bedroom.", "")),
        ("S_mom_movie_night", ("Mom", "Home", "Entrance", "Talk to Mom about movie night.", "Evening")),
        ("S_mom_romance_movie", ("Mom", "Home", "Living room", "Watch the movie with Mom.", "Evening")),
        ("S_mom_movie_afterthoughts", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_hang_out", ("Mom", "Home", "Entrance", "Talk to Mom, she wants to hang out.", "Daytime")),
        ("S_mom_hang_out_return", ("Mom", "Home", "", "Talk to Mom again and agree to go out with her.", "Daytime")),
        ("S_mom_mall_outing", ("Mom", "Mall", "", "Go to the Mall with Mom.", "Daytime")),
        ("S_mom_cupid_store", ("Mom", "Mall", "Cupid (2nd floor)", "Meet Mom in the Cupid store.", "Daytime")),
        ("S_mom_choose_gift", ("Mom", "Mall", "Cupid (2nd floor)", "Pick a necklace from the display.", "Daytime")),
        ("S_mom_show_necklace", ("Mom", "Mall", "Cupid (2nd floor)", "Show Mom the necklace.", "Daytime")),
        ("S_mom_dressing_room", ("Mom", "Mall", "Cupid (2nd floor)", "Check on Mom in the dressing room.", "Daytime")),
        ("S_mom_smith_dream", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_spy", ("Mom", "Home", "Mom's bedroom", "Go to Mom's bedroom.", "")),
        ("S_mom_solo_dream", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_kissing_practice", ("Mom", "Home", "", "Talk to Mom.", "")),
        ("S_mom_shower_walk_in", ("Mom", "Home", "Bathroom", "Go to the upstairs bathroom.", "Morning")),
        ("S_mom_car_broken", ("Mom", "Home", "Entrance", "Talk to Mom about her car.", "")),
        ("S_mom_check_car", ("Mom", "Home", "Garage", "Check Mom's car in the garage.", "")),
        ("S_mom_car_condition", ("Mom", "Home", "", "Tell Mom what's wrong with the car.", "")),
        ("S_mom_fix_car", ("Mom", "Car Dealership", "", "Sort out the car at the dealership, then tell Mom.", "Weekday, daytime")),
        ("S_mom_car_fixed", ("Mom", "Home", "", "Go home and talk to Mom.", "")),
        ("S_mom_panties_masturbation_again", ("Mom", "Home", "Mom's bedroom", "Go to Mom's bedroom.", "")),
        ("S_mom_night_visit", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_bad_guys_revisit", ("Mom", "Home", "Front yard", "The debt collectors are back. Go home.", "")),
        ("S_mom_story_delay", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_sleepover_offer", ("Mom", "Home", "Upstairs hallway", "Walk through the upstairs hallway.", "Night")),
        ("S_mom_sleepover", ("Mom", "Home", "Bedroom", "Spend the night with Mom, then sleep.", "Night")),
        ("S_mom_sleepover_wakeup", ("Mom", "Home", "Mom's bedroom", "Wake up in Mom's bedroom.", "Morning")),
        ("S_mom_diane_visit", ("Mom", "Home", "Kitchen", "Aunt Diane is visiting. Talk to Mom.", "")),
        ("S_mom_dinner", ("Mom", "Home", "Kitchen", "Help Mom prepare dinner.", "")),
        ("S_mom_dinner_outfit", ("Mom", "Home", "Mom's bedroom", "Give Mom your opinion on her dinner outfit.", "")),
        ("S_mom_dinner_fish", ("Mom", "Pier", "", "Get a fish for dinner (fish at the Pier), then bring it to Mom in the kitchen.", "Daytime")),
        ("S_mom_diane_dinner", ("Mom", "Home", "Dining room", "Have dinner with Mom and Diane.", "Evening")),
        ("S_mom_movie_night_two", ("Mom", "Home", "", "Movie night again. Talk to Mom.", "Evening")),
        ("S_mom_romance_movie_two", ("Mom", "Home", "Living room", "Watch the movie with Mom.", "Evening")),
        ("S_mom_movie_afterthoughts_two", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_night_visit_two", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_midnight_noises", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_midnight_search", ("Mom", "Home", "Backyard", "Look for Mom. Check the backyard.", "Night")),
        ("S_mom_fetch_towel", ("Mom", "Home", "Bathroom", "Get a towel and bring it to Mom at the backyard pool.", "Night")),
        ("S_mom_midnight_swim_after", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_night_visit_three", ("Mom", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mom_note_delay", ("Mom", "Home", "Bedroom", "Sleep. Something will happen in a few days.", "Night")),
        ("S_mom_note", ("Mom", "Home", "Bedroom", "Read the note Mom left.", "")),
        ("S_mom_fetch_laundry", ("Mom", "Home", "Mom's bedroom", "Pick up the laundry in Mom's bedroom.", "")),
        ("S_mom_give_laundry", ("Mom", "Home", "Basement", "Bring the laundry to Mom in the basement.", "")),

        # --- Mia / Helen / Harold -----------------------------------------
        ("S_mia_start", ("Mia", "School", "Science classroom", "Talk to Mia.", "Morning")),
        ("S_mia_do_homework", ("Mia", "Mia's House", "", "Study with Mia (do your homework).", "Afternoon")),
        ("S_mia_wait_homework", ("Mia", "Mia's House", "", "Bring Mia the finished homework.", "Afternoon")),
        ("S_mia_parent_blocking", ("Mia", "Mia's House", "Entrance", "Helen won't let you in. Talk to Mia at school.", "Morning")),
        ("S_mia_consult", ("Mia", "Mia's House", "", "Ask Mia how to get night study sessions back.", "Afternoon")),
        ("S_mia_impress_harold", ("Mia", "Donut Shop", "", "Get Harold's favourite donut (Donut Shop), then bring it to him at the Police Station.", "Daytime")),
        ("S_mia_parent_unblock", ("Mia", "Mia's House", "", "Ask Mia whether you're allowed back.", "Afternoon")),
        ("S_mia_tattoo_help", ("Mia", "Mia's House", "", "Talk to Mia about her tattoo.", "Afternoon")),
        ("S_mia_find_easel", ("Mia", "School", "Art classroom", "Find an easel in the art classroom.", "Daytime")),
        ("S_mia_draw_tattoo", ("Mia", "School", "Art classroom", "Draw a tattoo design at the easel.", "Daytime")),
        ("S_mia_show_tattoo", ("Mia", "Mia's House", "", "Show Mia the tattoo you drew.", "Afternoon")),
        ("S_mia_get_tattoo", ("Mia", "Tattoo Parlor", "", "Meet Mia at the Tattoo Parlor.", "Saturday, daytime")),
        ("S_mia_buy_tattoo", ("Mia", "Tattoo Parlor", "", "Watch Mia get her tattoo.", "Saturday, daytime")),
        ("S_mia_return_favor", ("Mia", "School", "Science classroom", "Talk to Mia, she wants to return the favour.", "Morning")),
        ("S_mia_night_visit", ("Mia", "Mia's House", "", "Visit Mia at night.", "Evening")),
        ("S_mia_strip_aftermath", ("Mia", "School", "Science classroom", "Ask Mia what happened after she got caught.", "Morning")),
        ("S_mia_midnight_call", ("Mia", "Home", "Bedroom", "Check the message Mia sent to your phone.", "Night")),
        ("S_mia_midnight_help", ("Mia", "Mia's House", "", "Go to Mia's house, she needs help.", "Night")),
        ("S_mia_locked_room", ("Mia", "Mia's House", "Upstairs", "Get into the locked room.", "Night")),
        ("S_mia_need_space", ("Mia", None, "", "Leave Mia and her parents alone for a while (sleep a few days).", "")),
        ("S_mia_concerning_visit", ("Mia", "Mia's House", "", "Visit Mia, you haven't heard from her.", "Afternoon")),
        ("S_mia_helen_fight", ("Mia", "Mia's House", "Entrance", "Go to Mia's house.", "Afternoon")),
        ("S_mia_helen_talk", ("Mia", "Mia's House", "Helen's bedroom", "Try to talk to Helen.", "Afternoon")),
        ("S_mia_helen_refusal", ("Mia", "Mia's House", "", "Talk to Mia about Helen.", "Afternoon")),
        ("S_mia_church_plan", ("Mia", "Church", "", "Find a way to convince Helen at the church.", "Daytime")),
        ("S_mia_convince_helen", ("Mia", "Church", "Confessional", "Talk to Helen in the confessional.", "Weekend morning")),
        ("S_mia_priest_act", ("Mia", "Church", "Confessional", "Pretend to be the priest to convince Helen.", "Weekend morning")),
        ("S_mia_return_priest_outfit", ("Mia", "Church", "Nun's room", "Return the priest outfit.", "Daytime")),
        ("S_mia_nun_thoughts", ("Mia", "Church", "", "Go back to the church.", "Daytime")),
        ("S_mia_helen_change_news", ("Mia", "Mia's House", "", "Tell Mia that Helen is willing to change.", "Afternoon")),
        ("S_mia_waiting_for_harold", ("Mia", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mia_urgent_message", ("Mia", "Home", "Bedroom", "Check Mia's urgent message on your phone.", "Morning")),
        ("S_mia_urgent_help", ("Mia", "Mia's House", "", "Go to Mia's house, Harold is missing.", "")),
        ("S_mia_clues", ("Mia", "Police Station", "", "Look for clues about Harold (Police Station, Helen's bedroom).", "Daytime")),
        ("S_mia_search_desk", ("Mia", "Police Station", "Harold's office", "Search Harold's desk for clues.", "Daytime")),
        ("S_mia_find_harold", ("Mia", "Hill", "", "Look for Harold at Raven Hill.", "Daytime")),
        ("S_mia_harold_found_news", ("Mia", "Mia's House", "Entrance", "Tell Mia and Helen that Harold is okay.", "")),
        ("S_mia_angelicas_patience", ("Mia", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mia_angelicas_impatience", ("Mia", "Home", "Entrance", "Angelica is at your door.", "")),
        ("S_mia_church_night_visit", ("Mia", "Church", "Angelica's room", "Visit Angelica at the church.", "Evening")),
        ("S_mia_find_sinners", ("Mia", "Mia's House", "Helen's bedroom", "Ask Helen to join Angelica's sacrament.", "Afternoon")),
        ("S_mia_church_sacrement", ("Mia", "Church", "Angelica's room", "Go with Helen to the first sacrament.", "Evening")),
        ("S_mia_glasses_favor", ("Mia", "School", "", "Talk to Mia at school.", "Morning")),
        ("S_mia_harold_gift", ("Mia", "Police Station", "Harold's office", "Give Harold his glasses.", "Daytime")),
        ("S_mia_inmate_status", ("Mia", "Police Station", "Basement cells", "Check on the inmate transfer in the basement.", "Daytime")),
        ("S_mia_harold_backup", ("Mia", "Police Station", "Harold's office", "Tell Harold that Yumi needs backup.", "Daytime")),
        ("S_mia_harold_to_the_rescue", ("Mia", "Police Station", "Basement cells", "Go back to the cells.", "Daytime")),
        ("S_mia_harold_yumi_out", ("Mia", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mia_unexpected_visit", ("Mia", "Mia's House", "", "Pay Mia a visit.", "Afternoon")),
        ("S_mia_helen_outfit_request", ("Mia", "Mall", "Pink (2nd floor)", "Buy the red corset lingerie at Pink, then give it to Helen.", "Daytime")),
        ("S_mia_angelicas_delay", ("Mia", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mia_angelicas_home_visit", ("Mia", "Home", "Entrance", "Angelica is at your door.", "Morning")),
        ("S_mia_angelicas_order", ("Mia", "Mall", "Pink (2nd floor)", "Buy a whip at Pink for Angelica.", "Daytime")),
        ("S_mia_angelicas_whip", ("Mia", "Church", "Angelica's room", "Bring the whip to Angelica.", "Evening")),
        ("S_mia_helen_condition", ("Mia", "Mia's House", "Helen's bedroom", "Check on Helen.", "Afternoon")),
        ("S_mia_favor", ("Mia", "Mia's House", "", "Mia has a favour to ask.", "Afternoon")),
        ("S_mia_convince_harold", ("Mia", "Police Station", "Harold's office", "Convince Harold to go to dinner with Mia and Helen.", "Daytime")),
        ("S_mia_stolen_goods", ("Mia", "Park", "Bushes", "Find the stolen goods in the park bushes.", "Daytime")),
        ("S_mia_return_goods", ("Mia", "Police Station", "Harold's office", "Return the stolen goods to Harold.", "Daytime")),
        ("S_mia_angelicas_final_delay", ("Mia", "Home", "Bedroom", SLEEP, "Night")),
        ("S_mia_angelicas_final_home_visit", ("Mia", "Home", "Entrance", "Angelica is at your door.", "Morning")),
        ("S_mia_harolds_thoughts", ("Mia", "Police Station", "Harold's office", "Ask Harold about Helen.", "Daytime")),
        ("S_mia_angelicas_final_request", ("Mia", "Church", "Angelica's room", "Hear Angelica's final request.", "Evening")),
        ("S_mia_helens_final_sacrament", ("Mia", "Church", "Angelica's room", "Attend Helen's final sacrament.", "Evening")),
        ("S_mia_route_split", ("Mia", "Mia's House", "Entrance", "Go to Mia's house. You'll choose between Mia and Helen.", "")),
        ("S_mia_study_sex", ("Mia", "Mia's House", "Mia's bedroom", "Study with Mia.", "Evening")),
        ("S_helen_route_split", ("Helen", "Mia's House", "Entrance", "Go to Mia's house. You'll choose between Mia and Helen.", "")),
        ("S_helen_harold_moved_on", ("Helen", "Mia's House", "Entrance", "Visit Mia's house.", "")),
        ("S_helen_mia_breakdown", ("Helen", "Police Station", "Harold's office", "Talk to Harold.", "Daytime")),
        ("S_helen_master_servant_fun", ("Helen", "Mia's House", "Helen's bedroom", "Visit Helen.", "Afternoon")),
        ("S_helen_aftersex_mia_suspicious", ("Helen", "Mia's House", "Upstairs", "Talk to Mia upstairs.", "")),

        # --- Others ---------------------------------------------------------
        ("S_terry_start", ("Terry", "Pier", "", "Talk to Terry, the fisherman.", "Daytime")),
        ("S_terry_secret", ("Terry", "Pier", "", "Ask Terry about his fishing secret.", "Daytime")),
        ("S_terry_lure", ("Terry", "Pier", "", "Ask Terry about his lure.", "Daytime")),
        ("S_terry_nemesis", ("Terry", "Pier", "", "Find out why Terry is drunk.", "Daytime")),
        ("S_terry_drunk", ("Terry", None, "", "Terry is drunk today. Try again tomorrow.", "")),
        ("S_terry_trade", ("Terry", "Pier", "", "Find the Golden Compass (Aqua's story), then trade it to Terry for his lure.", "Daytime")),
        ("S_terry_bored", ("Terry", "Pier", "", "Ask Terry about retiring (after Aqua's mating request).", "Daytime")),
        ("S_terry_retire", ("Terry", "Pier", "Fishing chair", "Catch Tigger with the special lure, then show it to Terry.", "Daytime")),
        ("S_terry_tigger_sign", ("Terry", "Pier", "", "Visit Terry to see Tigger mounted.", "Daytime")),
        ("S_roz_start", ("Roz", "Clinic", "", "Visit Roz at the Clinic.", "Daytime")),
        ("S_roz_sexy_time", ("Roz", "Clinic", "", "Visit Roz at the Clinic.", "Daytime")),
        ("S_dex_start", ("Dexter", "Basket Ball Court", "", "Check out the basketball court.", "Daytime")),
        ("S_dex_flirting", ("Dexter", "Basket Ball Court", "", "Talk to Dexter and challenge him.", "Daytime")),

        # --- Aqua (needs the private/ art) -----------------------------------
        ("S_aqua_start", ("Aqua", "Pier", "", "Ask Terry about his fishing secret.", "Daytime")),
        ("S_aqua_boatsmith_search", ("Aqua", "Clinic", "", "Ask Roz about ancestry to get the Obituary Records, then read them in your backpack.", "Daytime")),
        ("S_aqua_graveyard_search", ("Aqua", "Church", "Graveyard", "Find Ben Dover's tombstone in the graveyard.", "Daytime")),
        ("S_aqua_bell_search", ("Aqua", "Church", "Bell tower", "Look at the big bell up the church stairs.", "")),
        ("S_aqua_altar_search", ("Aqua", "Forest", "Altar", "Solve the stone altar puzzle. The scroll in the Hill's tree hole helps.", "Evening")),
        ("S_aqua_treasure_search", ("Aqua", "Beach", "Island", "Dig at the island statue. Needs the shovel from your garage.", "Daytime")),
        ("S_aqua_treasure_unlock", ("Aqua", "Beach", "Island", "Open the chest: code 1-5-1-3 plus the key from Larry's stash in the park bushes.", "Daytime")),
        ("S_aqua_trade", ("Aqua", "Pier", "", "Trade the Golden Compass to Terry for his special lure.", "Daytime")),
        ("S_aqua_fishing", ("Aqua", "Pier", "Fishing chair", "Fish with the golden lure and cast it low, near the dock.", "Daytime")),
        ("S_aqua_chase", ("Aqua", "Pier", "Fishing chair", "Use the fishing chair, talk to Aqua and dive after her.", "Daytime")),
        ("S_aqua_squid_gaurd", ("Aqua", "Pier", "", "Beat the giant squid in the fight minigame.", "")),
        ("S_aqua_maze", ("Aqua", "Pier", "Lair entrance", "Swim the cave maze: middle, middle, left, left, middle, right, middle.", "")),
        ("S_aqua_lair", ("Aqua", None, "", "Swim out of the maze into Aqua's lair.", "")),
        ("S_aqua_found", ("Aqua", "Lair", "", "Talk to Aqua to get your lure back.", "")),
        ("S_aqua_mating_proposal", ("Aqua", "Lair", "", "Ask Aqua about mating and offer to help (needs 7 Charisma).", "")),
        ("S_aqua_valor_test", ("Aqua", "Pier", "", "Ask Terry about retiring, catch Tigger with the special lure, then show it to Terry.", "Daytime")),
        ("S_aqua_mate", ("Aqua", "Lair", "", "Visit Aqua and mate with her.", "")),
        ("S_aqua_seasucc_intro", ("Aqua", "Lair", "Sea throne", "Meet SeaSucc on the throne.", "")),
        ("S_aqua_seasucc_mushroom", ("Aqua", "Forest", "", "Pick the Falicum mushroom in the forest, then feed it to SeaSucc in the Lair.", "")),

        # --- Sister ---------------------------------------------------------
        ("sis_breakfast", ("Sister", "Home", "Dining room", "Have breakfast with your sister.", "Morning")),
        ("sis_telescope01", ("Sister", "Home", "Bedroom", "Use the telescope in your bedroom.", "Morning")),
        ("sis_telescope02", ("Sister", "Home", "Bedroom", "Use the telescope in your bedroom.", "Morning")),
        ("sis_telescope03", ("Sister", "Home", "Bedroom", "Use the telescope in your bedroom.", "Morning")),
        ("sis_webcam01", ("Sister", "Home", "Bedroom", "Use your computer's webcam app.", "Night")),
        ("sis_webcam02", ("Sister", "Home", "Bedroom", "Use your computer's webcam app.", "Night")),
        ("sis_webcam03", ("Sister", "Home", "Bedroom", "Use your computer's webcam app.", "Night")),
        ("sis_panty01", ("Sister", "Home", "Sister's bedroom", "Buy a pair of panties from your sister ($100) for Master Somrak.", "Daytime")),
        ("sis_panty02", ("Sister", "Home", "Sister's bedroom", "Ask your sister for more panties.", "")),
        ("sis_panty03", ("Sister", "Home", "Sister's bedroom", "Ask your sister for more panties.", "")),
        ("sis_panty04", ("Sister", "Home", "Sister's bedroom", "Ask your sister for more panties.", "")),
        ("sis_hallway01", ("Sister", "Home", "Upstairs hallway", "Walk through the upstairs hallway.", "")),
        ("sis_hallway02", ("Sister", "Home", "Upstairs hallway", "Walk through the upstairs hallway.", "")),
        ("sis_couch01", ("Sister", "Home", "Living room", "Join your sister on the couch.", "Evening")),
        ("sis_couch02", ("Sister", "Home", "Living room", "Join your sister on the couch.", "Evening")),
        ("sis_couch03", ("Sister", "Home", "Living room", "Join your sister on the couch.", "Evening")),
        ("sis_shower_cuddle01", ("Sister", "Home", "Bathroom", "Peep on your sister in the shower (some mornings), or sneak into her bed at night and cuddle.", "")),
        ("sis_shower_cuddle02", ("Sister", "Home", "Bathroom", "Go inside the shower with your sister (some mornings), or sneak into her bed at night and cuddle.", "")),
        ("sis_shower_cuddle03", ("Sister", "Home", "Bathroom", "Join your sister in the shower and beg (some mornings), or sneak into her bed at night and squeeze her boobs.", "")),
        ("sis_shower_cuddle04", ("Sister", "Home", "Bathroom", "Join your sister in the shower and beg (some mornings), or sneak into her bed at night and rub her pussy.", "")),
        ("sis_final", ("Sister", "Home", "Sister's bedroom", "Talk to your sister.", "Daytime")),
        ("sis_final2", ("Sister", "Home", "Sister's bedroom", "Get the cheerleader outfit (attic) and handcuffs (Pink, Mall, $50), then choose 'Cam show' with your sister.", "Daytime")),
        ("sis_shower_cuddle05", ("Sister", "Home", "Bathroom", "With DEX 7+, join your sister in the shower (some mornings) or sneak into her bed at night, and put it inside.", "")),
        ("sis_webcam04", ("Sister", "Mall", "Pink (2nd floor)", "Buy the Bad Monster at Pink ($500), then give it to your sister ('Need toys?').", "Daytime")),

        # --- Player / school -------------------------------------------------
        ("roxxy_homework_copy01", ("Roxxy", "School", "", "Go to school with the finished homework; Roxxy asks to copy it.", "Daytime")),
        ("intense_gymercise", ("Coach", "School", "Courtyard", "Talk to the coach in the courtyard.", "Morning")),
        ("roxxy_shower", ("Roxxy", "School", "Boys' locker room", "Go to the boys' locker room.", "Morning")),
        ("crystal_intro", ("Crystal", "Trailer Park", "Trailer interior", "Talk to Crystal in her trailer.", "Daytime")),

        # --- Aunt Diane ------------------------------------------------------
        ("aunt_mouse_attack", ("Diane", "Diane's House", "Kitchen", "Help Aunt Diane, she's scared of something.", "")),
        ("aunt_drunken_splur", ("Diane", "Diane's House", "Bedroom", "Check on Aunt Diane in her bedroom.", "Evening")),
        ("aunt_breeding_guide", ("Diane", "Library", "Front desk", "Find a book about milk production.", "Daytime")),
        ("aunt_breeding_bull", ("Diane", "Diane's House", "Kitchen", "Talk to Aunt Diane in the kitchen.", "Daytime")),
        ("aunt_breeding_help", ("Diane", "Diane's House", "Shed", "Meet Aunt Diane in the shed.", "Daytime")),

        # --- Erik / Mrs. Johnson ---------------------------------------------
        ("erik_intro", ("Erik", "Erik's House", "", "Visit Erik.", "Daytime")),
        ("erik_favor", ("Erik", "Erik's House", "", "Ask Erik for a favour.", "")),
        ("erik_favor_2", ("Erik", "School", "Cafeteria", "Tell Kevin in the cafeteria that Erik will take over his duties.", "Morning")),
        ("erik_card_hunt", ("Erik", "Erik's House", "Basement", "Find Erik's card deck in his basement, then give it to him.", "")),
        ("erik_crown_card", ("Erik", "Erik's House", "", "Bring Erik the 'Cock Crown of Thorns' card.", "")),
        ("erik_orcette", ("Erik", "Home", "Bedroom computer", "Order Erik's package online, then give it to him.", "")),
        ("erik_orcette_2", ("Erik", "Erik's House", "", "Give Erik the package.", "")),
        ("erik_bullying", ("Erik", "Home", "Entrance", "Leave your house.", "Morning")),
        ("erik_bullying_2", ("Erik", "School", "", "Go to school.", "Morning")),
        ("erik_bullying_3", ("Erik", "Home", "Bedroom", SLEEP, "Night")),
        ("erik_vr", ("Erik", "Mall", "Comic store", "Buy the VR headset at the comic store, then bring it to Erik.", "Daytime")),
        ("erik_breastfeeding", ("Erik", "Erik's House", "Erik's room", "Visit Erik in his room.", "")),
        ("erik_breastfeeding_2", ("Erik", "Erik's House", "Entrance", "Talk to Mrs. Johnson after walking in on her and Erik.", "")),
        ("erik_thief", ("Erik", "Home", "Bedroom", "Sleep in your bedroom; when you hear a noise at night, use the telescope. Then catch the thief in Erik's backyard (needs DEX 5).", "Night")),
        ("erik_thief_2", ("Erik", "Erik's House", "Entrance", "Visit Erik's house so Mrs. Johnson can thank you.", "")),
        ("erik_father_forgive", ("Erik", "Police Station", "Cells", "Visit Larry in the police cells, then pass his message to Erik.", "Daytime")),
        ("erik_father_treasure", ("Erik", "Park", "Bushes", "Search the park bushes for Larry's stash.", "Daytime")),
        ("erik_path_split", ("Erik", "Erik's House", "", "Talk to Erik or Mrs. Johnson to choose a path.", "")),
        ("erik_gf", ("Erik", "Erik's House", "", "Talk to Erik about getting a girlfriend.", "")),
        ("erik_gf_2", ("Erik", "Erik's House", "Entrance", "Visit Erik's house to see him with June.", "")),
        ("erik_gf_stolen", ("Erik", "Erik's House", "", "Tell Erik that June isn't interested in him.", "")),
        ("erik_sex_ed", ("Erik", "Erik's House", "Erik's room", "Talk to Erik.", "")),
        ("mrsj_intro", ("Mrs. Johnson", "Erik's House", "Entrance", "Visit Erik's house.", "Afternoon or evening")),
        ("mrsj_yoga_intro", ("Mrs. Johnson", "Gym", "Yoga room", "Say hi to Mrs. Johnson in the yoga room.", "Afternoon")),
        ("mrsj_yoga_help", ("Mrs. Johnson", "Gym", "Yoga room", "Help Mrs. Johnson at the yoga class.", "Afternoon")),
        ("mrsj_yoga_help_2", ("Mrs. Johnson", "Erik's House", "Entrance", "Talk to Mrs. Johnson.", "")),
        ("mrsj_poker_night", ("Mrs. Johnson", "Erik's House", "Basement", "Invite Mrs. Johnson to poker (CHA 5), win strip poker at night, then join her in the backroom and make her cum.", "Evening")),
        ("mrsj_poker_night_2", ("Mrs. Johnson", "Erik's House", "Entrance", "Visit Erik's house and talk to Mrs. Johnson about poker night.", "")),
        ("mrsj_sex_ed", ("Mrs. Johnson", "Clinic", "2nd floor storage", "Get birth control pills from the Clinic storage room.", "Daytime")),
        ("roz_intro", ("Roz", "Clinic", "Front desk", "Talk to Roz at the Clinic front desk.", "Daytime")),
        ("roz_storage", ("Roz", "Clinic", "2nd floor", "Get the hospital access card for Roz.", "Daytime")),
        ("roz_trick", ("Roz", "Clinic", "2nd floor", "Roz left her desk: take the access card from her front-desk locker, then open the 2nd floor storage room.", "Daytime")),
        ("grace_intro", ("Grace", "Tattoo Parlor", "", "Talk to Grace and pick 'You look familiar.' (without Mia there).", "Daytime")),

        # --- Anna / June -----------------------------------------------------
        ("anna_intro", ("Anna", "Gym", "Yoga room", "Help Mrs. Johnson at the yoga class; you meet Anna.", "Evening")),
        ("anna_missing_pup", ("Anna", "Forest", "", "Find Anna's dog in the forest, then bring it to her at the Park.", "Daytime")),
        ("june_intro", ("June", "Erik's House", "Erik's room", "Visit Erik's room.", "Afternoon")),
        ("june_intro_2", ("June", "Erik's House", "", "Talk to Mrs. Johnson about Erik's girlfriend.", "")),
        ("june_erik_help", ("June", None, "", "Open the town map during the day.", "Daytime")),
        ("june_mc_help", ("June", None, "", "Open the town map during the day.", "Daytime")),
        ("june_mc_help_2", ("June", "Home", "Bedroom", "Play the orc game with June in your bedroom.", "Evening")),
        ("june_cosplay", ("June", "Mall", "Comic store", "Buy the Orcette cosplay at the comic store, then give it to June.", "Daytime")),

        # --- Phone side quests ------------------------------------------------
        ("quest03", ("Side quest", "Mall", "CONSUM-R", "Buy a swimsuit ($100), then go to the Pool.", "Daytime")),
        ("quest05", ("Side quest", "Mall", "CONSUM-R", "Buy computer parts ($200) to fix your PC.", "Daytime")),
        ("quest06", ("Side quest", "Library", "", "Bring the webcam to the Library.", "Daytime")),
        ("quest07", ("Side quest", "Home", "Sister's bedroom", "Get a pair of your sister's panties for Somrak at the Gym.", "")),
        ("quest08", ("Side quest", "Diane's House", "", "Find the milk pump for Aunt Diane.", "Daytime")),
        ("quest09", ("Side quest", "School", "", "Deliver Aunt Diane's milk at school, then tell her.", "Morning")),
        ("quest10", ("Side quest", "Mall", "CONSUM-R", "Buy bug spray, then use it in Aunt Diane's garden.", "Daytime")),
        ("quest11", ("Side quest", "Library", "", "Place the hidden camera for the librarian.", "Daytime")),
        ("quest12", ("Side quest", "Mall", "CONSUM-R", "Buy a milk jug ($300) for Aunt Diane.", "Daytime")),
        ("quest13", ("Side quest", "Diane's House", "Shed", "Bring the package (cow costume) to Aunt Diane's shed.", "Daytime")),
        ("quest20", ("Side quest", "Diane's House", "Garden", "Find a shovel for Aunt Diane's garden.", "Daytime")),
        ("quest21", ("Side quest", "Diane's House", "Garden", "Deal with the wheelbarrow in Aunt Diane's garden.", "Daytime")),
        ]
    RM_STEPS = dict(RM_STEPS_ORDERED)
    # Step keys in story order (dicts are unordered in Python 2).
    RM_ORDER = [k for k, _v in RM_STEPS_ORDERED]

    # Machines to read, in display priority order.
    RM_MACHINES = ["M_mom", "M_mia", "M_helen", "M_terry", "M_roz", "M_dex", "M_aqua"]
    # Steps that can only be played with the Aqua storyline's private/ art.
    RM_AQUA_ONLY = set(["S_terry_trade", "S_terry_bored", "S_terry_retire"])
    # Legacy event queues.
    RM_QUEUES = ["sister", "mother", "aunt", "erik", "mrsj", "June", "Anna", "Roz", "roxxy", "crystal", "Grace", "player"]
    RM_STATE_KEYS = [k for k in RM_STEPS if k.startswith("S_")]
    RM_EVENT_KEYS = [k for k in RM_STEPS if not k.startswith("S_") and not k.startswith("quest")]
    RM_QUEST_KEYS = sorted(k for k in RM_STEPS if k.startswith("quest"))

    ## ---------------------------------------------------------------------
    ## Helpers
    ## ---------------------------------------------------------------------

    def rm_location_unlocked(name):
        loc = RM_LOC.get(name)
        if loc is None:
            return False
        if loc[1] is None:
            return True
        if name == "Lair":
            # Same condition the town map uses to draw the Lair.
            try:
                if not (AQUA_CONTENT and all(M_aqua.is_set(f) for f in
                        ("altar pass", "treasure pass", "squid pass", "maze pass"))):
                    return False
            except Exception:
                return False
        return bool(getattr(store, loc[1], False))

    def rm_location_open(name):
        """True when the town map lets you in right now."""
        loc = RM_LOC.get(name)
        if loc is None:
            return True
        rule = loc[2]
        try:
            if rule == "always":
                return True
            if rule == "day":
                return not gTimer.is_dark()
            if rule == "day_evening":
                return not gTimer.is_night()
            if rule == "not_night":
                return not gTimer.is_night()
            if rule == "day_weekday":
                return not gTimer.is_dark() and not gTimer.is_weekend()
            if rule == "church":
                if not gTimer.is_dark():
                    return True
                return gTimer.is_evening() and not M_mia.is_set('church night locked')
        except Exception:
            return True
        return True

    def rm_hours(name):
        loc = RM_LOC.get(name)
        if loc is None:
            return ""
        return RM_HOURS.get(loc[2], "")

    def _rm_find(keys, obj):
        for k in keys:
            if getattr(store, k, None) is obj:
                return k
        return None

    def _rm_task(key, kind):
        who, loc, room, hint, when = RM_STEPS[key]
        if loc is not None and loc not in RM_LOC:
            loc = None
        return {
            "key": key,
            "kind": kind,
            "who": who,
            "loc": loc,
            "room": room,
            "hint": hint,
            "when": when,
            "sleep": hint in (SLEEP,) or hint.startswith("Sleep"),
            "unlocked": loc is None or rm_location_unlocked(loc),
            "open": loc is None or rm_location_open(loc),
            }

    def roadmap_tasks():
        """All current tasks, most useful first. Never raises."""
        tasks = []
        seen = set()
        try:
            for mname in RM_MACHINES:
                m = getattr(store, mname, None)
                if m is None:
                    continue
                try:
                    state = m.get_state()
                except Exception:
                    continue
                key = _rm_find(RM_STATE_KEYS, state)
                if not AQUA_CONTENT and (mname == "M_aqua" or key in RM_AQUA_ONLY):
                    continue
                if key and key not in seen:
                    seen.add(key)
                    t = _rm_task(key, "story")
                    t["machine"] = mname
                    tasks.append(t)

            for qname in RM_QUEUES:
                q = getattr(store, qname, None)
                events = getattr(q, "_events", None)
                if not events:
                    continue
                for e in events:
                    # Only steps still waiting for the player.
                    if getattr(e, "_done", False) or getattr(e, "_completed", False):
                        continue
                    key = _rm_find(RM_EVENT_KEYS, e)
                    if key and key not in seen:
                        seen.add(key)
                        t = _rm_task(key, "event")
                        t["queue"] = qname
                        tasks.append(t)

            ql = getattr(store, "quest_list", None) or []
            done = getattr(store, "completed_quests", None) or []
            for key in RM_QUEST_KEYS:
                qobj = getattr(store, key, None)
                if qobj is not None and qobj in ql and qobj not in done and key not in seen:
                    seen.add(key)
                    tasks.append(_rm_task(key, "quest"))
        except Exception:
            pass

        # Reachable-now first, then story before events before side quests,
        # sleep reminders last.
        kind_order = {"story": 0, "event": 1, "quest": 2}
        tasks.sort(key=lambda t: (t["sleep"], not (t["unlocked"] and t["open"]), kind_order[t["kind"]]))
        return tasks

    def roadmap_by_location(tasks):
        result = {}
        for t in tasks:
            if t["loc"] is not None:
                result.setdefault(t["loc"], []).append(t)
        return result

    def roadmap_next(tasks):
        """The single best thing to do now."""
        for t in tasks:
            if t["unlocked"] and t["open"] and not t["sleep"]:
                return t
        return tasks[0] if tasks else None

    def roadmap_groups(tasks):
        """[(location or None, [tasks])] in map order, general tasks last."""
        by_loc = roadmap_by_location(tasks)
        groups = sorted(by_loc.items(), key=lambda kv: (
            not (rm_location_unlocked(kv[0]) and rm_location_open(kv[0])),
            RM_LOC_ORDER.get(kv[0], 99)))
        general = [t for t in tasks if t["loc"] is None]
        if general:
            groups.append((None, general))
        return groups

    RM_PEOPLE = [
        ("mom", "Mom"), ("sis", "Sister"), ("mia", "Mia"), ("helen", "Helen"),
        ("harold", "Harold"), ("erik", "Erik"), ("mrsj", "Mrs. Johnson"),
        ("june", "June"), ("anna", "Anna"), ("roz", "Roz"), ("crystal", "Crystal"),
        ("grace", "Grace"), ("angelica", "Angelica"), ("yumi", "Yumi"),
        ("earl", "Earl"), ("dexter", "Dexter"), ("terry", "Terry"),
        ]

    def roadmap_people():
        """[(name, where)] for characters whose location is known right now."""
        result = []
        for key, label in RM_PEOPLE:
            try:
                where = where_is(key)
            except Exception:
                continue
            if where:
                result.append((label, where))
        return result

    ## ---------------------------------------------------------------------
    ## Romance check: which repeatable intimate scenes are unlocked.
    ## Each condition is copied from the menu choice that offers the scene,
    ## so this only reports what the game itself already allows.
    ## (who, location, unlocked condition, available-now condition, how)
    ## ---------------------------------------------------------------------
    RM_ROMANCE = [
        ("Mom", "Home", "M_mom.is_set('sex available')", "True",
         "Talk to Mom at home (shower, her room, your room, car)."),
        ("Mom (laundry)", "Home", "M_mom.is_set('basement sex')", "True",
         "Talk to Mom in the basement and pick 'Laundry'."),
        ("Mrs. Johnson", "Erik's House", "mrsj.over(mrsj_sex_ed)", "gTimer.is_dark()",
         "Talk to her in the evening/night and pick 'Sex education'."),
        ("Mrs. Johnson (yoga)", "Erik's House", "erik.over(erik_gf)", "gTimer.is_dark()",
         "Talk to her in the evening/night and pick 'Private Yoga'."),
        ("June", "Home", "June.over(june_cosplay)", "gTimer.is_evening()",
         "June visits your bedroom in the evening."),
        ("Roz", "Clinic", "M_roz.get_state() == S_roz_end", "not M_roz.is_set('fun time') and not gTimer.is_night()",
         "Talk to Roz at the Clinic and pick 'Go on break' (once a day)."),
        ("Mia", "Mia's House", "M_mia.get_state() in (S_mia_study_sex, S_mia_end)", "gTimer.is_dark()",
         "Study with Mia in her bedroom in the evening."),
        ("Helen", "Mia's House", "M_helen.get_state() in (S_helen_master_servant_fun, S_helen_end)", "gTimer.is_afternoon()",
         "Visit Helen in her bedroom."),
        ("Aunt Diane", "Diane's House", "aunt.over(aunt_breeding_help)", "not gTimer.is_night()",
         "Visit Aunt Diane."),
        ]

    def _rm_eval(expr):
        try:
            return bool(eval(expr, store.__dict__))
        except Exception:
            return False

    def roadmap_romance():
        """[(who, location, unlocked, available now, how)]"""
        result = []
        for who, loc, unlocked, now, how in RM_ROMANCE:
            u = _rm_eval(unlocked)
            n = u and _rm_eval(now) and rm_location_unlocked(loc) and rm_location_open(loc)
            result.append((who, loc, u, n, how))
        return result

    def roadmap_time_text():
        try:
            tod = ["", "Morning", "Afternoon", "Evening", "Night"][gTimer._tod]
            return "{} {}, day {}".format(gTimer.dayOfWeek(True), tod, gTimer.gameDay())
        except Exception:
            return ""

    def roadmap_task_line(t, show_loc=False):
        parts = []
        if show_loc and t["loc"]:
            parts.append(u"{b}" + t["loc"] + u"{/b}")
        if t["room"]:
            parts.append(t["room"])
        place = u" > ".join(parts)
        line = u"{color=#ffd75e}" + t["who"] + u":{/color} "
        if place:
            line += u"[" + place + u"] "
        line += t["hint"]
        if t["when"]:
            line += u" {color=#9fc3ff}(" + t["when"] + u"){/color}"
        # Square brackets would be read as variable interpolation.
        return line.replace("[", "[[")

    ## ---------------------------------------------------------------------
    ## Auto-finish: clicking a task in the list completes it the same way the
    ## game's own scene would (fires the state machine trigger, finishes the
    ## event or marks the side quest done). The scene itself is skipped.
    ## ---------------------------------------------------------------------

    def _rm_give(item_name):
        item = getattr(store, item_name, None)
        if item is not None:
            inventory.get_item(item)

    def _rm_extra_stolen_goods():
        _rm_give("stolen_goods")

    def _rm_extra_larry_stash():
        if AQUA_CONTENT:
            _rm_give("treasure_key")

    def _rm_take(item_name):
        item = getattr(store, item_name, None)
        if item is not None and item in inventory.items:
            inventory.items.remove(item)

    def _rm_queue_event(queue_name, event_name):
        q = getattr(store, queue_name, None)
        e = getattr(store, event_name, None)
        if q is not None and e is not None and not q.known(e):
            q.add_event(e)

    def _rm_advance(machine_name, state_key):
        """Moves another machine on when the skipped scene would have too."""
        m = getattr(store, machine_name, None)
        state = getattr(store, state_key, None)
        if m is None or state is None or m.get_state() is not state:
            return
        pairs = sorted(state._table.items(), key=lambda kv: kv[0]._name)
        pairs = [kv for kv in pairs if kv[1] is not state] or pairs
        if pairs:
            result = state.trigger(pairs[0][0], m)
            if result is not None:
                m._state = result

    def _rm_extra_sis_panty01():
        inventory.money = max(0, inventory.money - 100)
        _rm_give("panties")
        if quest07 not in completed_quests:
            completed_quests.append(quest07)
        store.sis_panties_bought = True

    def _rm_extra_sis_cuddle02():
        _rm_queue_event("sister", "sis_hallway01")
        store.sis_shower_intro_first = False

    def _rm_extra_sis_final2():
        _rm_take("handcuffs")
        _rm_take("cheerleader_outfit")
        _rm_queue_event("sister", "sis_shower_cuddle05")

    def _rm_extra_roz_trick():
        roz_storage.finish()
        _rm_give("hospital_access_card")

    def _rm_extra_poker_night():
        store.mrsj_afterpoker_fun = False

    def _rm_extra_aqua_start():
        _rm_advance("M_terry", "S_terry_secret")

    def _rm_extra_terry_secret():
        _rm_advance("M_aqua", "S_aqua_start")

    def _rm_extra_lure_trade(partner, partner_state):
        _rm_take("golden_compass")
        _rm_give("special_lure")
        _rm_advance(partner, partner_state)

    def _rm_extra_valor(partner, partner_state):
        _rm_give("tigger")
        _rm_advance(partner, partner_state)

    def _rm_extra_aqua_lair():
        store.loc_lair_unlocked = True

    # Side effects the skipped scene would normally give (items etc.).
    RM_FINISH_EXTRAS = {
        "S_mia_stolen_goods": _rm_extra_stolen_goods,
        "erik_father_treasure": _rm_extra_larry_stash,
        "sis_panty01": _rm_extra_sis_panty01,
        "sis_shower_cuddle02": _rm_extra_sis_cuddle02,
        "sis_shower_cuddle03": lambda: _rm_queue_event("sister", "sis_couch03"),
        "sis_shower_cuddle04": lambda: _rm_queue_event("sister", "sis_final"),
        "sis_final2": _rm_extra_sis_final2,
        "sis_webcam04": lambda: _rm_take("badmonster"),
        "roz_trick": _rm_extra_roz_trick,
        "mrsj_poker_night": _rm_extra_poker_night,
        "S_terry_secret": _rm_extra_terry_secret,
        "S_aqua_start": _rm_extra_aqua_start,
        "S_aqua_boatsmith_search": lambda: _rm_give("obituary_records"),
        "S_aqua_altar_search": lambda: _rm_give("treasure_map"),
        "S_aqua_treasure_unlock": lambda: _rm_give("golden_compass"),
        "S_aqua_trade": lambda: _rm_extra_lure_trade("M_terry", "S_terry_trade"),
        "S_terry_trade": lambda: _rm_extra_lure_trade("M_aqua", "S_aqua_trade"),
        "S_aqua_fishing": lambda: _rm_take("special_lure"),
        "S_aqua_lair": _rm_extra_aqua_lair,
        "S_aqua_found": lambda: _rm_give("special_lure"),
        "S_aqua_valor_test": lambda: _rm_extra_valor("M_terry", "S_terry_retire"),
        "S_terry_retire": lambda: _rm_extra_valor("M_aqua", "S_aqua_valor_test"),
        }

    def _rm_triggers(task):
        """Outgoing (trigger, next state) pairs of a story task's state."""
        m = getattr(store, task.get("machine") or "", None)
        if m is None:
            return []
        try:
            state = m.get_state()
            table = state._table
        except Exception:
            return []
        pairs = sorted(table.items(), key=lambda kv: kv[0]._name)
        # "Wait a day" transitions loop back to the same state; skip them
        # when the step has a real way forward.
        forward = [kv for kv in pairs if kv[1] is not state]
        return forward or pairs

    def _rm_state_hint(state):
        key = _rm_find(RM_STATE_KEYS, state)
        if key:
            return RM_STEPS[key][3]
        return getattr(state, "_desc", None) or getattr(state, "_name", "?")

    def roadmap_finish_options(task):
        """[(button label, option index)] for the confirm row."""
        if task["kind"] == "story":
            pairs = _rm_triggers(task)
            if len(pairs) == 1:
                return [(u"Finish", 0)]
            # Branching step: let the player pick which way it goes.
            return [(u"Finish > " + _rm_state_hint(nxt)[:48], i) for i, (_t, nxt) in enumerate(pairs)]
        return [(u"Finish", 0)]

    def roadmap_finish(task, option=0):
        """Completes a roadmap task. Returns True on success."""
        key = task["key"]
        try:
            if task["kind"] == "story":
                pairs = _rm_triggers(task)
                if not pairs:
                    renpy.notify("This step can't be finished automatically.")
                    return False
                trig, _nxt = pairs[min(option, len(pairs) - 1)]
                m = getattr(store, task["machine"])
                # Only this machine moves (the game's global trigger would also
                # advance other storylines waiting on the same trigger).
                result = m.get_state().trigger(trig, m)
                if result is not None:
                    m._state = result
            elif task["kind"] == "event":
                getattr(store, key).finish()
            elif task["kind"] == "quest":
                quest_complete(getattr(store, key))
            extra = RM_FINISH_EXTRAS.get(key)
            if extra is not None:
                extra()
        except Exception as e:
            renpy.notify("Couldn't finish task: {}".format(e))
            return False
        renpy.notify(u"Task finished: " + task["hint"])
        renpy.restart_interaction()
        return True

    ## ---------------------------------------------------------------------
    ## Storyline: every step of the storyline a task belongs to (same person
    ## and same kind), in story order, marked done / current / upcoming.
    ## ---------------------------------------------------------------------

    def _rm_event_status(key):
        e = getattr(store, key, None)
        if e is None:
            return "todo"
        for qname in RM_QUEUES:
            q = getattr(store, qname, None)
            if q is not None and e in getattr(q, "_events", []):
                if getattr(e, "_done", False) or getattr(e, "_completed", False):
                    return "done"
                return "now"
        return "todo"

    def roadmap_storyline(task):
        """[(step key, status)] with status "done", "now" or "todo"."""
        who, kind = task["who"], task["kind"]
        prefix = {"story": "S_", "quest": "quest"}.get(kind)
        keys = []
        for k in RM_ORDER:
            if RM_STEPS[k][0] != who:
                continue
            if not AQUA_CONTENT and (k.startswith("S_aqua_") or k in RM_AQUA_ONLY):
                continue
            if prefix is not None:
                if not k.startswith(prefix):
                    continue
            elif k.startswith("S_") or k.startswith("quest"):
                continue
            keys.append(k)
        result = []
        try:
            if kind == "story":
                cur = keys.index(task["key"]) if task["key"] in keys else -1
                for i, k in enumerate(keys):
                    result.append((k, "done" if i < cur else ("now" if i == cur else "todo")))
            elif kind == "event":
                for k in keys:
                    result.append((k, _rm_event_status(k)))
            else:
                ql = getattr(store, "quest_list", None) or []
                done = getattr(store, "completed_quests", None) or []
                for k in keys:
                    q = getattr(store, k, None)
                    st = "done" if q in done else ("now" if q in ql else "todo")
                    result.append((k, st))
        except Exception:
            pass
        return result

    RM_NEXT_SHOWN = 5

    def roadmap_next_steps(task):
        """What to do next in this task's storyline: [(number, line, is current)].
        Starts with the current step, then the steps still to come."""
        result = []
        n = 0
        for k, st in roadmap_storyline(task):
            if st == "done":
                continue
            # Other "now" events of the same person are their own tasks.
            if st == "now" and k != task["key"]:
                continue
            n += 1
            line = roadmap_task_line(_rm_task(k, task["kind"]), True)
            result.append((n, line, k == task["key"]))
        result.sort(key=lambda r: not r[2])
        return [(i + 1, line, cur) for i, (_n, line, cur) in enumerate(result)]

    def roadmap_then(task, count=2):
        """The next few steps after the current one, for the town map."""
        return [line for _n, line, cur in roadmap_next_steps(task) if not cur][:count]

    def roadmap_quick_finish(task):
        """Finish from the town map; branching steps open the full list to pick."""
        if len(roadmap_finish_options(task)) > 1:
            renpy.show_screen("roadmap")
            renpy.restart_interaction()
            return
        roadmap_finish(task, 0)

    def rm_status_text(name):
        if not rm_location_unlocked(name):
            return u"{color=#ff8080}Not unlocked yet{/color}"
        if rm_location_open(name):
            return u"{color=#7CFC00}Open now{/color}"
        return u"{color=#ffb060}Closed now{/color} - " + rm_hours(name)

    def rm_marker_pos(name):
        loc = RM_LOC[name]
        x = loc[3] + loc[5] // 2
        y = max(loc[4] + 6, 2)
        return x, y


## -------------------------------------------------------------------------
## Styles
## -------------------------------------------------------------------------

style rm_text:
    color "#ffffff"
    size 18
    outlines [(1, "#000000", 0, 0)]

style rm_small is rm_text:
    size 15

style rm_title is rm_text:
    size 28
    bold True

style rm_frame:
    background "#101425ee"
    xpadding 16
    ypadding 12

style rm_button:
    background "#3a2a6a"
    hover_background "#6a4ac0"
    xpadding 14
    ypadding 8

style rm_button_text:
    color "#ffffff"
    hover_color "#ffffff"
    size 20
    xalign 0.5

transform rm_pulse:
    linear 0.6 zoom 1.12
    linear 0.6 zoom 1.0
    repeat


## -------------------------------------------------------------------------
## Global ROADMAP button (next to CHEATS, whenever the top bar is shown)
## -------------------------------------------------------------------------

screen roadmap_button:
    zorder 50
    if renpy.get_screen("ui") and not renpy.get_screen("roadmap") and not renpy.get_screen("cheat_menu"):
        textbutton "ROADMAP":
            style "rm_button"
            text_style "rm_button_text"
            xpos 1014 xanchor 1.0 ypos 130
            action Show("roadmap")

init python:
    config.overlay_screens.append("roadmap_button")


## -------------------------------------------------------------------------
## Town map layer: markers, NEXT banner, hover panel
## -------------------------------------------------------------------------

screen roadmap_map_layer:
    $ rm_tasks = roadmap_tasks()
    $ rm_by_loc = roadmap_by_location(rm_tasks)

    if persistent.roadmap_markers:
        for rm_name, rm_list in rm_by_loc.items():
            if rm_location_unlocked(rm_name):
                $ rm_x, rm_y = rm_marker_pos(rm_name)
                $ rm_open = rm_location_open(rm_name)
                frame:
                    at rm_pulse
                    xpos rm_x ypos rm_y xanchor 0.5 yanchor 0.5
                    xpadding 9 ypadding 2
                    background ("#ffcc33" if rm_open else "#8a8a8a")
                    text ("!" + str(len(rm_list))):
                        size 18 bold True color "#1a1a1a"

        # Romance available right now: heart badge on the building.
        $ rm_rom_now = [r for r in roadmap_romance() if r[3]]
        $ rm_rom_locs = []
        for rm_r in rm_rom_now:
            if rm_r[1] not in rm_rom_locs:
                $ rm_rom_locs.append(rm_r[1])
        for rm_name in rm_rom_locs:
            $ rm_x, rm_y = rm_marker_pos(rm_name)
            frame:
                at rm_pulse
                xpos (rm_x + 26) ypos (rm_y + 26) xanchor 0.5 yanchor 0.5
                xpadding 7 ypadding 1
                background "#ff5fa8"
                text u"\u2665" size 18 bold True color "#ffffff"

        $ rm_next = roadmap_next(rm_tasks)
        vbox:
            xpos 8 ypos 88
            spacing 4
            if rm_next is not None:
                hbox:
                    spacing 4
                    button:
                        xmaximum 560
                        background "#101425dd"
                        hover_background "#2a2f55ee"
                        xpadding 12 ypadding 6
                        action Show("roadmap")
                        vbox:
                            spacing 2
                            text ("{b}NEXT >{/b} " + roadmap_task_line(rm_next, True)) style "rm_small"
                            for rm_line in roadmap_then(rm_next):
                                text ("{color=#9fc3ff}then:{/color} " + rm_line) style "rm_small" size 13 color "#d8d8d8"
                    textbutton u"\u2713 Finish":
                        style "rm_button"
                        text_style "rm_button_text"
                        text_size 15
                        xpadding 10 ypadding 6
                        action Function(roadmap_quick_finish, rm_next)
            if rm_rom_now:
                button:
                    xmaximum 640
                    background "#101425dd"
                    hover_background "#2a2f55ee"
                    xpadding 12 ypadding 6
                    action Show("roadmap", rm_start_tab="romance")
                    text (u"{color=#ff8fc8}{b}ROMANCE NOW >{/b}{/color} " + u", ".join(r[0] + u" (" + r[1] + u")" for r in rm_rom_now)) style "rm_small"

    # Hovering a building (mouse) shows its tasks and opening hours.
    if location_count in RM_LOC:
        frame:
            style "rm_frame"
            xpos 8 yalign 0.99 xmaximum 620
            vbox:
                spacing 4
                text ("{b}" + location_count + "{/b}  " + rm_status_text(location_count)) style "rm_text"
                if location_count in rm_by_loc:
                    for rm_t in rm_by_loc[location_count][:3]:
                        text roadmap_task_line(rm_t) style "rm_small"
                        for rm_line in roadmap_then(rm_t):
                            text ("    {color=#9fc3ff}then:{/color} " + rm_line) style "rm_small" size 13 color "#d8d8d8"
                else:
                    text "Nothing to do here right now." style "rm_small" color "#bbbbbb"
                for rm_r in roadmap_romance():
                    if rm_r[1] == location_count and rm_r[2]:
                        text (("{color=#ff8fc8}Romance:{/color} " + rm_r[0] + " - ") + ("{color=#7CFC00}available now{/color}" if rm_r[3] else "{color=#ffb060}not now{/color}")) style "rm_small"


## -------------------------------------------------------------------------
## Full roadmap screen
## -------------------------------------------------------------------------

screen roadmap(rm_start_tab="tasks"):
    modal True
    zorder 200
    default rm_tab = rm_start_tab
    default rm_confirm = None
    default rm_story_open = set()

    add "#000b"

    frame:
        style "rm_frame"
        xalign 0.5 yalign 0.5
        xsize 940 ysize 700

        vbox:
            spacing 8

            hbox:
                xfill True
                text "Roadmap" style "rm_title"
                text roadmap_time_text() style "rm_text" xalign 1.0 yalign 0.5

            hbox:
                spacing 8
                textbutton "Where to go" style "rm_button" text_style "rm_button_text" action SetScreenVariable("rm_tab", "tasks") selected rm_tab == "tasks"
                textbutton "Where is everyone" style "rm_button" text_style "rm_button_text" action SetScreenVariable("rm_tab", "people") selected rm_tab == "people"
                textbutton "Romance" style "rm_button" text_style "rm_button_text" action SetScreenVariable("rm_tab", "romance") selected rm_tab == "romance"
                textbutton ("Map markers: ON" if persistent.roadmap_markers else "Map markers: OFF") style "rm_button" text_style "rm_button_text" action ToggleField(persistent, "roadmap_markers")

            viewport:
                ysize 540
                scrollbars "vertical"
                mousewheel True
                draggable True

                vbox:
                    spacing 6
                    xsize 880

                    if rm_tab == "tasks":
                        $ rm_tasks = roadmap_tasks()
                        if not rm_tasks:
                            text "No open tasks found. Explore the town and talk to people." style "rm_text"
                        for rm_loc, rm_list in roadmap_groups(rm_tasks):
                            null height 4
                            if rm_loc is None:
                                text "{b}Anywhere{/b}" style "rm_text" size 21 color "#ffd75e"
                            else:
                                text ("{b}" + rm_loc + "{/b}   " + rm_status_text(rm_loc)) style "rm_text" size 21
                            for rm_t in rm_list:
                                if rm_confirm == rm_t["key"]:
                                    frame:
                                        background "#2a2f55ee"
                                        xfill True
                                        xpadding 8 ypadding 6
                                        vbox:
                                            spacing 6
                                            text ("  - " + roadmap_task_line(rm_t)) style "rm_small"
                                            hbox:
                                                spacing 8
                                                box_wrap True
                                                for rm_lbl, rm_opt in roadmap_finish_options(rm_t):
                                                    textbutton rm_lbl.replace("[", "[[") style "rm_button" text_style "rm_button_text" text_size 16 action [Function(roadmap_finish, rm_t, rm_opt), SetScreenVariable("rm_confirm", None)]
                                                textbutton "Cancel" style "rm_button" text_style "rm_button_text" text_size 16 action SetScreenVariable("rm_confirm", None)
                                else:
                                    button:
                                        background None
                                        hover_background "#2a2f55cc"
                                        xfill True
                                        xpadding 4 ypadding 1
                                        action SetScreenVariable("rm_confirm", rm_t["key"])
                                        text ("  - " + roadmap_task_line(rm_t)) style "rm_small"
                                $ rm_steps = roadmap_next_steps(rm_t)
                                if len(rm_steps) > 1:
                                    $ rm_all = rm_t["key"] in rm_story_open
                                    vbox:
                                        xpos 40
                                        spacing 1
                                        text "What to do next:" style "rm_small" size 14 color "#9fc3ff"
                                        for rm_n, rm_line, rm_cur in (rm_steps if rm_all else rm_steps[:RM_NEXT_SHOWN]):
                                            if rm_cur:
                                                text ("{b}" + str(rm_n) + ". " + rm_line + "  {color=#7CFC00}< you are here{/color}{/b}") style "rm_small" size 14
                                            else:
                                                text (str(rm_n) + ". " + rm_line) style "rm_small" size 14 color "#d8d8d8"
                                        if len(rm_steps) > RM_NEXT_SHOWN:
                                            textbutton (u"Show less" if rm_all else (u"Show all " + str(len(rm_steps)) + u" steps")):
                                                background None
                                                xpadding 0 ypadding 0
                                                text_size 14
                                                text_color "#9fc3ff"
                                                text_hover_color "#ffffff"
                                                action ToggleSetMembership(rm_story_open, rm_t["key"])
                        null height 8
                        text "Tip: yellow ! markers on the town map show where tasks are. Grey means closed at this time of day." style "rm_small" color "#bbbbbb"
                        text "Click a task to auto-finish it (skips the scene)." style "rm_small" color "#bbbbbb"
                    elif rm_tab == "romance":
                        text "Repeatable scenes you've unlocked, and whether you can go now." style "rm_small" color "#bbbbbb"
                        for rm_who, rm_loc, rm_u, rm_n, rm_how in roadmap_romance():
                            vbox:
                                spacing 0
                                hbox:
                                    spacing 12
                                    text rm_who style "rm_text" min_width 230 color "#ff8fc8"
                                    if rm_n:
                                        text ("{color=#7CFC00}Available now{/color} at " + rm_loc) style "rm_text"
                                    elif rm_u:
                                        text ("{color=#ffb060}Unlocked, not right now{/color} (" + rm_loc + ")") style "rm_text"
                                    else:
                                        text "{color=#888888}Not unlocked yet{/color}" style "rm_text"
                                if rm_u:
                                    text ("    " + rm_how) style "rm_small" color "#cccccc"
                    else:
                        for rm_who, rm_where in roadmap_people():
                            hbox:
                                spacing 12
                                text rm_who style "rm_text" min_width 200 color "#ffd75e"
                                text rm_where.replace("[", "[[") style "rm_text"

            textbutton "Close" style "rm_button" text_style "rm_button_text" xalign 0.5 action Hide("roadmap")

init -2 python:
    # The Aqua / Lair storyline's art lives in "private/", which this release
    # doesn't ship. Its entry points (Hill treehole, Park coin and key, Beach
    # statue, Library old book) are hidden unless those files exist, because
    # opening them would crash on the missing images.
    AQUA_CONTENT = renpy.loadable("private/backgrounds/location_lair_blur.jpg")
