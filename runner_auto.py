import pygame
import sys
import time

# import tictactoe as ttt
import tactictoe_precalculated as ttt

ttt.init()
MOVE_DELAY = 0.2
RESET_DELAY = 1

pygame.init()
size = width, height = 600, 400

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

screen = pygame.display.set_mode(size)

smallFont = pygame.font.Font("OpenSans-Regular.ttf", 12)
mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)

user = None
state = ttt.initial_state()
game_over = False

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(black)

    # Let user choose a player.
    if user is None:
        user = ttt.O
        
    else:

        # Draw game board
        tile_size = 80
        tile_origin = (width / 2 - (1.5 * tile_size),
                       height / 2 - (1.5 * tile_size))
        tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                pygame.draw.rect(screen, white, rect, 3)

                padding = 7 # Pixels to push numbers away from the borders

                # --- Display score number in bottom-left ---
                if state["board"][i][j] == ttt.EMPTY:
                    # Render the text
                    move_score_str = ttt.getStateScore(ttt.result(state, (i, j)))
                    left_num_surface = smallFont.render(move_score_str, True, white)
                    # Get the rectangle of the rendered text
                    left_num_rect = left_num_surface.get_rect()
                    # Position the text's rectangle in the bottom-left of the cell
                    left_num_rect.bottomleft = (rect.left + padding, rect.bottom - padding)
                    # Draw it on the screen
                    screen.blit(left_num_surface, left_num_rect)

                # --- Display lifetime number in bottom-right ---
                if state["board"][i][j] != ttt.EMPTY:
                    # Render the text
                    right_num_surface = smallFont.render(str(state["board"][i][j]), True, white)
                    # Get the rectangle of the rendered text
                    right_num_rect = right_num_surface.get_rect()
                    # Position the text's rectangle in the bottom-right of the cell
                    right_num_rect.bottomright = (rect.right - padding, rect.bottom - padding)
                    # Draw it on the screen
                    screen.blit(right_num_surface, right_num_rect)

                if state["board"][i][j] != ttt.EMPTY:
                    if state["board"][i][j] > 0:
                        move = moveFont.render("X", True, white)
                    else:
                        move = moveFont.render("O", True, white)
                    moveRect = move.get_rect()
                    moveRect.center = rect.center
                    screen.blit(move, moveRect)
                row.append(rect)
            tiles.append(row)

        game_over = ttt.terminal(state)
        player = ttt.player(state)

        # Show title
        if game_over:
            winner = ttt.winner(state)
            if winner == ttt.X:
                winner_str = "X"
            else:
                winner_str = "O"
            print(f"GAME OVER - Winner: {winner_str}")
            if winner is None:
                title = f"Game Over: Tie."
            else:
                title = f"Game Over: {winner_str} wins."

        elif user == player:
            title = f"Computer 1 thinking..."
        else:
            title = f"Computer 2 thinking..."
        title = largeFont.render(title, True, white)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 30)
        screen.blit(title, titleRect)


        # Update the display
        pygame.display.flip()
 
        if user != player and not game_over:
            time.sleep(MOVE_DELAY)
            move = ttt.getRandomMove(state)
            state = ttt.result(state, move)

        if user == player and not game_over:
            # AI vs AI
            time.sleep(MOVE_DELAY)
            move = ttt.getBestMove(state)
            state = ttt.result(state, move)

        if game_over:
            time.sleep(RESET_DELAY)
            user = None
            state = ttt.initial_state()
            ai_turn = False
            game_over = False
