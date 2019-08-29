## Copyright 2019 The TensorFlow Authors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# adapted from https://github.com/tensorflow/docs/blob/r2.0rc/site/en/r2/tutorials/distribute/multi_worker_with_keras.ipynb
# environment variables setup is performed esternally
# and a time.sleep() call is added to keep the container running after training is finished

import tensorflow as tf
import os
import json
import tensorflow_datasets as tfds

number_workers = int(os.environ["TOT_WORKERS"])
worker_number = os.environ["WORKER_NUMBER"]

tfds.disable_progress_bar()

strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
# tunables
BATCH_SIZE = 32 * number_workers
VAL_BATCH_SIZE = 2000
EPOCHS = 10

BUFFER_SIZE = 10000

# Scaling MNIST data from (0, 255] to (0., 1.]
def scale(image, label):
    image = tf.cast(image, tf.float32)
    image /= 255
    return image, label


datasets, info = tfds.load(name="mnist", with_info=True, as_supervised=True)

train_datasets_unbatched = datasets["train"].map(scale).shuffle(BUFFER_SIZE)
train_datasets = train_datasets_unbatched.batch(BATCH_SIZE).repeat()
test_datasets = datasets["test"].map(scale).batch(VAL_BATCH_SIZE)

def build_and_compile_cnn_model():
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Conv2D(32, 3, activation="relu", input_shape=(28, 28, 1)),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )
    model.compile(
        loss=tf.keras.losses.sparse_categorical_crossentropy,
        optimizer=tf.keras.optimizers.SGD(learning_rate=0.001),
        metrics=["accuracy"],
    )
    return model


steps_per_epoch = 60000 // BATCH_SIZE #the are 60000 samples in the training set
validation_steps = 10000 // VAL_BATCH_SIZE
with strategy.scope():
    multi_worker_model = build_and_compile_cnn_model()
print("Now training the distributed model")
history = multi_worker_model.fit(x=train_datasets, epochs=EPOCHS, steps_per_epoch=steps_per_epoch, verbose=1)


print("Finished training.\nNow computing loss and accuracy on the validation dataset:")
options = tf.data.Options()
options.experimental_distribute.auto_shard = False
test_datasets_no_auto_shard = test_datasets.with_options(options)
multi_worker_model.evaluate(test_datasets_no_auto_shard, steps=validation_steps)

exit()

