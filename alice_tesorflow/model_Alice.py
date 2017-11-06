from __future__ import division
import os
import time
from glob import glob
import tensorflow as tf
import numpy as np
from collections import namedtuple

from module import *
from utils import *

import pdb


class ALICE(object):
    def __init__(self, sess, args):
        self.sess = sess
        self.batch_size = args.batch_size
        self.image_size = args.fine_size
        self.input_c_dim = args.input_nc
        self.output_c_dim = args.output_nc
        self.L1_lambda = args.L1_lambda
        self.L1_lambda_sup = args.L1_lambda_sup
        self.cgan_lambda = args.cgan_lambda
        self.dataset_dir = args.dataset_dir
        self.edge_type = args.edge_type

        self.discriminator = discriminator
        self.discriminatorAB = discriminator_AB
        if args.use_resnet:
            self.generator = generator_resnet
        else:
            self.generator = generator_unet
        if args.use_lsgan:
            self.criterionGAN = mae_criterion
        else:
            self.criterionGAN = sce_criterion

        OPTIONS = namedtuple('OPTIONS', 'batch_size image_size \
                              gf_dim df_dim output_c_dim is_training')
        self.options = OPTIONS._make((args.batch_size, args.fine_size,
                                      args.ngf, args.ndf, args.output_nc,
                                      args.phase == 'train'))

        self._build_model()
        self.saver = tf.train.Saver()
        self.pool = ImagePool(args.max_size)

    def _build_model(self):
        self.real_data = tf.placeholder(tf.float32,
                                        [None, self.image_size, self.image_size,
                                         self.input_c_dim + self.output_c_dim],
                                        name='real_A_and_B_images')

        self.real_pair_data = tf.placeholder(tf.float32,
                                        [None, self.image_size, self.image_size,
                                         self.input_c_dim + self.output_c_dim],
                                        name='paired_A_and_B_images')

        self.real_A = self.real_data[:, :, :, :self.input_c_dim]
        self.real_B = self.real_data[:, :, :, self.input_c_dim:self.input_c_dim + self.output_c_dim]

        self.real_A_p = self.real_pair_data[:, :, :, :self.input_c_dim]
        self.real_B_p = self.real_pair_data[:, :, :, self.input_c_dim:self.input_c_dim + self.output_c_dim]

        self.fake_B = self.generator(self.real_A, self.options, False, name="generatorA2B")
        self.fake_A_ = self.generator(self.fake_B, self.options, False, name="generatorB2A")
        self.fake_A = self.generator(self.real_B, self.options, True, name="generatorB2A")
        self.fake_B_ = self.generator(self.fake_A, self.options, True, name="generatorA2B")
        self.fake_A_p = self.generator(self.real_B_p, self.options, True, name="generatorB2A")
        self.fake_B_p = self.generator(self.real_A_p, self.options, True, name="generatorA2B")

        self.DB_fake = self.discriminator(self.fake_B, self.options, reuse=False, name="discriminatorB")
        self.DA_fake = self.discriminator(self.fake_A, self.options, reuse=False, name="discriminatorA")
        self.DAB_B_fake = self.discriminatorAB(tf.stack([self.real_A_p, self.fake_B_p], 3), self.options, reuse=False, name="discriminatorAB")
        self.DAB_A_fake = self.discriminatorAB(tf.stack([self.fake_A_p, self.real_B_p], 3), self.options, reuse=True,  name="discriminatorAB")

        self.g_loss_a2b = self.criterionGAN(self.DB_fake, tf.ones_like(self.DB_fake)) \
            + self.L1_lambda * abs_criterion(self.real_A, self.fake_A_) \
            + self.L1_lambda * abs_criterion(self.real_B, self.fake_B_) \
            + self.L1_lambda_sup * abs_criterion(self.real_A_p, self.fake_A_p) \
            + self.L1_lambda_sup * abs_criterion(self.real_B_p, self.fake_B_p) \
            + self.cgan_lambda * self.criterionGAN(self.DAB_B_fake, tf.ones_like(self.DAB_B_fake)) \
            + self.cgan_lambda * self.criterionGAN(self.DAB_A_fake, tf.ones_like(self.DAB_A_fake))

        self.g_loss_b2a = self.criterionGAN(self.DA_fake, tf.ones_like(self.DA_fake)) \
            + self.L1_lambda * abs_criterion(self.real_A, self.fake_A_) \
            + self.L1_lambda * abs_criterion(self.real_B, self.fake_B_) \
            + self.L1_lambda_sup * abs_criterion(self.real_A_p, self.fake_A_p) \
            + self.L1_lambda_sup * abs_criterion(self.real_B_p, self.fake_B_p) \
            + self.cgan_lambda * self.criterionGAN(self.DAB_B_fake, tf.ones_like(self.DAB_B_fake)) \
            + self.cgan_lambda * self.criterionGAN(self.DAB_A_fake, tf.ones_like(self.DAB_A_fake))

        self.g_loss = self.criterionGAN(self.DA_fake, tf.ones_like(self.DA_fake)) \
            + self.criterionGAN(self.DB_fake, tf.ones_like(self.DB_fake)) \
            + self.L1_lambda * abs_criterion(self.real_A, self.fake_A_) \
            + self.L1_lambda * abs_criterion(self.real_B, self.fake_B_) \
            + self.L1_lambda_sup * abs_criterion(self.real_A_p, self.fake_A_p) \
            + self.L1_lambda_sup * abs_criterion(self.real_B_p, self.fake_B_p) \
            + self.cgan_lambda * self.criterionGAN(self.DAB_B_fake, tf.ones_like(self.DAB_B_fake)) \
            + self.cgan_lambda * self.criterionGAN(self.DAB_A_fake, tf.ones_like(self.DAB_A_fake))

        self.fake_A_sample = tf.placeholder(tf.float32,
                                            [None, self.image_size, self.image_size,
                                             self.input_c_dim], name='fake_A_sample')
        self.fake_B_sample = tf.placeholder(tf.float32,
                                            [None, self.image_size, self.image_size,
                                             self.output_c_dim], name='fake_B_sample')
        self.real_A_sample_p = tf.placeholder(tf.float32,
                                            [None, self.image_size, self.image_size,
                                             self.input_c_dim], name='real_A_sample_p')
        self.real_B_sample_p = tf.placeholder(tf.float32,
                                            [None, self.image_size, self.image_size,
                                             self.output_c_dim], name='real_B_sample_p')

        self.DB_real = self.discriminator(self.real_B, self.options, reuse=True, name="discriminatorB")
        self.DA_real = self.discriminator(self.real_A, self.options, reuse=True, name="discriminatorA")
        self.DB_fake_sample = self.discriminator(self.fake_B_sample, self.options, reuse=True, name="discriminatorB")
        self.DA_fake_sample = self.discriminator(self.fake_A_sample, self.options, reuse=True, name="discriminatorA")
        self.DAB_real_sample_p = self.discriminatorAB(tf.stack([self.real_A_sample_p, self.real_A_sample_p], 3), self.options, reuse=True, name="discriminatorAB")

        self.db_loss_real = self.criterionGAN(self.DB_real, tf.ones_like(self.DB_real))
        self.db_loss_fake = self.criterionGAN(self.DB_fake_sample, tf.zeros_like(self.DB_fake_sample))
        self.db_loss = (self.db_loss_real + self.db_loss_fake) / 2
        self.da_loss_real = self.criterionGAN(self.DA_real, tf.ones_like(self.DA_real))
        self.da_loss_fake = self.criterionGAN(self.DA_fake_sample, tf.zeros_like(self.DA_fake_sample))
        self.da_loss = (self.da_loss_real + self.da_loss_fake) / 2
        self.dab_loss_real_p = self.criterionGAN(self.DAB_real_sample_p, tf.zeros_like(self.DAB_real_sample_p))
        self.d_loss = self.da_loss + self.db_loss + self.cgan_lambda * self.dab_loss_real_p


        self.g_loss_a2b_sum = tf.summary.scalar("g_loss_a2b", self.g_loss_a2b)
        self.g_loss_b2a_sum = tf.summary.scalar("g_loss_b2a", self.g_loss_b2a)
        self.g_loss_sum = tf.summary.scalar("g_loss", self.g_loss)
        self.g_sum = tf.summary.merge([self.g_loss_a2b_sum, self.g_loss_b2a_sum, self.g_loss_sum])
        self.db_loss_sum = tf.summary.scalar("db_loss", self.db_loss)
        self.da_loss_sum = tf.summary.scalar("da_loss", self.da_loss)
        self.d_loss_sum = tf.summary.scalar("d_loss", self.d_loss)
        self.db_loss_real_sum = tf.summary.scalar("db_loss_real", self.db_loss_real)
        self.db_loss_fake_sum = tf.summary.scalar("db_loss_fake", self.db_loss_fake)
        self.da_loss_real_sum = tf.summary.scalar("da_loss_real", self.da_loss_real)
        self.da_loss_fake_sum = tf.summary.scalar("da_loss_fake", self.da_loss_fake)
        self.d_sum = tf.summary.merge(
            [self.da_loss_sum, self.da_loss_real_sum, self.da_loss_fake_sum,
             self.db_loss_sum, self.db_loss_real_sum, self.db_loss_fake_sum,
             self.d_loss_sum]
        )

        self.test_A = tf.placeholder(tf.float32,
                                     [None, self.image_size, self.image_size,
                                      self.input_c_dim], name='test_A')
        self.test_B = tf.placeholder(tf.float32,
                                     [None, self.image_size, self.image_size,
                                      self.output_c_dim], name='test_B')
        self.testB = self.generator(self.test_A, self.options, True, name="generatorA2B")
        self.testA = self.generator(self.test_B, self.options, True, name="generatorB2A")

        t_vars = tf.trainable_variables()
        self.d_vars = [var for var in t_vars if 'discriminator' in var.name]
        self.g_vars = [var for var in t_vars if 'generator' in var.name]
        for var in t_vars: print(var.name)

    def obtain_data(self):

        def sort_paths(fpaths):
            idx_img = np.array([int(p.split('/')[-1].split('.')[0].split('_')[10]) for p in fpaths])
            idx2 = np.argsort(idx_img)
            fpaths = [fpaths[i] for i in idx2]
            return fpaths


        dataA_ = glob('../data_wonderland/{}/*.*'.format(self.dataset_dir + '/color_256'))
        dataB_ = glob('../data_wonderland/{}.*'.format(self.dataset_dir + '/edge_256/*'+self.edge_type))
        # pdb.set_trace()

        dataA_ = sort_paths(dataA_)
        dataB_ = sort_paths(dataB_)

        dstart, dend = 91, 143 # beginning and end index of training set (unsupervised)
        dataA = dataA_[dstart:dend]
        dataB = dataB_[dstart:dend]

        # pairwise info 
        idx_anchor = [95, 140] # two index of training set (supervised)
        dataAB = [ (dataA_[i], dataB_[i]) for i in idx_anchor]
        return dataA, dataB, dataAB


    def train(self, args):
        """Train cyclegan"""
        self.lr = tf.placeholder(tf.float32, None, name='learning_rate')
        self.d_optim = tf.train.AdamOptimizer(self.lr, beta1=args.beta1) \
            .minimize(self.d_loss, var_list=self.d_vars)
        self.g_optim = tf.train.AdamOptimizer(self.lr, beta1=args.beta1) \
            .minimize(self.g_loss, var_list=self.g_vars)

        init_op = tf.global_variables_initializer()
        self.sess.run(init_op)
        self.writer = tf.summary.FileWriter("./logs_alice", self.sess.graph)


        counter = 1
        start_time = time.time()


        if args.continue_train:
            if self.load(args.checkpoint_dir):
                print(" [*] Load SUCCESS")
            else:
                print(" [!] Load failed...")

        dataA, dataB, dataAB = self.obtain_data()

        # pairwise information
        # dataA_, dataB_ = dataA, dataB 

        for epoch in range(args.epoch):

            np.random.shuffle(dataA)
            np.random.shuffle(dataB)
            train_size = min(min(len(dataA), len(dataB)), args.train_size)

            idx_pair = np.random.shuffle(range(train_size))

            batch_idxs = train_size // self.batch_size
            lr = args.lr if epoch < args.epoch_step else args.lr*(args.epoch-epoch)/(args.epoch-args.epoch_step)

            for idx in range(0, batch_idxs):
                batch_files = list(zip(dataA[idx * self.batch_size:(idx + 1) * self.batch_size],
                                       dataB[idx * self.batch_size:(idx + 1) * self.batch_size]))

                
                batch_images = [load_train_data(batch_file, args.load_size, args.fine_size) for batch_file in batch_files]
                batch_images = np.array(batch_images).astype(np.float32)

                batch_pair_images = [load_train_data(batch_file, args.load_size, args.fine_size) for batch_file in dataAB]
                batch_pair_images = np.array(batch_pair_images).astype(np.float32)
                # pdb.set_trace()

                # Update G network and record fake outputs
                fake_A, fake_B, _, summary_str = self.sess.run(
                    [self.fake_A, self.fake_B, self.g_optim, self.g_sum],
                    feed_dict={self.real_data: batch_images, self.lr: lr, self.real_pair_data: batch_pair_images})
                self.writer.add_summary(summary_str, counter)
                [fake_A, fake_B] = self.pool([fake_A, fake_B])

                # Update D network
                _, summary_str = self.sess.run(
                    [self.d_optim, self.d_sum],
                    feed_dict={self.real_data: batch_images,
                               self.fake_A_sample: fake_A,
                               self.fake_B_sample: fake_B,
                               self.real_A_sample_p: batch_pair_images[:,:,:,:self.input_c_dim],
                               self.real_B_sample_p: batch_pair_images[:,:,:,self.input_c_dim:self.input_c_dim + self.output_c_dim],                          
                               self.lr: lr})
                self.writer.add_summary(summary_str, counter)

                counter += 1
                print(("Epoch: [%2d] [%4d/%4d] time: %4.4f" % (
                    epoch, idx, batch_idxs, time.time() - start_time)))

                if np.mod(counter, args.print_freq) == 1:
                    self.sample_model(args.sample_dir, epoch, idx)

                if np.mod(counter, args.save_freq) == 2:
                    self.save(args.checkpoint_dir, counter)

    def save(self, checkpoint_dir, step):
        model_name = "alice.model"
        model_dir = "%s_%s" % (self.dataset_dir, self.image_size)
        checkpoint_dir = os.path.join(checkpoint_dir, model_dir)

        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        self.saver.save(self.sess,
                        os.path.join(checkpoint_dir, model_name),
                        global_step=step)

    def load(self, checkpoint_dir):
        print(" [*] Reading checkpoint...")

        model_dir = "%s_%s" % (self.dataset_dir, self.image_size)
        checkpoint_dir = os.path.join(checkpoint_dir, model_dir)
        # pdb.set_trace()
        ckpt_name_ = "alice.model-" + "10002"
        ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
        if ckpt and ckpt.model_checkpoint_path:
            # ckpt_name = os.path.basename(ckpt.model_checkpoint_path)
            # ckpt_name = os.path.basename(ckpt.model_checkpoint_path)
            self.saver.restore(self.sess, os.path.join(checkpoint_dir, ckpt_name_))
            return True
        else:
            return False

    def sample_model(self, sample_dir, epoch, idx):
        dataA, dataB, _ = self.obtain_data()
        np.random.shuffle(dataA)
        np.random.shuffle(dataB)
        batch_files = list(zip(dataA[:self.batch_size], dataB[:self.batch_size]))
        sample_images = [load_train_data(batch_file, is_testing=True) for batch_file in batch_files]
        sample_images = np.array(sample_images).astype(np.float32)

        fake_A, fake_B = self.sess.run(
            [self.fake_A, self.fake_B],
            feed_dict={self.real_data: sample_images}
        )
        save_images(fake_A, [self.batch_size, 1],
                    './{}/A_{:02d}_{:04d}.jpg'.format(sample_dir, epoch, idx))
        save_images(fake_B, [self.batch_size, 1],
                    './{}/B_{:02d}_{:04d}.jpg'.format(sample_dir, epoch, idx))

    def test(self, args):
        """Test cyclegan"""
        init_op = tf.global_variables_initializer()
        self.sess.run(init_op)
        if args.which_direction == 'E2C':
            sample_files = glob('../data_wonderland/{}.*'.format(self.dataset_dir + '/edge_256/*'+self.edge_type))
        else:
            raise Exception('--which_direction must be edge to color')

        pdb.set_trace()

        if self.load(args.checkpoint_dir):
            print(" [*] Load SUCCESS")
        else:
            print(" [!] Load failed...")

        # write html for visual comparison
        index_path = os.path.join(args.test_dir, '{0}_index.html'.format(args.which_direction))
        index = open(index_path, "w")
        index.write("<html><body><table><tr>")
        index.write("<th>name</th><th>input</th><th>output</th></tr>")

        out_var, in_var = (self.testB, self.test_A) if args.which_direction == 'AtoB' else (
            self.testA, self.test_B)

        for sample_file in sample_files:
            print('Processing image: ' + sample_file)
            sample_image = [load_test_data(sample_file, args.fine_size)]
            sample_image = np.array(sample_image).astype(np.float32)
            image_path = os.path.join(args.test_dir,
                                      '{0}_{1}'.format(args.which_direction, os.path.basename(sample_file)))
            fake_img = self.sess.run(out_var, feed_dict={in_var: sample_image})
            save_images(fake_img, [1, 1], image_path)
            index.write("<td>%s</td>" % os.path.basename(image_path))
            index.write("<td><img src='%s'></td>" % (sample_file if os.path.isabs(sample_file) else (
                '..' + os.path.sep + sample_file)))
            index.write("<td><img src='%s'></td>" % (image_path if os.path.isabs(image_path) else (
                '..' + os.path.sep + image_path)))
            index.write("</tr>")
        index.close()
