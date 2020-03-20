#
# MNIST classifier example
#
# Credits: adapted from tf.keras tutorials and documentation
# See also: https://github.com/tensorflow/docs/blob/master/site/en/tutorials/distribute/multi_worker_with_keras.ipynb
# Environment variables setup for TF_CONFIG is performed externally
# A time.sleep() call is added to keep the container running after training is finished

import tensorflow as tf
import os

strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()

number_workers = int(os.environ["TOT_WORKERS"])
worker_number = os.environ["WORKER_NUMBER"]

mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train / 255.0
x_test = x_test / 255.0
x_train = x_train.reshape(60000,28,28,1)
x_test = x_test.reshape(10000,28,28,1)

BATCH_SIZE = 32 * number_workers
VAL_BATCH_SIZE = 100
num_train_samples = x_train.shape[0]
num_test_samples = x_test.shape[0]

train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_ds = train_ds.shuffle(10000).batch(BATCH_SIZE).cache().repeat()
test_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test)).cache().repeat()
test_ds = test_ds.batch(1000)

with strategy.scope():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, 3,
                               activation='relu',
                               input_shape=(28, 28, 1)),
        tf.keras.layers.MaxPool2D((2, 2)),
        tf.keras.layers.Conv2D(16, 3, activation='relu'),
        tf.keras.layers.MaxPool2D((2, 2)),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax'),
    ])
    model.summary()
    optimizer = tf.keras.optimizers.Adam()
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

print("Now training the distributed model")
history = model.fit(train_ds, epochs=10,
                    steps_per_epoch=num_train_samples // BATCH_SIZE,
                    callbacks=[tf.keras.callbacks.EarlyStopping(patience=2, monitor='accuracy')])

print("Finished training.\nNow computing validation loss and accuracy:")
model.evaluate(test_ds, steps=num_test_samples // VAL_BATCH_SIZE)


exit()
