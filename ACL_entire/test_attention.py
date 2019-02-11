from __future__ import print_function
from self_attention2 import self_attention
from self_attention import Position_Embedding
from test_load_data import get_data, data_generator, data_generator_output,analyze_data  # process_train_data
from keras.models import Model
from keras.layers import Dense, Dropout, Input, Embedding, concatenate, \
    GlobalAveragePooling1D, Conv1D, GlobalMaxPooling1D, TimeDistributed
from keras.layers import BatchNormalization, Activation
from keras.optimizers import Adam
import numpy as np
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
max_features = 20000
batch_size = 16
epo = 100
filters = 128
flag = 0.60
numclass = 5
audio_path = r'E:\\Yue\\Entire Data\\ACL_2018_entire\\Word_Mat_New_1\\'

# loading data
print('Loading data...')
train_audio_data, train_text_data, train_label, test_audio_data, test_text_data, test_label, test_label_o, embed_matrix, dic, token_data = get_data()
'''
np.save('train_audio_data3.npy',train_audio_data)
np.save('train_text_data3.npy',train_text_data)
np.save('train_label3.npy',train_label)

np.save('test_audio_data3.npy',test_audio_data)
np.save('test_text_data3.npy',test_text_data)
np.save('test_label3.npy',test_label)

np.save('test_label_o3.npy',test_label_o)
'''
print('train_audio shape:', len(train_audio_data))
print('train_text shape:', train_text_data.shape)
print('test_audio shape:', len(test_audio_data))
print('test_text shape:', test_text_data.shape)
print('train_label shape:', train_label.shape)
print('test_label shape:', test_label.shape)

# Text Branch (adam)
text_input = Input(shape=(50,))
print(len(dic))
em_text = Embedding(len(dic) + 1, 200, weights=[embed_matrix], trainable=True)(text_input)
em_text = Position_Embedding()(em_text)
text_att = self_attention(d_model=256,d_inner_hid=512,n_head=4,d_k=64,d_v=64,dropout=0.1)(em_text)
text_att1 = self_attention(d_model=256,d_inner_hid=512,n_head=4,d_k=64,d_v=64,dropout=0.1)(text_att)
text_att2 = self_attention(d_model=256,d_inner_hid=512,n_head=4,d_k=64,d_v=64,dropout=0.1)(text_att1)
text_att_gap = GlobalMaxPooling1D()(text_att2)
text_prediction = Dense(5, activation='softmax')(text_att_gap)
text_model = Model(inputs=text_input, outputs=text_prediction)
inter_text_model = Model(inputs=text_input, outputs=text_att2)
adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
text_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Text Branch (sgd)
text_input_s = Input(shape=(50,))
em_text_s = Embedding(len(dic) + 1, 200, weights=[embed_matrix], trainable=True)(text_input_s)
em_text = Position_Embedding()(em_text)
text_att_s = self_attention(d_model=256,d_inner_hid=512,n_head=4,d_k=64,d_v=64,dropout=0.1)(em_text_s)
text_att1_s = self_attention(d_model=256,d_inner_hid=512,n_head=4,d_k=64,d_v=64,dropout=0.1)(text_att_s)
text_att2_s = self_attention(d_model=256,d_inner_hid=512,n_head=4,d_k=64,d_v=64,dropout=0.1)(text_att1_s)
text_att_gap_s = GlobalMaxPooling1D()(text_att2_s)
text_prediction_s = Dense(5, activation='softmax')(text_att_gap_s)
text_model_s = Model(inputs=text_input_s, outputs=text_prediction_s)
inter_text_model_s = Model(inputs=text_input_s, outputs=text_att2_s)
text_model_s.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

text_acc = 0
train_text_inter = None
test_text_inter = None

loss = []
acc = []
epoch = np.linspace(1,200,200) #load

print('start adam')
for i in range(200):
    print('text branch, epoch: ', str(i))

    history = text_model.fit(train_text_data, train_label, batch_size=batch_size, epochs=1, verbose=1)
    loss.append(history.history['loss'])
    acc.append(history.history['acc'])
    loss_t, acc_t = text_model.evaluate(test_text_data, test_label, batch_size=batch_size, verbose=0)
    print('epoch: ', str(i))
    print('loss_t', loss_t, ' ', 'acc_t', acc_t)
    if acc_t >= text_acc:
        text_acc = acc_t
        train_text_inter = inter_text_model.predict(train_text_data, batch_size=batch_size)
        test_text_inter = inter_text_model.predict(test_text_data, batch_size=batch_size)
        text_model.save_weights(r'E:\Yue\Code\ACL_entire\text_model\\text_2_8.h5')
        inter_text_model.save_weights(r'E:\Yue\Code\ACL_entire\text_model\\inter_text_2_8.h5')
print('adam ends: ',text_acc)

print('sgd start')
text_model_s.load_weights(r'E:\Yue\Code\ACL_entire\text_model\\text_2_8.h5')
inter_text_model_s.load_weights(r'E:\Yue\Code\ACL_entire\text_model\\inter_text_2_8.h5')
for i in range(0):
    print('text branch, epoch: ', str(i))

    history=text_model_s.fit(train_text_data, train_label, batch_size=batch_size, epochs=1, verbose=1)
    loss.append(history.history['loss'])
    acc.append(history.history['acc'])
    loss_t, acc_t = text_model_s.evaluate(test_text_data, test_label, batch_size=batch_size, verbose=0)
    print('epoch: ', str(i))
    print('loss_t', loss_t, ' ', 'acc_t', acc_t)
    if acc_t >= text_acc:
        text_acc = acc_t
        train_text_inter = inter_text_model_s.predict(train_text_data, batch_size=batch_size)
        test_text_inter = inter_text_model_s.predict(test_text_data, batch_size=batch_size)
        text_model_s.save_weights(r'E:\Yue\Code\ACL_entire\text_model\\text_2_8.h5')
        inter_text_model_s.save_weights(r'E:\Yue\Code\ACL_entire\text_model\\inter_text_2_8.h5')
print('sgd ends :',text_acc)

text_model.load_weights(r'E:\Yue\Code\ACL_entire\text_model\\text_2_8.h5')
inter_text_model.load_weights(r'E:\Yue\Code\ACL_entire\text_model\\inter_text_2_8.h5')
loss_t, acc_t = text_model.evaluate(test_text_data, test_label, batch_size=batch_size, verbose=0)
text_acc = acc_t
train_text_inter = inter_text_model.predict(train_text_data, batch_size=batch_size)
test_text_inter = inter_text_model.predict(test_text_data, batch_size=batch_size)

result = text_model_s.predict([test_text_data], batch_size=batch_size)
result = np.argmax(result, axis=1)
r_0, r_1, r_2, r_3, r_4 = analyze_data(test_label_o, result)
print('final result: ')
print('text acc: ', text_acc)
print("0", r_0)
print("1", r_1)
print("2", r_2)
print("3", r_3)
print("4", r_4)

plt.figure()
plt.plot(epoch, loss, label='loss')
plt.plot(epoch, acc, label ='acc')
plt.xlabel("epoch")
plt.ylabel("audio loss and acc")
plt.legend()
plt.show()
