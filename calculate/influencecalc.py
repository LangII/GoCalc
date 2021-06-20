


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


####################################################################################################


np.set_printoptions(
    linewidth=220, # <- How many characters per line before new line.
    # threshold=300, # <- How many lines allowed before summarized print.
    threshold=sys.maxsize, # <- How many lines allowed before summarized print. (no summarization)
    edgeitems=10, # <- When summarized, how many edge values are printed.
    suppress=True, # <- Suppress scientific notation.
    precision=2, # <- How many decimal places on floats.
    # sign='+', # <- Display + for positive numbers.
)


####################################################################################################


EMPTY_VALUE = 0
BLACK_VALUE = +1
WHITE_VALUE = -1

MAIN_DTYPE = 'int32'


####################################################################################################


def getInfluenceData():
    """ Main return function of influencecalc.py. """

    """ COLLECT INPUTS FROM app_data """
    app_data = App.get_running_app().data
    board = getBoardTensorFromBoardObj(app_data['board'])
    # print(board, "<- board\n")
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

    """ HANDLE EMPTY BOARD ERROR """
    if both_count == 0:  return tf.zeros(board_shape, dtype=MAIN_DTYPE).numpy()

    """ START BUILDING TENSORS """
    empty_coords = getEmptyCoords(board)
    # print(empty_coords, "<- empty_coords\n")
    pred_moves = getPredMoves(board, board_shape, empty_count, empty_coords, pred_value)
    # print(pred_moves, "<- pred_moves\n")
    ### Logic must change to handle 'cur_infl' display_mode.
    if display_mode == 'cur_infl':
        pred_moves = reshapeInsertDim(board, 0)
        empty_count_per_pred = empty_count
        black_count_per_pred = black_count
        white_count_per_pred = white_count
        both_count_per_pred = both_count
        empty_count_all_pred = empty_count
        empty_count = 1
    # print(pred_moves, "<- pred_moves\n")
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
    # print(angle_decay_infls_adjs, "<- angle_decay_infls_adjs")

    """ GET OPPOSITE ANGLE GROWTH INFLUENCE ADJUSTMENT """
    wall_coords = getWallCoords(
        pred_empty_coords, empty_count_all_pred, empty_count, board_shape, empty_count_per_pred
    )
    # print(wall_coords, "<- wall_coords")
    pred_stones_dists_angles_with_wall = getPredStonesDistsAnglesWithWall(
        wall_coords, pred_empty_coords, pred_stones_dists_angles, empty_count
    )
    # print(pred_stones_dists_angles_with_wall, "<- pred_stones_dists_angles_with_wall")
    closest_stones = pred_stones_dists_angles[:, 0, :]
    # print(closest_stones, "<- closest_stones")
    closest_opp_stone = getClosestOppStone(
        closest_stones, both_count_per_pred, pred_stones_dists_angles_with_wall,
        opp_angle_growth_angle_lt_weight, empty_count_all_pred
    )
    # print(closest_opp_stone, "<- closest_opp_stone")
    opp_angle_growth_infls_adjs = getOppAngleGrowthInflsAdjs(
        closest_stones, closest_opp_stone, opp_angle_growth_dist_lt_weight,
        opp_angle_growth_lin_weight, pred_moves
    )
    # print(opp_angle_growth_infls_adjs, "<- opp_angle_growth_infls_adjs")

    """ APPLY WEIGHT ADJUSTMENTS TO STONE INFLUENCES """
    pred_moves_stone_infls = raw_infls
    if dist_decay_adj:  pred_moves_stone_infls *= dist_decay_infls_adjs
    if dist_zero_adj:  pred_moves_stone_infls *= dist_zero_infls_adjs
    if angle_decay_adj:  pred_moves_stone_infls *= angle_decay_infls_adjs

    """ REDUCE STONE INFLUENCES TO GET MOVE INFLUENCES """
    pred_move_infls = reduceStoneInflsGetMoveInfls(pred_moves_stone_infls, pred_moves)

    """ APPLY WEIGHT ADJUSTMENTS TO MOVE INFLUENCES """
    if opp_angle_growth_adj:  pred_move_infls *= opp_angle_growth_infls_adjs
    if clamp_adj:  pred_move_infls = applyClampAdjs(pred_move_infls, clamp_within_weight)
    # print(pred_move_infls, "<- pred_move_infls")

    """ RETURN INFLUENCE DATA BASED ON display_mode """
    if display_mode == 'cur_infl':
        influence_data = mergeDimsAndScaleInfls(pred_move_infls).numpy()
    else:  # 'infl_pred'
        influence_data = reduceMoveInflsGetPred(
            pred_move_infls, empty_coords, board_shape, board, pred_value
        ).numpy()
    print(influence_data, "<- influence_data")

    return influence_data


####################################################################################################


def getPredValue(app_data):
    """ Extract stone value to be predicted from app_data. """
    return BLACK_VALUE if app_data['influence']['predicting_stone'] == 'black' else WHITE_VALUE



def getCountPerPred(stone_value, stone_count, pred_value):
    """ Quick helper to get count_per_pred. """
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
    @tf.function
    def getSparsePredMoves(coord):
        return tf.sparse.to_dense(tf.SparseTensor([coord], [pred_value], board_shape))
    sparse_pred_moves = tf.map_fn(fn=lambda coord: getSparsePredMoves(coord), elems=empty_coords)
    tiled_board = tf.tile(tf.reshape(board, [1, *board_shape]), [empty_count, 1, 1])
    pred_moves = sparse_pred_moves + tiled_board
    return pred_moves



def getPredValueCoords(pred_moves, value, empty_count):
    """ Similar to empty_coords.  Except what empty_coords does for the current board position,
    pred_value_coords does for every possible board position (pred_moves) in pred_moves for value. """
    pred_value_coords = tf.cast(tf.where(tf.equal(pred_moves, value)), dtype='int32')
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
    pred_black_dists, pred_black_angles, black_value, pred_white_dists, pred_white_angles,
    white_value
):
    """ Tensor representing each stone's data (value, dist, angle) in relation to each empty coord,
    for each pred move board (each empty coord's sub dim is sorted by stone's dist).
    NOTES:
        - pred_stones_dists_angles is the primary tensor to be fed into the model's weights
        application layers.
        - pred_stones_dists_angles' shape remains to not have the outer layer representing each
        predicted next move.  This is for the purpose of faster calculations and the output must be
        reshaped after calculations. """
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


def getWallCoords(
    pred_empty_coords, empty_count_all_pred, empty_count, board_shape, empty_count_per_pred
):
    """ wall_coords is used in adding "support" stones in the place of the nearest wall to simulate
    how influence is increased when the pos is "sandwiched" between a stone and wall. """
    pred_empty_coords_resh = tf.cast(reshapeMergeDims(pred_empty_coords, [0, 1]), dtype='int64')
    min_filler = tf.fill([empty_count_all_pred, 1], tf.constant(-1, dtype='int64'))
    max_filler = tf.fill([empty_count_all_pred, 1], tf.constant(board_shape[0], dtype='int64'))
    top_wall_coords = tf.concat([min_filler, reshapeAddDim(pred_empty_coords_resh[:, 1])], axis=1)
    top_wall_coords = reshapeInsertDim(top_wall_coords, 1)
    bottom_wall_coords = tf.concat([max_filler, reshapeAddDim(pred_empty_coords_resh[:, 1])], axis=1)
    bottom_wall_coords = reshapeInsertDim(bottom_wall_coords, 1)
    left_wall_coords = tf.concat([reshapeAddDim(pred_empty_coords_resh[:, 0]), min_filler], axis=1)
    left_wall_coords = reshapeInsertDim(left_wall_coords, 1)
    right_wall_coords = tf.concat([reshapeAddDim(pred_empty_coords_resh[:, 0]), max_filler], axis=1)
    right_wall_coords = reshapeInsertDim(right_wall_coords, 1)
    wall_coords = tf.concat([
        top_wall_coords, bottom_wall_coords, left_wall_coords, right_wall_coords
    ], axis=1)
    wall_dists = tf.concat([
        reshapeInsertDim(pred_empty_coords_resh[:, 0], 1),
        reshapeInsertDim(board_shape[0] - pred_empty_coords_resh[:, 0] - 1, 1),
        reshapeInsertDim(pred_empty_coords_resh[:, 1], 1),
        reshapeInsertDim(board_shape[1] - pred_empty_coords_resh[:, 1] - 1, 1),
    ], axis=1)
    wall_dists_min = tf.argmin(wall_dists, axis=1)
    wall_coord_concat = tf.concat([
        reshapeAddDim(tf.cast(tf.range(empty_count_all_pred), dtype='int64')),
        reshapeAddDim(wall_dists_min)
    ], axis=1)
    wall_coords = tf.gather_nd(wall_coords, wall_coord_concat)
    wall_coords = tf.reshape(wall_coords, [empty_count, empty_count_per_pred, 2])
    wall_coords = tf.cast(wall_coords, dtype=MAIN_DTYPE)
    return wall_coords



def getPredStonesDistsAnglesWithWall(
    wall_coords, pred_empty_coords, pred_stones_dists_angles, empty_count
):
    """ Returns output similar to getPredStonesDistsAngles().  Except each outer dim element has an
     additional row of data that represents an additional stone at an exterior point at the nearest
     wall. """
    wall_normals = wall_coords - tf.cast(pred_empty_coords, dtype=MAIN_DTYPE)
    wall_normals = reshapeInsertDim(wall_normals, 2)
    wall_dists = getDistsFromNormals(wall_normals)
    wall_angles = getAnglesFromNormals(wall_normals)
    wall_stones = tf.reshape(pred_stones_dists_angles[:, 0, 0], [empty_count, -1, 1])
    wall_stone_dists_angles = reshapeInsertDim(tf.concat([
        wall_stones, wall_dists, wall_angles
    ], axis=2), 2)
    wall_stone_dists_angles = reshapeMergeDims(wall_stone_dists_angles, [0, 1])
    pred_stones_dists_angles_with_wall = tf.concat(
        [pred_stones_dists_angles, wall_stone_dists_angles], axis=1
    )
    pred_stones_dists_angles_with_wall = tf.vectorized_map(
        fn=lambda pred_empty: sort2dByCol(pred_empty, 1),
        elems=pred_stones_dists_angles_with_wall
    )
    return pred_stones_dists_angles_with_wall



def getClosestOppStone(
    closest_stones, both_count_per_pred, pred_stones_dists_angles_with_wall,
    opp_angle_growth_angle_lt_weight, empty_count_all_pred
):
    """ Return representation of closest opposite stone to closest stone. """
    closest_stones_angles = closest_stones[:, 2]
    opposite_angles = tf.where(
        closest_stones_angles >= 180, closest_stones_angles - 180, closest_stones_angles + 180
    )
    opposite_angles_tiled = tf.tile(reshapeAddDim(opposite_angles), [1, both_count_per_pred + 1])
    opp_angles_dif = tf.abs(pred_stones_dists_angles_with_wall[:, :, 2] - opposite_angles_tiled)
    opp_angles_dif = tf.where(opp_angles_dif > 180, 360 - opp_angles_dif, opp_angles_dif)
    opp_angles_mask = tf.where(opp_angles_dif <= opp_angle_growth_angle_lt_weight, True, False)
    closest_opp_stone = tf.argmax(opp_angles_mask, axis=1)
    closest_opp_stone = tf.gather_nd(
        pred_stones_dists_angles_with_wall,
        tf.concat([
            reshapeAddDim(tf.range(empty_count_all_pred)),
            tf.cast(reshapeAddDim(closest_opp_stone), dtype=MAIN_DTYPE)
        ], axis=1)
    )
    return closest_opp_stone



def getOppAngleGrowthInflsAdjs(
    closest_stones, closest_opp_stone, opp_angle_growth_dist_lt_weight,
    opp_angle_growth_lin_weight, pred_moves
):
    """ Get influence adjustment based on opp_angle """
    is_support_stone = closest_stones[:, 0] == closest_opp_stone[:, 0]
    is_within_dist = (closest_stones[:, 1] + closest_opp_stone[:, 1]) < opp_angle_growth_dist_lt_weight
    opp_angle_growth_infl_adjs = tf.where(
        tf.logical_and(is_support_stone, is_within_dist), opp_angle_growth_lin_weight, 1.0
    )
    pred_empty_coords_3d = tf.where(tf.equal(pred_moves, 0))
    opp_angle_growth_infl_adjs = tf.SparseTensor(
        pred_empty_coords_3d, opp_angle_growth_infl_adjs, pred_moves.shape
    )
    opp_angle_growth_infl_adjs = tf.sparse.to_dense(opp_angle_growth_infl_adjs)
    return opp_angle_growth_infl_adjs


####################################################################################################


def reduceStoneInflsGetMoveInfls(pred_moves_stone_infls, pred_moves):
    """ Reduce stone influences to get move influences. """
    pred_move_infls = tf.reduce_sum(pred_moves_stone_infls, axis=1)
    pred_empty_coords_3d = tf.where(tf.equal(pred_moves, 0))
    pred_move_infls = tf.SparseTensor(pred_empty_coords_3d, pred_move_infls, pred_moves.shape)
    pred_move_infls = tf.sparse.to_dense(pred_move_infls)
    return pred_move_infls



def applyClampAdjs(pred_move_infls, clamp_within_weight):
    """ Apply clamp limits to influences. """
    return tf.clip_by_value(pred_move_infls, -clamp_within_weight, clamp_within_weight)



def mergeDimsAndScaleInfls(pred_move_infls):
    """  """
    influence = reshapeMergeDims(pred_move_infls, [0, 1])

    infl_min = tf.abs(tf.reduce_min(influence))
    infl_max = tf.abs(tf.reduce_max(influence))
    infl_max = tf.reduce_max(tf.concat([infl_min, infl_max], axis=0))

    neg_infl = tf.where(influence <= 0, influence, 0)
    neg_infl = applyScale(
        # neg_infl, [tf.reduce_min(neg_infl), tf.reduce_max(neg_infl)], [-1, 0]
        neg_infl, [-infl_max, tf.reduce_max(neg_infl)], [-1, 0]
    )
    neg_infl = tf.where(tf.math.is_nan(neg_infl), 0, neg_infl)
    pos_infl = tf.where(influence > 0, influence, 0)
    pos_infl = applyScale(
        # pos_infl, [tf.reduce_min(pos_infl), tf.reduce_max(pos_infl)], [0, 1]
        pos_infl, [tf.reduce_min(pos_infl), infl_max], [0, 1]
    )
    pos_infl = tf.where(tf.math.is_nan(pos_infl), 0, pos_infl)
    influence = neg_infl + pos_infl
    return influence



def reduceMoveInflsGetPred(pred_move_infls, empty_coords, board_shape, board, pred_value):
    """ Reduce move influences to get prediction output (influence data). """
    prediction = tf.reduce_sum(tf.reduce_sum(pred_move_infls, axis=2), axis=1)
    prediction = tf.SparseTensor(tf.cast(empty_coords, dtype='int64'), prediction, board_shape)
    prediction = tf.sparse.to_dense(prediction)
    no_zeros = tf.gather_nd(prediction, tf.where(prediction != 0))
    input_low, input_high = tf.reduce_min(no_zeros), tf.reduce_max(no_zeros)
    if pred_value == WHITE_VALUE:  input_low, input_high = input_high, input_low
    prediction = applyScale(prediction, [input_low, input_high], [0, 1])
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
