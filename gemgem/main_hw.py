import random, time, pygame, sys, copy, cv2
from pygame.locals import *
import gemgem
import numpy as np

PAD = 44
# Run with `python main_hw.py`


def bot_move():
    brd = np.zeros((8, 8))
    img = cv2.imread('screenshot.jpg', cv2.IMREAD_UNCHANGED)
    
    #init board from taken screenshot
    for i in range(gemgem.BOARDWIDTH):
        for j in range(gemgem.BOARDHEIGHT):            
            img_cropped = img[PAD+(gemgem.GEMIMAGESIZE*i):PAD+(gemgem.GEMIMAGESIZE*(i+1)), PAD+(gemgem.GEMIMAGESIZE*j):PAD+(gemgem.GEMIMAGESIZE*(j+1))]
            img_cropped[0,:] = img_cropped[-1,:] = img_cropped[:,0] = img_cropped[:,-1] = gemgem.LIGHTBLUE[::-1]
            
            for n in range(1, gemgem.NUMGEMIMAGES+1):
                gem = cv2.imread('gem{}.png'.format(str(n)), cv2.IMREAD_UNCHANGED)                    
                trans_mask = gem[:,:,3] == 0
                gem[trans_mask] = [*gemgem.LIGHTBLUE[::-1], 255]

                new_gem = cv2.cvtColor(gem, cv2.COLOR_BGRA2BGR)[:,:,:3]
                difference = cv2.subtract(img_cropped, new_gem)
                b, g, r = cv2.split(difference)
                
                #find most similar .png image
                dif_pix = 30
                if (len(b[np.where(b>dif_pix)]) > 500 and len(b[np.where(b>dif_pix)]) < 900) and \
                (len(g[np.where(g>dif_pix)]) > 500 and len(g[np.where(g>dif_pix)]) < 900) and \
                (len(r[np.where(r>dif_pix)]) > 500 and len(r[np.where(r>dif_pix)]) < 900):
                    brd[j,i]=n-1
                    break
                    
    #trying 4 different combinations of possible winning states
    
    for i in range(gemgem.BOARDWIDTH-2):
        for j in range(gemgem.BOARDHEIGHT-1): 
            sel_area = brd[i:i+3, j:j+2].T
            unique, counts = np.unique(sel_area, return_counts=True)
            if 3 in counts or 4 in counts:
                val = unique[np.where(counts>2)][0]
                for v in range(2):
                    ind = np.where(sel_area[v]!=val)[0][0]
                    if sel_area[(v + 1) % 2, ind] == val and len(np.where(sel_area[v]==val)[0]) == 2:
                        x1 = int(i + ind)
                        y1 = int(j + v)
                        x2 = int(i + ind)
                        y2 = int(j + (v + 1) % 2)
                        return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}
    
    for i in range(gemgem.BOARDWIDTH-1):
        for j in range(gemgem.BOARDHEIGHT-2): 
            sel_area = brd[i:i+2, j:j+3].T
            unique, counts = np.unique(sel_area, return_counts=True)
            if 3 in counts or 4 in counts:
                val = unique[np.where(counts>2)][0]
                for v in range(2):
                    _, counts = np.unique(sel_area[:, v], return_counts=True)
                    ind = np.where(sel_area[:, v]!=val)[0][0]
                    if len(np.where(sel_area[:, v]==val)[0]) == 2 and sel_area[ind, (v + 1) % 2] == val:
                        x1 = int(i + v)
                        y1 = int(j + ind)
                        x2 = int(i + (v + 1) % 2)
                        y2 = int(j + ind)
                        return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}
                    
    for i in range(gemgem.BOARDWIDTH-3):
        for j in range(gemgem.BOARDHEIGHT): 
            sel_area = brd[i:i+4, j].T
            unique, counts = np.unique(sel_area, return_counts=True)
            if 3 in counts:
                val = unique[np.where(counts>2)][0]
                ind = np.where(sel_area!=val)[0][0]
                x1 = int(i + ind)
                y1 = int(j)
                x2 = int(i + ind + 1) if ind == 2 else int(i+ind-1)
                y2 = int(j)
                return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}
    
    for i in range(gemgem.BOARDWIDTH):
        for j in range(gemgem.BOARDHEIGHT-3): 
            sel_area = brd[i, j:j+4].T
            unique, counts = np.unique(sel_area, return_counts=True)
            if 3 in counts:
                val = unique[np.where(counts>2)][0]
                ind = np.where(sel_area!=val)[0][0]
                x1 = int(i)
                y1 = int(j+ind)
                x2 = int(i)
                y2 = int(j + ind + 1) if ind == 2 else int(j+ind-1)
                return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}
    return None, None








# copied from source code with a few rows inserted(making screenshots and calling bot)

def myRunGame():
    # Plays through a single game. When the game is over, this function returns.

    # initalize the board
    gameBoard = gemgem.getBlankBoard()
    score = 0
    gemgem.fillBoardAndAnimate(gameBoard, [], score) # Drop the initial gems.

    # initialize variables for the start of a new game
    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None
    
    field_updated = True
    game_started = True
    while True: # main game loop
        clickedSpace = None

        if field_updated and not game_started and not gameIsOver:
            pygame.image.save(gemgem.DISPLAYSURF,"screenshot.jpg")
            firstSelectedGem, clickedSpace = bot_move()
            field_updated = False

        for event in pygame.event.get(): # event handling loop
            if event.type == gemgem.QUIT or (event.type == gemgem.KEYUP and event.key == gemgem.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == gemgem.KEYUP and event.key == gemgem.K_BACKSPACE:
                return # start a new game

            elif event.type == gemgem.MOUSEBUTTONUP:
                if gameIsOver:
                    return # after games ends, click to start a new game

                if event.pos == (lastMouseDownX, lastMouseDownY):
                    # This event is a mouse click, not the end of a mouse drag.
                    clickedSpace = gemgem.checkForGemClick(event.pos)
                else:
                    # this is the end of a mouse drag
                    firstSelectedGem = gemgem.checkForGemClick((lastMouseDownX, lastMouseDownY))
                    clickedSpace = gemgem.checkForGemClick(event.pos)
                    if not firstSelectedGem or not clickedSpace:
                        # if not part of a valid drag, deselect both
                        firstSelectedGem = None
                        clickedSpace = None
            elif event.type == gemgem.MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem:
            # This was the first gem clicked on.
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            # Two gems have been clicked on and selected. Swap the gems.
            firstSwappingGem, secondSwappingGem = gemgem.getSwappingGems(gameBoard, firstSelectedGem, clickedSpace)
            if firstSwappingGem == None and secondSwappingGem == None:
                # If both are None, then the gems were not adjacent
                firstSelectedGem = None # deselect the first gem
                continue

            # Show the swap animation on the screen.
            boardCopy = gemgem.getBoardCopyMinusGems(gameBoard, (firstSwappingGem, secondSwappingGem))
            gemgem.animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)

            # Swap the gems in the board data structure.
            gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = secondSwappingGem['imageNum']
            gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = firstSwappingGem['imageNum']

            # See if this is a matching move.
            matchedGems = gemgem.findMatchingGems(gameBoard)
            if matchedGems == []:
                # Was not a matching move; swap the gems back
                gemgem.GAMESOUNDS['bad swap'].play()
                gemgem.animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
            else:
                # This was a matching move.
                scoreAdd = 0
                while matchedGems != []:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the playergets multiple matches, then multiple points text should appear.
                    points = []
                    for gemSet in matchedGems:
                        scoreAdd += (10 + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            gameBoard[gem[0]][gem[1]] = gemgem.EMPTY_SPACE
                        points.append({'points': scoreAdd,
                                       'x': gem[0] * gemgem.GEMIMAGESIZE + gemgem.XMARGIN,
                                       'y': gem[1] * gemgem.GEMIMAGESIZE + gemgem.YMARGIN})
                    random.choice(gemgem.GAMESOUNDS['match']).play()
                    score += scoreAdd

                    # Drop the new gems.
                    gemgem.fillBoardAndAnimate(gameBoard, points, score)

                    # Check if there are any new matches.
                    matchedGems = gemgem.findMatchingGems(gameBoard)
                field_updated = True
            firstSelectedGem = None

            if not gemgem.canMakeMove(gameBoard):
                gameIsOver = True
        
        # Draw the board.
        gemgem.DISPLAYSURF.fill(gemgem.BGCOLOR)
        gemgem.drawBoard(gameBoard)
        if firstSelectedGem != None:
            gemgem.highlightSpace(firstSelectedGem['x'], firstSelectedGem['y'])
        if gameIsOver:
            if clickContinueTextSurf == None:
                # Only render the text once. In future iterations, just
                # use the Surface object already in clickContinueTextSurf
                clickContinueTextSurf = gemgem.BASICFONT.render('Final Score: %s (Click to continue)' % (score), 1, gemgem.GAMEOVERCOLOR, gemgem.GAMEOVERBGCOLOR)
                clickContinueTextRect = clickContinueTextSurf.get_rect()
                clickContinueTextRect.center = int(gemgem.WINDOWWIDTH / 2), int(gemgem.WINDOWHEIGHT / 2)
            gemgem.DISPLAYSURF.blit(clickContinueTextSurf, clickContinueTextRect)
        elif score > 0 and time.time() - lastScoreDeduction > gemgem.DEDUCTSPEED:
            # score drops over time
            score -= 1
            lastScoreDeduction = time.time()
        gemgem.drawScore(score)
        pygame.display.update()
        gemgem.FPSCLOCK.tick(gemgem.FPS)
        
        if game_started:
            pygame.image.save(gemgem.DISPLAYSURF,"screenshot.jpg")
            game_started = False
            
            
gemgem.runGame = myRunGame
            
if __name__ == '__main__':
    gemgem.main()