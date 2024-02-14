# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Attention layers that can be used in sequence DNN/CNN models.

This file follows the terminology of https://arxiv.org/abs/1706.03762 Figure 2.
Attention is formed by three tensors: Query, Key and Value.
"""
# pylint: disable=g-classes-have-attributes,g-direct-tensorflow-import

from keras import backend
from keras.engine import base_layer
from keras.utils import control_flow_util
import tensorflow.compat.v2 as tf
from tensorflow.python.util.tf_export import keras_export


class BaseDenseAttention(base_layer.BaseRandomLayer):
  """Base Attention class for Dense networks.

  This class is suitable for Dense or CNN networks, and not for RNN networks.

  Implementations of attention mechanisms should inherit from this class, and
  reuse the `apply_attention_scores()` method.

  Args:
    causal: Boolean. Set to `True` for decoder self-attention. Adds a mask such
      that position `i` cannot attend to positions `j > i`. This prevents the
      flow of information from the future towards the past.
    dropout: Float between 0 and 1. Fraction of the units to drop for the
      attention scores.

  Call Args:

    inputs: List of the following tensors:
      * query: Query `Tensor` of shape `[batch_size, Tq, dim]`.
      * value: Value `Tensor` of shape `[batch_size, Tv, dim]`.
      * key: Optional key `Tensor` of shape `[batch_size, Tv, dim]`. If not
        given, will use `value` for both `key` and `value`, which is the
        most common case.
    mask: List of the following tensors:
      * query_mask: A boolean mask `Tensor` of shape `[batch_size, Tq]`.
        If given, the output will be zero at the positions where
        `mask==False`.
      * value_mask: A boolean mask `Tensor` of shape `[batch_size, Tv]`.
        If given, will apply the mask such that values at positions where
        `mask==False` do not contribute to the result.
    training: Python boolean indicating whether the layer should behave in
      training mode (adding dropout) or in inference mode (no dropout).
    return_attention_scores: bool, if `True`, returns the attention scores
      (after masking and softmax) as an additional output argument.

  Output:

    Attention outputs of shape `[batch_size, Tq, dim]`.
    [Optional] Attention scores after masking and softmax with shape
      `[batch_size, Tq, Tv]`.
  """

  def __init__(self, causal=False, dropout=0.0, **kwargs):
    super(BaseDenseAttention, self).__init__(**kwargs)
    self.causal = causal
    self.dropout = dropout
    self.supports_masking = True

  def _calculate_scores(self, query, key):
    """Calculates attention scores.

    Args:
      query: Query tensor of shape `[batch_size, Tq, dim]`.
      key: Key tensor of shape `[batch_size, Tv, dim]`.

    Returns:
      Tensor of shape `[batch_size, Tq, Tv]`.
    """
    return NotImplementedError

  def _apply_scores(self, scores, value, scores_mask=None, training=None):
    """Applies attention scores to the given value tensor.

    To use this method in your attention layer, follow the steps:

    * Use `query` tensor of shape `[batch_size, Tq]` and `key` tensor of shape
      `[batch_size, Tv]` to calculate the attention `scores`.
    * Pass `scores` and `value` tensors to this method. The method applies
      `scores_mask`, calculates `attention_distribution = softmax(scores)`, then
      returns `matmul(attention_distribution, value).
    * Apply `query_mask` and return the result.

    Args:
      scores: Scores float tensor of shape `[batch_size, Tq, Tv]`.
      value: Value tensor of shape `[batch_size, Tv, dim]`.
      scores_mask: A boolean mask `Tensor` of shape `[batch_size, 1, Tv]` or
        `[batch_size, Tq, Tv]`. If given, scores at positions where
        `scores_mask==False` do not contribute to the result. It must contain
        at least one `True` value in each line along the last dimension.
      training: Python boolean indicating whether the layer should behave in
        training mode (adding dropout) or in inference mode (no dropout).

    Returns:
      Tensor of shape `[batch_size, Tq, dim]`.
      Attention scores after masking and softmax with shape
        `[batch_size, Tq, Tv]`.
    """
    if scores_mask is not None:
      padding_mask = tf.logical_not(scores_mask)
      # Bias so padding positions do not contribute to attention distribution.
      # Note 65504. is the max float16 value.
      if scores.dtype is tf.float16:
        scores -= 65504. * tf.cast(padding_mask, dtype=scores.dtype)
      else:
        scores -= 1.e9 * tf.cast(padding_mask, dtype=scores.dtype)
    if training is None:
      training = backend.learning_phase()
    weights = tf.nn.softmax(scores)

    def dropped_weights():
      return self._random_generator.dropout(weights, rate=self.dropout)

    weights = control_flow_util.smart_cond(training, dropped_weights,
                                           lambda: tf.identity(weights))
    return tf.matmul(weights, value), weights

  # TODO(b/125916026): Consider exposing a __call__ method with named args.
  def call(self,
           inputs,
           mask=None,
           training=None,
           return_attention_scores=False):
    self._validate_call_args(inputs=inputs, mask=mask)
    q = inputs[0]
    v = inputs[1]
    k = inputs[2] if len(inputs) > 2 else v
    q_mask = mask[0] if mask else None
    v_mask = mask[1] if mask else None
    scores = self._calculate_scores(query=q, key=k)
    if v_mask is not None:
      # Mask of shape [batch_size, 1, Tv].
      v_mask = tf.expand_dims(v_mask, axis=-2)
    if self.causal:
      # Creates a lower triangular mask, so position i cannot attend to
      # positions j>i. This prevents the flow of information from the future
      # into the past.
      scores_shape = tf.shape(scores)
      # causal_mask_shape = [1, Tq, Tv].
      causal_mask_shape = tf.concat(
          [tf.ones_like(scores_shape[:-2]), scores_shape[-2:]],
          axis=0)
      causal_mask = _lower_triangular_mask(causal_mask_shape)
    else:
      causal_mask = None
    scores_mask = _merge_masks(v_mask, causal_mask)
    result, attention_scores = self._apply_scores(
        scores=scores, value=v, scores_mask=scores_mask, training=training)
    if q_mask is not None:
      # Mask of shape [batch_size, Tq, 1].
      q_mask = tf.expand_dims(q_mask, axis=-1)
      result *= tf.cast(q_mask, dtype=result.dtype)
    if return_attention_scores:
      return result, attention_scores
    return result

  def compute_mask(self, inputs, mask=None):
    self._validate_call_args(inputs=inputs, mask=mask)
    if mask:
      q_mask = mask[0]
      if q_mask is None:
        return None
      return tf.convert_to_tensor(q_mask)
    return None

  def compute_output_shape(self, input_shape):
    # return_attention_scores argument of BaseDenseAttention.call method
    # is ignored. Output shape of attention_scores cannot be returned.
    return tf.TensorShape(input_shape[0])

  def _validate_call_args(self, inputs, mask):
    """Validates arguments of the call method."""
    class_name = self.__class__.__name__
    if not isinstance(inputs, list):
      raise ValueError(
          f'{class_name} layer must be called on a list of inputs, '
          'namely [query, value] or [query, value, key]. '
          f'Received: {inputs}.')
    if len(inputs) < 2 or len(inputs) > 3:
      raise ValueError(
          f'{class_name} layer accepts inputs list of length 2 or 3, '
          'namely [query, value] or [query, value, key]. '
          f'Received length: {len(inputs)}.')
    if mask:
      if not isinstance(mask, list):
        raise ValueError(
            f'{class_name} layer mask must be a list, '
            f'namely [query_mask, value_mask]. Received: {mask}.')
      if len(mask) < 2 or len(mask) > len(inputs):
        raise ValueError(
            f'{class_name} layer mask must be a list of length 2, '
            f'namely [query_mask, value_mask]. Received length: {len(mask)}.')

  def get_config(self):
    config = {
        'causal': self.causal,
        'dropout': self.dropout,
    }
    base_config = super(BaseDenseAttention, self).get_config()
    return dict(list(base_config.items()) + list(config.items()))


@keras_export('keras.layers.Attention')
class Attention(BaseDenseAttention):
  """Dot-product attention layer, a.k.a. Luong-style attention.

  Inputs are `query` tensor of shape `[batch_size, Tq, dim]`, `value` tensor of
  shape `[batch_size, Tv, dim]` and `key` tensor of shape
  `[batch_size, Tv, dim]`. The calculation follows the steps:

  1. Calculate scores with shape `[batch_size, Tq, Tv]` as a `query`-`key` dot
     product: `scores = tf.matmul(query, key, transpose_b=True)`.
  2. Use scores to calculate a distribution with shape
     `[batch_size, Tq, Tv]`: `distribution = tf.nn.softmax(scores)`.
  3. Use `distribution` to create a linear combination of `value` with
     shape `[batch_size, Tq, dim]`:
     `return tf.matmul(distribution, value)`.

  Args:
    use_scale: If `True`, will create a scalar variable to scale the attention
      scores.
    causal: Boolean. Set to `True` for decoder self-attention. Adds a mask such
      that position `i` cannot attend to positions `j > i`. This prevents the
      flow of information from the future towards the past.
      Defaults to `False`.
    dropout: Float between 0 and 1. Fraction of the units to drop for the
      attention scores. Defaults to 0.0.
    score_mode: Function to use to compute attention scores, one of 
      `{"dot", "concat"}`. `"dot"` refers to the dot product between the query
      and key vectors. `"concat"` refers to the hyperbolic tangent of the 
      concatenation of the query and key vectors.

  Call Args:

    inputs: List of the following tensors:
      * query: Query `Tensor` of shape `[batch_size, Tq, dim]`.
      * value: Value `Tensor` of shape `[batch_size, Tv, dim]`.
      * key: Optional key `Tensor` of shape `[batch_size, Tv, dim]`. If not
        given, will use `value` for both `key` and `value`, which is the
        most common case.
    mask: List of the following tensors:
      * query_mask: A boolean mask `Tensor` of shape `[batch_size, Tq]`.
        If given, the output will be zero at the positions where
        `mask==False`.
      * value_mask: A boolean mask `Tensor` of shape `[batch_size, Tv]`.
        If given, will apply the mask such that values at positions where
        `mask==False` do not contribute to the result.
    return_attention_scores: bool, it `True`, returns the attention scores
      (after masking and softmax) as an additional output argument.
    training: Python boolean indicating whether the layer should behave in
      training mode (adding dropout) or in inference mode (no dropout).

  Output:

    Attention outputs of shape `[batch_size, Tq, dim]`.
    [Optional] Attention scores after masking and softmax with shape
      `[batch_size, Tq, Tv]`.

  The meaning of `query`, `value` and `key` depend on the application. In the
  case of text similarity, for example, `query` is the sequence embeddings of
  the first piece of text and `value` is the sequence embeddings of the second
  piece of text. `key` is usually the same tensor as `value`.

  Here is a code example for using `Attention` in a CNN+Attention network:

  ```python
  # Variable-length int sequences.
  query_input = tf.keras.Input(shape=(None,), dtype='int32')
  value_input = tf.keras.Input(shape=(None,), dtype='int32')

  # Embedding lookup.
  token_embedding = tf.keras.layers.Embedding(input_dim=1000, output_dim=64)
  # Query embeddings of shape [batch_size, Tq, dimension].
  query_embeddings = token_embedding(query_input)
  # Value embeddings of shape [batch_size, Tv, dimension].
  value_embeddings = token_embedding(value_input)

  # CNN layer.
  cnn_layer = tf.keras.layers.Conv1D(
      filters=100,
      kernel_size=4,
      # Use 'same' padding so outputs have the same shape as inputs.
      padding='same')
  # Query encoding of shape [batch_size, Tq, filters].
  query_seq_encoding = cnn_layer(query_embeddings)
  # Value encoding of shape [batch_size, Tv, filters].
  value_seq_encoding = cnn_layer(value_embeddings)

  # Query-value attention of shape [batch_size, Tq, filters].
  query_value_attention_seq = tf.keras.layers.Attention()(
      [query_seq_encoding, value_seq_encoding])

  # Reduce over the sequence axis to produce encodings of shape
  # [batch_size, filters].
  query_encoding = tf.keras.layers.GlobalAveragePooling1D()(
      query_seq_encoding)
  query_value_attention = tf.keras.layers.GlobalAveragePooling1D()(
      query_value_attention_seq)

  # Concatenate query and document encodings to produce a DNN input layer.
  input_layer = tf.keras.layers.Concatenate()(
      [query_encoding, query_value_attention])

  # Add DNN layers, and create Model.
  # ...
  ```
  """

  def __init__(self, use_scale=False, score_mode='dot', **kwargs):
    super(Attention, self).__init__(**kwargs)
    self.use_scale = use_scale
    self.score_mode= score_mode
    if self.score_mode not in ['dot', 'concat']:
      raise ValueError(
                f"Received: score_mode={score_mode}. Acceptable values "
                "are: ['dot', 'concat']"
            )

  def build(self, input_shape):
    """Creates scale variable if use_scale==True and
      v parameter if score_mode==concat"""
    if self.use_scale:
      self.scale = self.add_weight(
          name='scale',
          shape=(),
          initializer='ones',
          dtype=self.dtype,
          trainable=True)
    else:
      self.scale = None
    if self.score_mode == 'concat':
      self.attention_v = self.add_weight(
          name='attention_v',
          shape=(),
          initializer='ones',
          dtype=self.dtype,
          trainable=True)
    super(Attention, self).build(input_shape)

  def _calculate_scores(self, query, key):
    """Calculates attention scores as a query-key dot product.

    Args:
      query: Query tensor of shape `[batch_size, Tq, dim]`.
      key: Key tensor of shape `[batch_size, Tv, dim]`.
    Returns:
      Tensor of shape `[batch_size, Tq, Tv]`.
    """
    if self.score_mode == 'dot':
      scores = tf.matmul(query, key, transpose_b=True)
      if self.scale is not None:
        scores *= self.scale
    elif self.score_mode == 'concat':
      # Reshape tensors to enable broadcasting.
      # Reshape into [batch_size, Tq, 1, dim].
      q_reshaped = tf.expand_dims(query, axis=-2)
      # Reshape into [batch_size, 1, Tv, dim].
      k_reshaped = tf.expand_dims(key, axis=-3)
      if self.scale is not None:
        scores = self.attention_v * tf.reduce_sum(
         tf.tanh(self.scale * (q_reshaped + k_reshaped)), axis=-1)
      else:
        scores = self.attention_v * tf.reduce_sum(
         tf.tanh(q_reshaped + k_reshaped), axis=-1)

    return scores

  def get_config(self):
    config = {'use_scale': self.use_scale,
              'score_mode': self.score_mode}
    base_config = super(Attention, self).get_config()
    return dict(list(base_config.items()) + list(config.items()))


@keras_export('keras.layers.AdditiveAttention')
class AdditiveAttention(BaseDenseAttention):
  """Additive attention layer, a.k.a. Bahdanau-style attention.

  Inputs are `query` tensor of shape `[batch_size, Tq, dim]`, `value` tensor of
  shape `[batch_size, Tv, dim]` and `key` tensor of shape
  `[batch_size, Tv, dim]`. The calculation follows the steps:

  1. Reshape `query` and `key` into shapes `[batch_size, Tq, 1, dim]`
     and `[batch_size, 1, Tv, dim]` respectively.
  2. Calculate scores with shape `[batch_size, Tq, Tv]` as a non-linear
     sum: `scores = tf.reduce_sum(tf.tanh(query + key), axis=-1)`
  3. Use scores to calculate a distribution with shape
     `[batch_size, Tq, Tv]`: `distribution = tf.nn.softmax(scores)`.
  4. Use `distribution` to create a linear combination of `value` with
     shape `[batch_size, Tq, dim]`:
     `return tf.matmul(distribution, value)`.

  Args:
    use_scale: If `True`, will create a variable to scale the attention scores.
    causal: Boolean. Set to `True` for decoder self-attention. Adds a mask such
      that position `i` cannot attend to positions `j > i`. This prevents the
      flow of information from the future towards the past.
      Defaults to `False`.
    dropout: Float between 0 and 1. Fraction of the units to drop for the
      attention scores. Defaults to 0.0.

  Call Args:

    inputs: List of the following tensors:
      * query: Query `Tensor` of shape `[batch_size, Tq, dim]`.
      * value: Value `Tensor` of shape `[batch_size, Tv, dim]`.
      * key: Optional key `Tensor` of shape `[batch_size, Tv, dim]`. If not
        given, will use `value` for both `key` and `value`, which is the
        most common case.
    mask: List of the following tensors:
      * query_mask: A boolean mask `Tensor` of shape `[batch_size, Tq]`.
        If given, the output will be zero at the positions where
        `mask==False`.
      * value_mask: A boolean mask `Tensor` of shape `[batch_size, Tv]`.
        If given, will apply the mask such that values at positions where
        `mask==False` do not contribute to the result.
    training: Python boolean indicating whether the layer should behave in
      training mode (adding dropout) or in inference mode (no dropout).
    return_attention_scores: bool, it `True`, returns the attention scores
      (after masking and softmax) as an additional output argument.

  Output:

    Attention outputs of shape `[batch_size, Tq, dim]`.
    [Optional] Attention scores after masking and softmax with shape
      `[batch_size, Tq, Tv]`.

  The meaning of `query`, `value` and `key` depend on the application. In the
  case of text similarity, for example, `query` is the sequence embeddings of
  the first piece of text and `value` is the sequence embeddings of the second
  piece of text. `key` is usually the same tensor as `value`.

  Here is a code example for using `AdditiveAttention` in a CNN+Attention
  network:

  ```python
  # Variable-length int sequences.
  query_input = tf.keras.Input(shape=(None,), dtype='int32')
  value_input = tf.keras.Input(shape=(None,), dtype='int32')

  # Embedding lookup.
  token_embedding = tf.keras.layers.Embedding(max_tokens, dimension)
  # Query embeddings of shape [batch_size, Tq, dimension].
  query_embeddings = token_embedding(query_input)
  # Value embeddings of shape [batch_size, Tv, dimension].
  value_embeddings = token_embedding(value_input)

  # CNN layer.
  cnn_layer = tf.keras.layers.Conv1D(
      filters=100,
      kernel_size=4,
      # Use 'same' padding so outputs have the same shape as inputs.
      padding='same')
  # Query encoding of shape [batch_size, Tq, filters].
  query_seq_encoding = cnn_layer(query_embeddings)
  # Value encoding of shape [batch_size, Tv, filters].
  value_seq_encoding = cnn_layer(value_embeddings)

  # Query-value attention of shape [batch_size, Tq, filters].
  query_value_attention_seq = tf.keras.layers.AdditiveAttention()(
      [query_seq_encoding, value_seq_encoding])

  # Reduce over the sequence axis to produce encodings of shape
  # [batch_size, filters].
  query_encoding = tf.keras.layers.GlobalAveragePooling1D()(
      query_seq_encoding)
  query_value_attention = tf.keras.layers.GlobalAveragePooling1D()(
      query_value_attention_seq)

  # Concatenate query and document encodings to produce a DNN input layer.
  input_layer = tf.keras.layers.Concatenate()(
      [query_encoding, query_value_attention])

  # Add DNN layers, and create Model.
  # ...
  ```
  """

  def __init__(self, use_scale=True, **kwargs):
    super(AdditiveAttention, self).__init__(**kwargs)
    self.use_scale = use_scale

  def build(self, input_shape):
    v_shape = tf.TensorShape(input_shape[1])
    dim = v_shape[-1]
    dim = tf.compat.dimension_value(dim)
    if self.use_scale:
      self.scale = self.add_weight(
          name='scale',
          shape=[dim],
          initializer='glorot_uniform',
          dtype=self.dtype,
          trainable=True)
    else:
      self.scale = None
    super(AdditiveAttention, self).build(input_shape)

  def _calculate_scores(self, query, key):
    """Calculates attention scores as a nonlinear sum of query and key.

    Args:
      query: Query tensor of shape `[batch_size, Tq, dim]`.
      key: Key tensor of shape `[batch_size, Tv, dim]`.
    Returns:
      Tensor of shape `[batch_size, Tq, Tv]`.
    """
    # Reshape tensors to enable broadcasting.
    # Reshape into [batch_size, Tq, 1, dim].
    q_reshaped = tf.expand_dims(query, axis=-2)
    # Reshape into [batch_size, 1, Tv, dim].
    k_reshaped = tf.expand_dims(key, axis=-3)
    if self.use_scale:
      scale = self.scale
    else:
      scale = 1.
    return tf.reduce_sum(
        scale * tf.tanh(q_reshaped + k_reshaped), axis=-1)

  def get_config(self):
    config = {'use_scale': self.use_scale}
    base_config = super(AdditiveAttention, self).get_config()
    return dict(list(base_config.items()) + list(config.items()))


def _lower_triangular_mask(shape):
  """Creates a lower-triangular boolean mask over the last 2 dimensions."""
  row_index = tf.cumsum(
      tf.ones(shape=shape, dtype=tf.int32), axis=-2)
  col_index = tf.cumsum(
      tf.ones(shape=shape, dtype=tf.int32), axis=-1)
  return tf.greater_equal(row_index, col_index)


def _merge_masks(x, y):
  if x is None:
    return y
  if y is None:
    return x
  return tf.logical_and(x, y)
