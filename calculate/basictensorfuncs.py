
import tensorflow as tf

####################################################################################################

def getCount(t, v):
    return int(tf.reduce_sum(tf.cast(tf.equal(t, v), dtype='int32')).numpy())

def getCountOfValue(t, v):
    return int(tf.reduce_sum(tf.cast(tf.equal(t, v), dtype='int32')).numpy())

def getPosOfValue(t, v):
    return tf.cast(tf.where(tf.equal(t, v)), dtype=t.dtype)

def reshapeFlatten(t):
    return tf.reshape(t, [-1])

def reshapeInsertDim(t, dim):
    reshape = t.shape.as_list()
    reshape.insert(dim, 1)
    return tf.reshape(t, reshape)

def reshapeAddDim(t):
    reshape = t.shape.as_list()
    reshape += [1]
    return tf.reshape(t, reshape)

def reshapeMergeDims(t, dims):
    reshape = t.shape.as_list()
    del reshape[dims[0]:(dims[1] + 1)]
    reshape.insert(dims[0], -1)
    return tf.reshape(t, reshape)

def replaceValueAtIndex(t, v, i):
    bool_mask = tf.sparse.to_dense(tf.SparseTensor([i], [True], t.shape))
    return tf.cast(tf.where(bool_mask, v, t), dtype=t.dtype)
