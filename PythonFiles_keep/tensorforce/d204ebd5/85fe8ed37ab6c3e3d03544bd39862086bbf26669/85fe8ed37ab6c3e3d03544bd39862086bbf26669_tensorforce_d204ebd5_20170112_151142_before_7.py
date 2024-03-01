# Copyright 2016 reinforce.io. All Rights Reserved.
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

"""
Models provide the general interface to TensorFlow functionality,
manages TensorFlow session and execution. In particular, a model for reinforcement learning
always needs to provide a function that gives an action, and one to trigger updates.
A model may use one more multiple neural networks and implement the update logic of a particular
RL algorithm.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import tensorflow as tf

from tensorforce.util.exploration_util import exploration_mode

class Model(object):
    def __init__(self, config):
        """

        :param config: Configuration parameters
        """

        # TODO move several default params up here
        self.session = tf.Session()
        self.total_states = 0
        self.saver = None

        self.batch_shape = [None]

        self.deterministic_mode = config.get('deterministic_mode', False)

        exploration = config.get('exploration')
        if not exploration:
            self.exploration = exploration_mode['constant'](self.deterministic_mode, 0)
        else:
            kwargs = config.get('exploration_param', {})
            self.exploration = exploration_mode[exploration](self.deterministic_mode, **kwargs)

    def get_action(self, state):
        raise NotImplementedError

    def update(self, batch):
        raise NotImplementedError

    def load_model(self, path):
        self.saver.restore(self.session, path)

    def save_model(self, path):
        self.saver.save(self.session, path)
