# Alice4Alice
ALICE algorithms for painting the cartoon ["Alice's Adventures in Wonderland"](https://en.wikipedia.org/wiki/Alice%27s_Adventures_in_Wonderland)


**Ideas: Weakly-supervised information can alleviate the non-identifiablility issues of CycleGAN/DiscoGAN/DualGAN for image-to-image translation.**

*Experiments*: For 52 images (21 alice image and 31 rabbit images) in each domain (cartoon and edge), we provide 1 pairwise correspondence for each character, which significantly improves the generation quality.

ALICE (Explicit)  | ![](/plot_generation/figures_alice/cartoon_alice_exp_200.png	) 
:-------------------------:|:-------------------------:
CycleGAN         |  ![](/plot_generation/figures_alice/cartoon_cyclegan_200.png)


As references:

Real Cartoon  | ![](/plot_generation/figures_alice/cartoon_real.png) 
:-------------------------:|:-------------------------:
Edges         |  ![](/plot_generation/figures_alice/edges_out3_real.png)



Detailed Comparison:

Rabbit
 ![](/plot_generation/figures_alice/cartoon_cmp_136.png) 
 
Alice 
 ![](/plot_generation/figures_alice/cartoon_cmp_100.png) 
 
Cat (remotely reated to training set) 
 ![](/plot_generation/figures_alice/cartoon_cmp_10.png) 


This is largely based on the code: https://github.com/xhujoy/CycleGAN-tensorflow

Creat a dataset with two domains:
  1. Convert video to images. 

      For example: https://image.online-convert.com/convert-to-jpg 
    
  2. Resize your images, and extract edges from the images. 
  
      For example: https://github.com/ppwwyyxx/tensorpack/tree/master/examples/HED

