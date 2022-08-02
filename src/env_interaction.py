import arcade


def levers_check_col(scene, layer, player1, player2):
    lever = arcade.check_for_collision_with_list(player1, scene[layer])
    on_lever = 1
    if not lever:
        lever = arcade.check_for_collision_with_list(player2, scene[layer])
        on_lever = 2
        if not lever:
            on_lever = 0
    return on_lever, lever


# Checks to see if the collision between the select player and the layer is still persistent
def levers_check_remaining_col(sprite, player, on_lever_old):
    lever = arcade.check_for_collision(player, sprite)
    on_lever = 0
    if lever:
        on_lever = on_lever_old
    return on_lever


def lever_platform(platform, move_up, move_down, max, min, move_vel, dir='v'):
    # If lever is pressed, move platform
    if move_down:
        if dir == 'v':
            # Adding moving velocity in moving platform
            platform.center_y -= move_vel
            # Stop once you reach bottom
            if platform.center_y < min:
                platform.center_y = min
        elif dir == 'h':
            # Adding moving velocity in moving platform
            platform.center_x -= move_vel
            # Stop once you reach bottom
            if platform.center_x < min:
                platform.center_x = min
    if move_up:
        if dir == 'v':
            # Adding moving velocity in moving platform
            platform.center_y += move_vel
            # Stop once you reach top
            if platform.center_y > max:
                platform.center_y = max
        elif dir == 'h':
            # Adding moving velocity in moving platform
            platform.center_x += move_vel
            # Stop once you reach top
            if platform.center_x > max:
                platform.center_x = max

    return platform


def button_platform(scene, player1, player2, layer, platform, end, start, move_vel, dir):
    player_coll = arcade.check_for_collision_with_list(player1, scene[layer]) or \
                    arcade.check_for_collision_with_list(player2, scene[layer])
    if dir == 'v':
        if end > start:
            if player_coll:
                # Adding moving velocity in moving platform
                platform.center_y += move_vel
                # Stop once you reach top
                if platform.center_y > end:
                    platform.center_y = end
            else:
                # Adding moving velocity in moving platform
                platform.center_y -= move_vel
                # Stop once you reach top
                if platform.center_y < start:
                    platform.center_y = start
        else:
            if player_coll:
                # Adding moving velocity in moving platform
                platform.center_y -= move_vel
                # Stop once you reach top
                if platform.center_y < end:
                    platform.center_y = end
            else:
                # Adding moving velocity in moving platform
                platform.center_y += move_vel
                # Stop once you reach top
                if platform.center_y > start:
                    platform.center_y = start

    elif dir == 'h':
        if end > start:
            if player_coll:
                # Adding moving velocity in moving platform
                platform.center_x += move_vel
                # Stop once you reach top
                if platform.center_x > end:
                    platform.center_x = end
            else:
                # Adding moving velocity in moving platform
                platform.center_x -= move_vel
                # Stop once you reach top
                if platform.center_x < start:
                    platform.center_x = start
        else:
            if player_coll:
                # Adding moving velocity in moving platform
                platform.center_x -= move_vel
                # Stop once you reach top
                if platform.center_x < end:
                    platform.center_x = end
            else:
                # Adding moving velocity in moving platform
                platform.center_x += move_vel
                # Stop once you reach top
                if platform.center_x > start:
                    platform.center_x = start

    return platform
