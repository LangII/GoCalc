


import os, sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from kivy.app import App
import math
import numpy as np
import tensorflow as tf

from calculate.basictensorfuncs import (
    getCountOfValue, getPosOfValue, reshapeFlatten, reshapeInsertDim, reshapeAddDim,
    reshapeMergeDims, replaceValueAtIndex, sort2dByCol, applyScale
)

# from calculate.calcfuncs import (
#     getDistTwoPoints, getAngleTwoPoints, applyScale, applySkew, applyClamp
# )

####################################################################################################

np.set_printoptions(
    linewidth=220, # <- How many characters per line before new line.
    threshold=300, # <- How many lines allowed before summarized print.
    # threshold=sys.maxsize, # <- How many lines allowed before summarized print. (no summarization)
    edgeitems=10, # <- When summarized, how many edge values are printed.
    suppress=True, # <- Suppress scientific notation.
    precision=4, # <- How many decimal places on floats.
    # sign='+', # <- Display + for positive numbers.
)

####################################################################################################

EMPTY_VALUE = 0
BLACK_VALUE = +1
WHITE_VALUE = -1

MAIN_DTYPE = 'int32'

####################################################################################################

def getInfluenceData():

    print("")

    """ COLLECT INPUTS FROM app_data """

    app_data = App.get_running_app().data

    board = getBoardTensorFromBoardObj(app_data['board'])
    display_mode = app_data['influence']['display_mode'] # 'cur_infl' or 'infl_pred'
    pred_value = getPredValue(app_data)

    dist_decay_adj = app_data['influence']['adjustments']['distance_decay']
    dist_zero_adj = app_data['influence']['adjustments']['distance_zero']
    angle_decay_adj = app_data['influence']['adjustments']['angle_decay']
    opp_angle_growth_adj = app_data['influence']['adjustments']['opposite_angle_growth']
    clamp_adj = app_data['influence']['adjustments']['clamp']

    dist_decay_gt_weight = app_data['influence']['weights']['dist_decay_gt']['value']
    dist_decay_lin_weight = app_data['influence']['weights']['dist_decay_lin']['value']
    dist_zero_gt_weight = app_data['influence']['weights']['dist_zero_gt']['value']
    angle_decay_lt_weight = app_data['influence']['weights']['angle_decay_lt']['value']
    angle_decay_lin_weight = app_data['influence']['weights']['angle_decay_lin']['value']
    opp_angle_growth_angle_lt_weight = app_data['influence']['weights']['opp_angle_growth_angle_lt']['value']
    opp_angle_growth_dist_lt_weight = app_data['influence']['weights']['opp_angle_growth_dist_lt']['value']
    opp_angle_growth_lin_weight = app_data['influence']['weights']['opp_angle_growth_lin']['value']
    clamp_within_weight = app_data['influence']['weights']['clamp_within']['value']

    # print(board, "<- board\n")

    """ COLLECT REUSABLES """

    board_shape = board.shape.as_list()
    empty_count = getCountOfValue(board, EMPTY_VALUE)
    black_count = getCountOfValue(board, BLACK_VALUE)
    white_count = getCountOfValue(board, WHITE_VALUE)
    both_count = black_count + white_count
    empty_count_per_pred = empty_count - 1
    black_count_per_pred = getCountPerPred(BLACK_VALUE, black_count, pred_value)
    white_count_per_pred = getCountPerPred(WHITE_VALUE, white_count, pred_value)
    both_count_per_pred = black_count_per_pred + white_count_per_pred
    empty_count_all_pred = empty_count * empty_count_per_pred
    max_dist = math.hypot(*board_shape)
    # print(f"pred_value = {pred_value}")
    # print(f"board_shape = {board_shape}")
    # print(f"empty_count = {empty_count}")
    # print(f"black_count = {black_count}")
    # print(f"white_count = {white_count}")
    # print(f"both_count = {both_count}")
    # print(f"empty_count_per_pred = {empty_count_per_pred}")
    # print(f"black_count_per_pred = {black_count_per_pred}")
    # print(f"white_count_per_pred = {white_count_per_pred}")
    # print(f"both_count_per_pred = {both_count_per_pred}")
    # print(f"empty_count_all_pred = {empty_count_all_pred}")
    # print(f"max_dist = {max_dist}")

    """ START BUILDING TENSORS """

    empty_coords = getEmptyCoords(board)
    # print(empty_coords, "<- empty_coords\n")

    pred_moves = getPredMoves(board, board_shape, empty_count, empty_coords, pred_value)
    # # print(pred_moves, "<- pred_moves\n")

    # Logic must change to handle 'cur_infl' display_mode.
    if display_mode == 'cur_infl':
        pred_moves = reshapeInsertDim(board, 0)
        empty_count_per_pred = empty_count
        black_count_per_pred = black_count
        white_count_per_pred = white_count
        both_count_per_pred = both_count
        empty_count_all_pred = empty_count
        empty_count = 1

    pred_empty_coords = getPredValueCoords(pred_moves, EMPTY_VALUE, empty_count)
    pred_black_coords = getPredValueCoords(pred_moves, BLACK_VALUE, empty_count)
    pred_white_coords = getPredValueCoords(pred_moves, WHITE_VALUE, empty_count)
    # print(pred_empty_coords, "<- pred_empty_coords")
    # print(pred_black_coords, "<- pred_black_coords")
    # print(pred_white_coords, "<- pred_white_coords")

    pred_black_normals = getPredValueNormals(
        pred_empty_coords, pred_black_coords, empty_count_per_pred, black_count_per_pred
    )
    pred_white_normals = getPredValueNormals(
        pred_empty_coords, pred_white_coords, empty_count_per_pred, white_count_per_pred
    )
    # print(pred_black_normals, "<- pred_black_normals")
    # print(pred_white_normals, "<- pred_white_normals")

    pred_black_dists = getDistsFromNormals(pred_black_normals)
    pred_white_dists = getDistsFromNormals(pred_white_normals)
    # print(pred_black_dists, "<- pred_black_dists")
    # print(pred_white_dists, "<- pred_white_dists")

    pred_black_angles = getAnglesFromNormals(pred_black_normals)
    pred_white_angles = getAnglesFromNormals(pred_white_normals)
    # print(pred_black_angles, "<- pred_black_angles")
    # print(pred_white_angles, "<- pred_white_angles")

    pred_stones_dists_angles = getPredStonesDistsAngles(
        pred_black_dists, pred_black_angles, BLACK_VALUE,
        pred_white_dists, pred_white_angles, WHITE_VALUE
    )
    pred_stones = pred_stones_dists_angles[:, :, 0]
    pred_dists = pred_stones_dists_angles[:, :, 1]
    pred_angles = pred_stones_dists_angles[:, :, 2]
    # print(pred_stones_dists_angles, "<- pred_stones_dists_angles")

    """ GET RAW INFLUENCES """

    raw_infls = getRawInfls(pred_stones, pred_dists, max_dist)
    # print(raw_infls, "<- raw_infls")

    """ GET DISTANCE DECAY INFLUENCE ADJUSTMENT """

    dist_decay_infls_adjs = getDistDecayInflsAdjs(
        pred_dists, dist_decay_gt_weight, dist_decay_lin_weight
    )
    # print(dist_decay_infls_adjs, "<- dist_decay_infls_adjs")

    """ GET DISTANCE ZERO INFLUENCE ADJUSTMENT """

    dist_zero_infls_adjs = getDistZeroInflsAdjs(pred_dists, dist_zero_gt_weight)
    # print(dist_zero_infls_adjs, "<- dist_zero_infls_adjs")

    """ GET ANGLE DECAY INFLUENCE ADJUSTMENT """

    angle_difs = getAngleDifs(pred_angles, both_count_per_pred)
    # print(angle_difs, "<- angle_difs")

    raw_angle_infls = getRawAngleInfls(angle_difs, angle_decay_lt_weight, angle_decay_lin_weight)
    # print(raw_angle_infls, "<- raw_angle_infls")

    angle_mirror_mask = getAngleMirrorMask(both_count_per_pred, empty_count_all_pred)
    # print(angle_mirror_mask, "<- angle_mirror_mask")

    angle_stones_mask = getAngleStonesMask(pred_stones, both_count_per_pred, pred_value)
    # print(angle_stones_mask, "<- angle_stones_mask")

    masked_angle_infls = getMaskedAngleInfls(raw_angle_infls, angle_mirror_mask, angle_stones_mask)
    # print(masked_angle_infls, "<- masked_angle_infls")

    angle_decay_infls_adjs = getAngleDecayInflsAdjs(masked_angle_infls)
    print(angle_decay_infls_adjs, "<- angle_decay_infls_adjs")

    """ APPLY WEIGHT ADJUSTMENTS TO STONE INFLUENCES """

    pred_moves_stone_infls = raw_infls
    if dist_decay_adj:  pred_moves_stone_infls *= dist_decay_infls_adjs
    if dist_zero_adj:  pred_moves_stone_infls *= dist_zero_infls_adjs
    if angle_decay_adj:  pred_moves_stone_infls *= angle_decay_infls_adjs

    """ REDUCE STONE INFLUENCES TO GET MOVE INFLUENCES """

    pred_move_infls = reduceStoneInflsGetMoveInfls(pred_moves_stone_infls, pred_moves)

    """ APPLY WEIGHT ADJUSTMENTS TO MOVE INFLUENCES """

    #
    #
    #

    # print(pred_move_infls, "<- pred_move_infls")

    """ REDUCE AND/OR RETURN INFLUENCE DATA """

    # Logic must change to handle 'cur_infl' display_mode.
    if display_mode == 'cur_infl':
        return reshapeMergeDims(pred_move_infls, [0, 1]).numpy()

    # Reduce move influences to get prediction (influence_data) output.
    prediction = reduceMoveInflsGetPred(pred_move_infls, empty_coords, board_shape, board)
    # print(prediction, "<- prediction")

    return prediction.numpy()


####################################################################################################

def getPredValue(app_data):
    """ Extract stone value to be predicted from app_data. """
    return BLACK_VALUE if app_data['influence']['predicting_stone'] == 'black' else WHITE_VALUE



def getCountPerPred(stone_value, stone_count, pred_value):
    return stone_count if pred_value != stone_value else stone_count + 1



def getBoardTensorFromBoardObj(board_obj):
    """ Convert Board object to tensor. """
    board_tensor = []
    for row in board_obj.grid:
        row_ = []
        for pos in row:
            if not pos:  num = EMPTY_VALUE
            elif pos.color == 'black':  num = BLACK_VALUE
            elif pos.color == 'white':  num = WHITE_VALUE
            row_ += [ num ]
        board_tensor += [ row_ ]
    return tf.constant(board_tensor, dtype=MAIN_DTYPE)



def getEmptyCoords(board):
    """ A list of all coords that have no stone in board. """
    return tf.cast(tf.where(tf.equal(board, 0)), dtype=board.dtype)



def getPredMoves(board, board_shape, empty_count, empty_coords, pred_value):
    """ A list of all possible next moves (represented as a board with next move) that will have
    influence predicted. """
    def getSparsePredMoves(coord):
        return tf.sparse.to_dense(tf.SparseTensor([coord], [pred_value], board_shape))
    sparse_pred_moves = tf.map_fn(fn=lambda coord: getSparsePredMoves(coord), elems=empty_coords)
    tiled_board = tf.tile(tf.reshape(board, [1, *board_shape]), [empty_count, 1, 1])
    pred_moves = sparse_pred_moves + tiled_board

    # Handle collection of data for display_mode = 'cur_infl'.
    # pred_moves = tf.concat([pred_moves, reshapeInsertDim(board, 0)], axis=0)

    return pred_moves



def getPredValueCoords(pred_moves, value, empty_count):
    """ Similar to empty_coords.  Except what empty_coords does for the current board position,
    pred_value_coords does for every possible board position (pred_moves) in pred_moves for value. """
    pred_value_coords = tf.cast(tf.where(tf.equal(pred_moves, value)), dtype='int32')

    # print(pred_value_coords)

    return tf.reshape(pred_value_coords[:, 1:], [empty_count, -1, 2])



def getPredValueNormals(
    pred_empty_coords, pred_value_coords, empty_count_per_pred, value_count_per_pred
):
    """ Tensors representing the coord normals of each stone in each predicted next move. """
    pred_empty_coords_resh = reshapeInsertDim(pred_empty_coords, 2)
    empty_multiples =  tf.constant([1, 1, value_count_per_pred, 1])
    pred_empty_coords_tiled = tf.tile(pred_empty_coords_resh, empty_multiples)
    pred_value_coords_resh = reshapeInsertDim(pred_value_coords, 1)
    value_multiples = tf.constant([1, empty_count_per_pred, 1, 1])
    pred_value_coords_tiled = tf.tile(pred_value_coords_resh, value_multiples)
    return pred_value_coords_tiled - pred_empty_coords_tiled



def getDistsFromNormals(normals):
    """ Tensors representing the distance between each empty coord and each value coord for each
    predicted next move. """
    flat_pred_value_normals = tf.reshape(tf.cast(normals, dtype='float32'), [-1, 2])
    pred_value_dists = tf.norm(flat_pred_value_normals, ord='euclidean', axis=1)
    return tf.reshape(pred_value_dists, normals.shape[:-1])



def getAnglesFromNormals(normals):
    """ Tensors representing the angle of each value coord from each empty coord for each predicted
    next move. """
    y_normals = tf.cast(normals[:, :, :, 0] * -1, dtype='float32')
    x_normals = tf.cast(normals[:, :, :, 1], dtype='float32')
    pred_value_angles = tf.atan2(y_normals, x_normals) * (180 / math.pi)
    return tf.where(pred_value_angles >= 0, pred_value_angles, pred_value_angles + 360)



def getPredStonesDistsAngles(
    pred_black_dists, pred_black_angles, black_value,
    pred_white_dists, pred_white_angles, white_value
):
    def getStoneDistsAngles(pred_value_dists, pred_value_angles, stone_value):
        pred_value_dists_resh = reshapeAddDim(pred_value_dists)
        pred_value_angles_resh = reshapeAddDim(pred_value_angles)
        stone_value = tf.constant(stone_value, dtype='float32')
        pred_value_stones = tf.fill(pred_value_dists_resh.shape, stone_value)
        return tf.concat([pred_value_stones, pred_value_dists_resh, pred_value_angles_resh], axis=3)
    pred_black_stone_dists_angles = getStoneDistsAngles(
        pred_black_dists, pred_black_angles, black_value
    )
    pred_white_stone_dists_angles = getStoneDistsAngles(
        pred_white_dists, pred_white_angles, white_value
    )
    pred_stones_dists_angles = tf.concat(
        [pred_black_stone_dists_angles, pred_white_stone_dists_angles], axis=2
    )
    pred_stones_dists_angles = reshapeMergeDims(pred_stones_dists_angles, [0, 1])
    pred_stones_dists_angles = tf.vectorized_map(
        fn=lambda pred_empty: sort2dByCol(pred_empty, 1),
        elems=pred_stones_dists_angles
    )
    return pred_stones_dists_angles

####################################################################################################

def getRawInfls(pred_stones, pred_dists, max_dist):
    """ Tensor representing the raw base influences of each stone on each empty coord for each
    predicted next move."""
    raw_infls = (max_dist - pred_dists) * pred_stones
    raw_infls = applyScale(raw_infls, [0, max_dist], [0, 1])
    return raw_infls

####################################################################################################

def getDistDecayInflsAdjs(pred_dists, dist_decay_gt_weight, dist_decay_lin_weight):
    """ Tensor representing the decay of values of raw_infls based on dist. """
    return tf.cast(tf.where(
        pred_dists > dist_decay_gt_weight, dist_decay_lin_weight, 1
    ), dtype='float32')



def getDistZeroInflsAdjs(pred_dists, dist_zero_gt_weight):
    """ Tensor representing the zero out of values of raw_infls based on dist. """
    return tf.cast(tf.where(pred_dists > dist_zero_gt_weight, 0, 1), dtype='float32')



def getAngleDifs(pred_angles, both_count_per_pred):
    """ A tensor (with mirrored values) representing a matrix of angular differences between each
    stone within each empty coord within each predicted next move. """
    angle_tiled_y = tf.tile(reshapeInsertDim(pred_angles, 1), [1, both_count_per_pred, 1])
    angle_tiled_x = tf.tile(reshapeAddDim(pred_angles), [1, 1, both_count_per_pred])
    angle_difs = tf.abs(angle_tiled_x - angle_tiled_y)
    return tf.where(angle_difs > 180, 360 - angle_difs, angle_difs)



def getRawAngleInfls(angle_difs, angle_decay_lt_weight, angle_decay_lin_weight):
    """ A tensor (with mirrored values) representing a matrix of influences for each stone's angle
    vs each stone's angle per empty coord for each predicted move. """
    return tf.where(angle_difs <= angle_decay_lt_weight, angle_decay_lin_weight, 1)



def getAngleMirrorMask(both_count_per_pred, empty_count_all_pred):
    """ A bool tensor used to cancel out the unwanted mirrored values in raw_angle_infls. """
    mirror_shape = [both_count_per_pred] * 2
    mirror_coords = tf.cast(tf.where(tf.equal(tf.zeros(mirror_shape), 0)), dtype='int32')
    mirror_y = -tf.cast(mirror_coords[:, 0], dtype='float32')
    mirror_x = tf.cast(mirror_coords[:, 1], dtype='float32')
    mirror_angles = tf.atan2(mirror_y, mirror_x) * (180 / math.pi)
    mirror_angles = tf.where(mirror_angles > 0, mirror_angles, mirror_angles + 360)
    angle_mirror_mask = tf.where(mirror_angles < 315, True, False)
    angle_mirror_mask = tf.reshape(angle_mirror_mask, [1] + mirror_shape)
    return tf.tile(angle_mirror_mask, [empty_count_all_pred, 1, 1])



def getAngleStonesMask(pred_stones, both_count_per_pred, pred_value):
    """ A bool tensor used to cancel out the unwanted like-stone values in raw_angle_infls. """
    stones_tiled_y = tf.reshape(pred_stones, [-1, 1, both_count_per_pred])
    stones_tiled_y = tf.tile(stones_tiled_y, [1, both_count_per_pred, 1])
    stones_tiled_x = tf.reshape(pred_stones, [-1, both_count_per_pred, 1])
    stones_tiled_x = tf.tile(stones_tiled_x, [1, 1, both_count_per_pred])
    angle_stones_mask = stones_tiled_y * stones_tiled_x
    return tf.where(angle_stones_mask == -1, True, False)



def getMaskedAngleInfls(raw_angle_infls, angle_mirror_mask, angle_stones_mask):
    """ A tensor with the values of raw_angle_infls masked by angle_mirror_mask and
    angle_stones_mask. """
    masked_angle_infls = tf.where(angle_stones_mask, raw_angle_infls, 1)
    return tf.where(angle_mirror_mask, masked_angle_infls, 1)



def getAngleDecayInflsAdjs(masked_angle_infls):
    """ Tensor representing the decay of values of raw_infls based on angle barriers. """
    return tf.reduce_prod(masked_angle_infls, axis=2)

####################################################################################################

def reduceStoneInflsGetMoveInfls(pred_moves_stone_infls, pred_moves):
    """ Reduce stone influences to get move influences. """
    pred_move_infls = tf.reduce_sum(pred_moves_stone_infls, axis=1)
    pred_empty_coords_3d = tf.where(tf.equal(pred_moves, 0))
    pred_move_infls = tf.SparseTensor(pred_empty_coords_3d, pred_move_infls, pred_moves.shape)
    pred_move_infls = tf.sparse.to_dense(pred_move_infls)
    return pred_move_infls



def reduceMoveInflsGetPred(pred_move_infls, empty_coords, board_shape, board):
    """ Reduce move influences to get prediction output (influence data). """
    prediction = tf.reduce_sum(tf.reduce_sum(pred_move_infls, axis=2), axis=1)
    prediction = tf.SparseTensor(tf.cast(empty_coords, dtype='int64'), prediction, board_shape)
    prediction = tf.sparse.to_dense(prediction)
    prediction = applyScale(
        prediction, [tf.reduce_min(prediction), tf.reduce_max(prediction)], [0, 1]
    )
    prediction = tf.where(board == 0, prediction, 0)
    return prediction

####################################################################################################

# def getBoardInfluence(board):
#
#     max_dist = getDistTwoPoints([0, 0], [ x - 1 for x in board.size ])
#     stones = board.stones['black'] + board.stones['white']
#     board_infl = []
#     for y, row in enumerate(board.grid):
#         row_infl = []
#         for x, stone_at_pos in enumerate(row):
#             pos_infl = 0
#             # Positions with stones get 0 influence.
#             if stone_at_pos:  row_infl += [ pos_infl ] ; continue
#
#             for stone in stones:
#
#                 stone_infl = getDistTwoPoints([y, x], stone.pos)
#                 stone_infl = applyScale(stone_infl, [max_dist, 1.0], [0.0, 100.0])
#                 stone_infl = applySkew(stone_infl, -20.0, +0.8, 'lin')
#                 stone_infl = applyClamp(stone_infl, [0.0, 100.0])
#
#                 if stone.color == 'white':  stone_infl = -stone_infl
#                 pos_infl += stone_infl
#
#             # stones_data = getStonesDataTable([y, x], stones)
#             # for i in range(len(stones_data)):
#
#             row_infl += [ pos_infl ]
#         board_infl += [ row_infl ]
#     return board_infl
#
#
#
# def getStonesDataTable(pos, stones):
#
#     stones_data = []
#     for stone in stones:
#         stone_data = {}
#
#         stone_data['pos'] = str(pos)
#         stone_data['stone_pos'] = str(stone.pos)
#         stone_data['stone_color'] = stone.color
#         stone_data['distance'] = getDistTwoPoints(pos, stone.pos)
#         stone_data['angle'] = getAngleTwoPoints(pos, stone.pos)
#
#         stone_data['influence'] = infl
#
#         stones_data += [ stone_data ]
#
#     stones_data = sorted(stones_data, key=lambda x: x['angle'])
#     stones_data = sorted(stones_data, key=lambda x: x['distance'])
#
#     stones_data = pandas.DataFrame(stones_data)
#     print(stones_data)
#
#     return stones_data
