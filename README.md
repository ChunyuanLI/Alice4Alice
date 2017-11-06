# Alice4Alice
ALICE algorithms for painting the cartoon ["Alice's Adventures in Wonderland"](https://en.wikipedia.org/wiki/Alice%27s_Adventures_in_Wonderland)


**Ideas: Leveraging weakly-supervised information can significantly alleviate the non-identifiablility issues of CycleGAN/DiscoGAN/DualGAN in image-to-image translation.**

If interested, please check out the [main code repo](https://arxiv.org/abs/1709.01215) for our NIPS 2017 paper [ALICE](https://github.com/ChunyuanLI/ALICE): 


## Experiments

For 52 images (21 alice image and 31 rabbit images) in each domain (cartoon and edge), we provide 1 pairwise correspondence for each character, which significantly improves the generation quality.

### Results on sample correspondence

ALICE (*Explicit variant*)  | ![](/plot_generation/figures_alice/cartoon_alice_exp_200.png	) 
:-------------------------:|:-------------------------:
CycleGAN         |  ![](/plot_generation/figures_alice/cartoon_cyclegan_200.png)


As references:

Real Cartoon (Groundtruth)  | ![](/plot_generation/figures_alice/cartoon_real.png) 
:-------------------------:|:-------------------------:
Edges (Input) |  ![](/plot_generation/figures_alice/edges_out3_real.png)



### Detailed Comparison:

Rabbit
 ![](/plot_generation/figures_alice/cartoon_cmp_136.png) 
 
Alice 
 ![](/plot_generation/figures_alice/cartoon_cmp_100.png) 
 
Cat (remotely related to the training set) 
 ![](/plot_generation/figures_alice/cartoon_cmp_10.png) 


## How to use

The scripts to train and test with various algorithms are in [`alice_tesorflow/script.sh`](/alice_tesorflow/script.sh). For example, training with explicit ALICE:

     $ CUDA_VISIBLE_DEVICES=0 python main.py --checkpoint_dir ./alice_exp_checkpoint --sample_dir=./alice_exp_sample --test_dir=./alice_exp_test_dir --L1_lambda_sup 10.0 --cgan_lambda 0.0



## Creat a dataset with two domains
  1. Convert video to images. 

      For example: https://image.online-convert.com/convert-to-jpg 
    
  2. Resize your images, and extract edges from the images. 
  
      For example: https://github.com/ppwwyyxx/tensorpack/tree/master/examples/HED

Our development is largely based on the code (greatly appreciated!): https://github.com/xhujoy/CycleGAN-tensorflow


## Citation
If you use this code for your research, please cite our [paper](https://arxiv.org/abs/1709.01215):

```
@article{li2017alice,
  title={ALICE: Towards Understanding Adversarial Learning for Joint Distribution Matching},
  author={Li, Chunyuan and Liu, Hao and Chen, Changyou and Pu, Yunchen and Chen, Liqun and Henao, Ricardo and Carin, Lawrence},
  journal={Neural Information Processing Systems (NIPS)},
  year={2017}
}
```

