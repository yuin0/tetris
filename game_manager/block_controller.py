#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime  # To pick up date
import pprint  # To customize output
import copy  # To copy objects
import numpy as np

from board_manager import Shape


class Coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class BlockStatus(object):
    def __init__(self, shapeClass: Shape, direction, coodinate: Coordinate):
        self.shapeClass = shapeClass
        self.direction = direction
        self.coodinate = coodinate

class BlockController(object):  # object is not necessary (to use python2)
    boardBackboard = 0
    boardDataWidth = 0
    boardDataHeight = 0

    shapeNoneIdx = 0
    currentShapeClass = 0
    nextShapeClass = 0
    holdShapeClass = 0

    def GetNextMove(self, nextMove, GameStatus):
        """
        # GetNextMove
           main function of BlockController
        # parameter
           nextMove : nextMove structure which is empty.
           GameStatus : block/field/judge/debug information.
            in detail see the internal GameStatus data. @game_manager
        # return
           nextMove : nextMove structure which includes next shape position.
        """

        t1 = datetime.now()
        print("=================================================>")
        pprint.pprint(GameStatus, width=61, compact=True)

        # get data from GameStatus
        currentShapeRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.currentShapeClass = GameStatus["block_info"]["currentShape"]["class"]
        
        nextShapeRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.nextShapeClass = GameStatus["block_info"]["nextShape"]["class"]

        holdShapeRange = GameStatus["block_info"]["holdShape"]["direction_range"]
        self.holdShapeClass = GameStatus["block_info"]["holdShape"]["class"]      

        self.boardBackboard = GameStatus["field_info"]["backboard"]
        self.boardDataWidth = GameStatus["field_info"]["width"]
        self.boardDataHeight = GameStatus["field_info"]["height"]

        self.shapeNoneIdx = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]

        # search best nextMove -->
        ## Initialize
        strategy = None  
        LatestEvalValue = -100000

        ## search with current block
        for blockDirection in currentShapeRange:
            startPoint, endPoint = self.getSearchXRange(self.currentShapeClass, blockDirection)
            for blockPosition in range(startPoint, endPoint):
                ## get board data, as if dropdown block
                blockCoodinate = Coordinate(blockPosition, 0)
                blockStatus = BlockStatus(self.currentShapeClass, blockDirection, blockCoodinate)
                temporaryBoard, fullLines = self.getTemporaryBoardAndFullLines(self.boardBackboard, blockStatus)

                ## Search with next block
                for nextBlockDirection in nextShapeRange:
                    nextStartPoint, nextEndPoint = self.getSearchXRange(self.nextShapeClass, nextBlockDirection)
                    for nextBlockPosition in range(nextStartPoint, nextEndPoint):
                        ## get board Data as if dropdown next block
                        nextBlockCoodinate = Coordinate(nextBlockPosition, 0)
                        nextBlockStatus = BlockStatus(self.nextShapeClass, nextBlockDirection, nextBlockCoodinate)
                        nextTemporaryBoard, nextFullLines = self.getTemporaryBoardAndFullLines(temporaryBoard, nextBlockStatus)

                        ## evaluate board
                        EvalValue = self.calcEvaluationValue(nextTemporaryBoard, fullLines, nextFullLines)
                        ## update best move
                        if EvalValue > LatestEvalValue:
                            useHold = 'n'
                            strategy = (blockDirection, blockPosition, 1, 1, useHold)
                            LatestEvalValue = EvalValue
                
                if self.holdShapeClass != None:
                    for holdBlockDirection in holdShapeRange:
                        holdStartPoint, holdEndPoint = self.getSearchXRange(self.holdShapeClass, holdBlockDirection)
                        for holdBlockPosition in range(holdStartPoint, holdEndPoint):
                            ## get board Data as if dropdown hold block
                            holdBlockCoodinate = Coordinate(holdBlockPosition, 0)
                            holdBlockStatus = BlockStatus(self.holdShapeClass, holdBlockDirection, holdBlockCoodinate)
                            holdTemporaryBoard, holdFullLines = self.getTemporaryBoardAndFullLines(temporaryBoard, holdBlockStatus)

                            ## evaluate board
                            EvalValue = self.calcEvaluationValue(holdTemporaryBoard, fullLines, holdFullLines)
                            ## update best move
                            if EvalValue > LatestEvalValue:
                                useHold = 'n'
                                strategy = (blockDirection, blockPosition, 1, 1, useHold)
                                LatestEvalValue = EvalValue

        if self.holdShapeClass != None:
            for blockDirection in holdShapeRange:
                startPoint, endPoint = self.getSearchXRange(self.holdShapeClass, blockDirection)
                for blockPosition in range(startPoint, endPoint):
                    ## get board data, as if dropdown block
                    blockCoodinate = Coordinate(blockPosition, 0)
                    blockStatus = BlockStatus(self.holdShapeClass, blockDirection, blockCoodinate)
                    temporaryBoard, fullLines = self.getTemporaryBoardAndFullLines(self.boardBackboard, blockStatus)

                    ## Search with next block
                    for nextBlockDirection in nextShapeRange:
                        nextStartPoint, nextEndPoint = self.getSearchXRange(self.nextShapeClass, nextBlockDirection)
                        for nextBlockPosition in range(nextStartPoint, nextEndPoint):
                            ## get board Data as if dropdown next block
                            nextBlockCoodinate = Coordinate(nextBlockPosition, 0)
                            nextBlockStatus = BlockStatus(self.nextShapeClass, nextBlockDirection, nextBlockCoodinate)
                            nextTemporaryBoard, nextFullLines = self.getTemporaryBoardAndFullLines(temporaryBoard, nextBlockStatus)

                            ## evaluate board
                            EvalValue = self.calcEvaluationValue(nextTemporaryBoard, fullLines, nextFullLines)
                            ## update best move
                            if EvalValue > LatestEvalValue:
                                useHold = 'y'
                                strategy = (blockDirection, blockPosition, 1, 1, useHold)
                                LatestEvalValue = EvalValue
                    for currentBlockDirection in currentShapeRange:
                        currentStartPoint, currentEndPoint = self.getSearchXRange(self.currentShapeClass, currentBlockDirection)
                        for currentBlockPosition in range(currentStartPoint, currentEndPoint):
                            ## get board Data as if dropdown current block
                            currentBlockCoodinate = Coordinate(currentBlockPosition, 0)
                            currentBlockStatus = BlockStatus(self.currentShapeClass, currentBlockDirection, currentBlockCoodinate)
                            currentTemporaryBoard, currentFullLines = self.getTemporaryBoardAndFullLines(temporaryBoard, currentBlockStatus)

                            ## evaluate board
                            EvalValue = self.calcEvaluationValue(currentTemporaryBoard, fullLines, currentFullLines)
                            ## update best move
                            if EvalValue > LatestEvalValue:
                                useHold = 'y'
                                strategy = (blockDirection, blockPosition, 1, 1, useHold)
                                LatestEvalValue = EvalValue
        else:
            for nextBlockDirection in nextShapeRange:
                nextStartPoint, nextEndPoint = self.getSearchXRange(self.nextShapeClass, nextBlockDirection)
                for nextBlockPosition in range(nextStartPoint, nextEndPoint):
                    ## get board Data as if dropdown next block
                    nextBlockCoodinate = Coordinate(nextBlockPosition, 0)
                    nextBlockStatus = BlockStatus(self.nextShapeClass, nextBlockDirection, nextBlockCoodinate)
                    nextTemporaryBoard, nextFullLines = self.getTemporaryBoardAndFullLines(temporaryBoard, nextBlockStatus)

                    for currentBlockDirection in currentShapeRange:
                        currentStartPoint, currentEndPoint = self.getSearchXRange(self.currentShapeClass, currentBlockDirection)
                        for currentBlockPosition in range(currentStartPoint, currentEndPoint):
                            ## get board Data as if dropdown current block
                            currentBlockCoodinate = Coordinate(currentBlockPosition, 0)
                            currentBlockStatus = BlockStatus(self.currentShapeClass, currentBlockDirection, currentBlockCoodinate)
                            currentTemporaryBoard, currentFullLines = self.getTemporaryBoardAndFullLines(temporaryBoard, currentBlockStatus)

                            ## evaluate board
                            EvalValue = self.calcEvaluationValue(currentTemporaryBoard, fullLines, currentFullLines)
                            ## update best move
                            if EvalValue > LatestEvalValue:
                                useHold = 'y'
                                strategy = (blockDirection, blockPosition, 1, 1, useHold)
                                LatestEvalValue = EvalValue                        


        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        nextMove["strategy"]["use_hold_function"] = strategy[4]
        # search best nextMove <--

        print("===", datetime.now() - t1)
        print(nextMove)
        print("Evaluation: ", LatestEvalValue)

        return nextMove

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        # get shape x offsets[minX,maxX] as relative value.
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction)
        xMin = -1 * minX
        xMax = self.boardDataWidth - maxX
        return xMin, xMax

    def getShapeCoordArray(self, blockStatus: BlockStatus):
        #
        # get coordinate array by given shape.
        #
        # get array from shape direction, x, y.
        coordArray = blockStatus.shapeClass.getCoords(
            blockStatus.direction, 
            blockStatus.coodinate.x, 
            blockStatus.coodinate.y
        )
        return coordArray

    def getTemporaryBoardAndFullLines(self, board_backboard, blockStatus: BlockStatus):
        """
        get board after the block dropped down preliminary
        """
        board = copy.deepcopy(board_backboard)
        boardPutBlock = self.dropDown(board, blockStatus)
        nextBoard, fullLines = self.getBoardWithoutFL(boardPutBlock)

        return nextBoard, fullLines

    def dropDown(self, board, blockStatus: BlockStatus):
        """
        internal function of getBoard.
        -- drop down the shape on the board.
        """
        coordArray = self.getShapeCoordArray(blockStatus)

        dy = self.boardDataHeight - 1
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.boardDataHeight \
                    and (_yy + _y < 0
                         or board[(_y + _yy) * self.boardDataWidth + _x]
                         == self.shapeNoneIdx):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, blockStatus, dy)
        return _board

    def dropDownWithDy(self, board, blockStatus: BlockStatus, dy):
        """
        internal function of dropDown
        """
        _board = board
        coordArray = self.getShapeCoordArray(blockStatus)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.boardDataWidth + _x] = blockStatus.shapeClass.shape
        return _board

    def getBoardWithoutFL(self, board):
        """
        inline function of getTemporaryBoard
        """
        width = self.boardDataWidth
        height = self.boardDataHeight
        nextBoard = [0] * width * height

        newY = height - 1
        fullLines = 0
        for y in range(height - 1, -1, -1):
            blockCount = sum([1 if board[x + y * width] > 0 else 0 for x in range(width)])
            if blockCount < width:
                for x in range(width):
                    nextBoard[x + newY * width] = board[x + y * width]
                newY -= 1
            else:
                fullLines += 1
        return nextBoard, fullLines

    def calcWellPenalty(self, blockMaxHeights):
        wellDepth = self.getWellDepth(blockMaxHeights)
        wellNum = 0
        wellPenalty = 0
        for x in range(self.boardDataWidth):
            if wellDepth[x] > 2:
                wellNum += 1
                wellPenalty += wellDepth[x]
        if wellNum < 2:
            wellPenalty = 0
        return wellPenalty

    def getWellDepth(self, blockMaxHeights):
        """
        inline function of calcWellDepth
        """
        leftDepth = [self.boardDataHeight] * self.boardDataWidth
        rightDepth = [self.boardDataHeight] * self.boardDataWidth
        wellDepth = [0] * self.boardDataWidth
        for x in range(self.boardDataWidth):
            if(x > 0):
                leftDepth[x] = blockMaxHeights[x - 1] - blockMaxHeights[x]
            if(x < len(blockMaxHeights) - 1):
                rightDepth[x] = blockMaxHeights[x + 1] - blockMaxHeights[x]
            wellDepth[x] = min(leftDepth[x], rightDepth[x])

        return wellDepth

    def getBoardFeatures(self, board):
        width = self.boardDataWidth
        height = self.boardDataHeight

        # Features
        holes = [0] * width
        isolatedBlocks = [0] * width
        maxHoleHeights = [0] * width
        maxBlockHeights = [0] * width

        # Temporary info for count hole number
        holeCandidates = [0] * width

        # Verify lines from bottom to top
        for y in range(height - 1, 0, -1): 
            for x in range(width):
                if board[y * width + x] == self.shapeNoneIdx:
                    holeCandidates[x] += 1  # just candidates in each column
                else:
                    maxBlockHeights[x] = height - y
                    if holeCandidates[x] > 0:
                        # update number of holes in target column
                        holes[x] += holeCandidates[x]
                        holeCandidates[x] = 0  # reset.
                        maxHoleHeights[x] = height - y - 1  # update the highest hole
                    if holes[x] > 0:
                        # update number of isolated blocks.
                        isolatedBlocks[x] += 1
        
        return holes, isolatedBlocks, maxHoleHeights, maxBlockHeights

    def calcEvaluationValue(self, board, offsetFL, fullLines):
        """
        Evaluate board
        """
        # Features of each column
        holes, isolatedBlocks, maxHoleHeights, maxBlockHeights = self.getBoardFeatures(board)
        
        # Penalties
        holeNumber = sum(holes)
        # onHolePenalty = sum( map(mul, isolatedBlocks, maxHoleHeights) )
        maxHolePenalty = max(maxHoleHeights)
        isolatedBlocksNumber = sum(isolatedBlocks)
        bumpiness = sum( np.abs( [a - b for a, b in zip(maxBlockHeights[1:], maxBlockHeights[:-2])] ) )
        maxHeight = max(maxBlockHeights)
        maxHeightDifference = maxHeight - sorted(maxBlockHeights)[1]
        wellPenalty = self.calcWellPenalty(maxBlockHeights)

        # calc Evaluation Value
        score = 0

        if fullLines == 4:
            score = score + fullLines * 100
        elif fullLines > 0:
            if maxHeight < 9:
                score = score - 9
            else:
                score = score + fullLines
        
        if offsetFL == 4:
            score = score + offsetFL * 100
        elif fullLines < 4 and offsetFL > 0:
            if maxHeight < 9:
                score = score - 9
            else:
                score = score + offsetFL
        
        if maxHeight > 12:
            score = score - maxHeight * 10  # maxHeight

        score -= holeNumber * 10
        # score -= onHolePenalty * 5
        score -= maxHolePenalty * 5
        score -= isolatedBlocksNumber * 5
        score -= bumpiness * 0.8
        score -= maxHeightDifference * 3.0
        score -= wellPenalty * 5.0

        return score

BLOCK_CONTROLLER = BlockController()
