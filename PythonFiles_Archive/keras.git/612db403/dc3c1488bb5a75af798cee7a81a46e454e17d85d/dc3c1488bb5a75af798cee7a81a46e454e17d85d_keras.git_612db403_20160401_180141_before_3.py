import pytest
import numpy as np
from numpy.testing import assert_allclose

from keras import backend as K
from keras.layers import core
from keras.utils.test_utils import layer_test


def test_masking():
    layer_test(core.Masking,
               kwargs={},
               input_shape=(3, 2, 3))


def test_merge():
    # test modes: 'sum', 'mul', 'concat', 'ave', 'cos', 'dot'.
    # test lambda with output_shape lambda
    # test function with output_shape function
    pass


def test_dropout():
    layer_test(core.Dropout,
               kwargs={'p': 0.5},
               input_shape=(3, 2))


def test_activation():
    # with string argument
    layer_test(core.Activation,
               kwargs={'activation': 'relu'},
               input_shape=(3, 2))

    # with function argument
    layer_test(core.Activation,
               kwargs={'activation': K.relu},
               input_shape=(3, 2))


def test_reshape():
    layer_test(core.Reshape,
               kwargs={'target_shape': (8, 1)},
               input_shape=(3, 2, 4))


def test_permute():
    layer_test(core.Permute,
               kwargs={'dims': (2, 1)},
               input_shape=(3, 2, 4))


def test_flatten():
    layer_test(core.Flatten,
               kwargs={},
               input_shape=(3, 2, 4))


def test_repeat_vector():
    layer_test(core.RepeatVector,
               kwargs={'n': 3},
               input_shape=(3, 2))


def test_lambda():
    from keras.utils.layer_utils import layer_from_config
    Lambda = core.Lambda

    layer_test(Lambda,
               kwargs={'function': lambda x: x + 1},
               input_shape=(3, 2))

    # test serialization with function
    def f(x):
        return x + 1

    ld = Lambda(f)
    config = ld.get_config()
    ld = layer_from_config({'class_name': 'Lambda', 'config': config})

    ld = Lambda(lambda x: K.concatenate([K.square(x), x]),
                output_shape=lambda s: tuple(list(s)[:-1] + [2 * s[-1]]))
    config = ld.get_config()
    ld = Lambda.from_config(config)

    # test serialization with output_shape function
    def f(x):
        return K.concatenate([K.square(x), x])

    def f_shape(s):
        return tuple(list(s)[:-1] + [2 * s[-1]])

    ld = Lambda(f, output_shape=f_shape)
    config = ld.get_config()
    ld = layer_from_config({'class_name': 'Lambda', 'config': config})


def test_dense():
    from keras import regularizers
    from keras import constraints

    layer_test(core.Dense,
               kwargs={'output_dim': 3},
               input_shape=(3, 2))

    layer_test(core.Dense,
               kwargs={'output_dim': 3,
                       'W_regularizer': regularizers.l2(0.01),
                       'b_regularizer': regularizers.l1(0.01),
                       'activity_regularizer': regularizers.activity_l2(0.01),
                       'W_constraint': constraints.MaxNorm(1),
                       'b_constraint': constraints.MaxNorm(1)},
               input_shape=(3, 2))


def test_activity_regularization():
    from keras.engine import Input, Model

    layer = core.ActivityRegularization(l1=0.01, l2=0.01)

    # test in functional API
    x = Input(shape=(3,))
    z = core.Dense(2)(x)
    y = layer(z)
    model = Model(input=x, output=y)
    model.compile('rmsprop', 'mse', mode='FAST_COMPILE')

    model.predict(np.random.random((2, 3)))

    # test serialization
    model_config = model.get_config()
    model = Model.from_config(model_config)
    model.compile('rmsprop', 'mse')


def test_maxout_dense():
    from keras import regularizers
    from keras import constraints

    layer_test(core.MaxoutDense,
               kwargs={'output_dim': 3},
               input_shape=(3, 2))

    layer_test(core.MaxoutDense,
               kwargs={'output_dim': 3,
                       'W_regularizer': regularizers.l2(0.01),
                       'b_regularizer': regularizers.l1(0.01),
                       'activity_regularizer': regularizers.activity_l2(0.01),
                       'W_constraint': constraints.MaxNorm(1),
                       'b_constraint': constraints.MaxNorm(1)},
               input_shape=(3, 2))


def test_highway():
    from keras import regularizers
    from keras import constraints

    layer_test(core.Highway,
               kwargs={},
               input_shape=(3, 2))

    layer_test(core.Highway,
               kwargs={'W_regularizer': regularizers.l2(0.01),
                       'b_regularizer': regularizers.l1(0.01),
                       'activity_regularizer': regularizers.activity_l2(0.01),
                       'W_constraint': constraints.MaxNorm(1),
                       'b_constraint': constraints.MaxNorm(1)},
               input_shape=(3, 2))


def test_timedistributeddense():
    from keras import regularizers
    from keras import constraints

    layer_test(core.TimeDistributedDense,
               kwargs={'output_dim': 2, 'input_length': 2},
               input_shape=(3, 2, 3))

    layer_test(core.TimeDistributedDense,
               kwargs={'output_dim': 3,
                       'W_regularizer': regularizers.l2(0.01),
                       'b_regularizer': regularizers.l1(0.01),
                       'activity_regularizer': regularizers.activity_l2(0.01),
                       'W_constraint': constraints.MaxNorm(1),
                       'b_constraint': constraints.MaxNorm(1)},
               input_shape=(3, 2, 3))


if __name__ == '__main__':
    pytest.main([__file__])
