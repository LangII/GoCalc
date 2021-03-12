
import tensorflow as tf

####################################################################################################

# Do not decorate this func because it does not return a tensor.
def getCountOfValue(t, v):
    return int(tf.reduce_sum(tf.cast(tf.equal(t, v), dtype='int32')).numpy())

@tf.function
def getPosOfValue(t, v):
    return tf.cast(tf.where(tf.equal(t, v)), dtype=t.dtype)

@tf.function
def reshapeFlatten(t):
    return tf.reshape(t, [-1])

@tf.function
def reshapeInsertDim(t, dim):
    reshape = t.shape.as_list()
    reshape.insert(dim, 1)
    return tf.reshape(t, reshape)

@tf.function
def reshapeAddDim(t):
    reshape = t.shape.as_list()
    reshape += [1]
    return tf.reshape(t, reshape)

@tf.function
def reshapeMergeDims(t, dims):
    reshape = t.shape.as_list()
    del reshape[dims[0]:(dims[1] + 1)]
    reshape.insert(dims[0], -1)
    return tf.reshape(t, reshape)

@tf.function
def replaceValueAtIndex(t, v, i):
    bool_mask = tf.sparse.to_dense(tf.SparseTensor([i], [True], t.shape))
    return tf.cast(tf.where(bool_mask, v, t), dtype=t.dtype)

@tf.function
def sort2dByCol(t, col=0, dir=-1):
    """
    t =     2D input tensor.
    col =   Which column of t to sort by.
    dir =   Accepts +1 or -1 to determine descending sort or ascending sort respectively.
    Return tensor parallel to t where rows are sorted in dir order based on col.
    """
    return tf.gather(t, tf.nn.top_k((t[:, col] * dir), k=t.shape[0]).indices)

@tf.function
def applyScale(t, scale_from=[], scale_to=[]):
    """
    t =             Input tensor.
    scale_from =    Tensor of shape [2] where scale_from[0] is minimum value to be scaled from and
                    scale_from[1] is maximum value to be scaled from.
    scale_to =      Tensor of shape [2] where scale_to[0] is minimum value to be scaled to and
                    scale_to[1] is maximum value to be scaled to.
    Return tensor parallel to t where each value is scaled from scale_from to scale_to.
    """
    t = (t - scale_from[0]) / (scale_from[1] - scale_from[0])
    return t * (scale_to[1] - scale_to[0]) + scale_to[0]
