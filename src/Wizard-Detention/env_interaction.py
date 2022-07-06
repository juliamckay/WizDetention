import arcade

def levers_check_col(scene, layer, player1, player2, move_up, move_down, on_lever):
    if arcade.check_for_collision_with_list(player1, scene[layer]) or \
            arcade.check_for_collision_with_list(player2, scene[layer]):
        if not on_lever:
            move_up = not move_up
            move_down = not move_down
        on_lever = True
    else:
        on_lever = False
    return on_lever, move_up, move_down

def lever_platform(platform, move_up, move_down, max_y, min_y, move_vel):
    # If lever is pressed, move platform
    if move_down:
        # Adding moving velocity in moving platform
        platform.center_y -= move_vel
        # Stop once you reach bottom
        if platform.center_y < min_y:
            platform.center_y = min_y
    if move_up:
        # Adding moving velocity in moving platform
        platform.center_y += move_vel
        # Stop once you reach top
        if platform.center_y > max_y:
            platform.center_y = max_y

    return platform

def button_platform(scene, player1, player2, layer, platform, max_y, min_y, move_vel):
    if arcade.check_for_collision_with_list(player1, scene[layer]) or \
            arcade.check_for_collision_with_list(player2, scene[layer]):
        # Adding moving velocity in moving platform
        platform.center_y += move_vel
        # Stop once you reach top
        if platform.center_y > max_y:
            platform.center_y = max_y
    else:
        # Adding moving velocity in moving platform
        platform.center_y -= move_vel
        # Stop once you reach top
        if platform.center_y < min_y:
            platform.center_y = min_y
    return platform
