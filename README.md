# Alice4Alice
ALICE algorithms for painting the cartoon "Alice's Adventures in Wonderland"




ALICE            | ![](/plot_generation/figures_alice/cartoon_alice_exp_200.png	) 
:-------------------------:|:-------------------------:
CycleGAN         |  ![](/plot_generation/figures_alice/cartoon_cyclegan_200.png)

Real Cartoon  | ![](/plot_generation/figures_alice/cartoon_real.png) 
Edges         |  ![](/plot_generation/figures_alice/edges_out3_real.png)



This is largely based on the code: https://github.com/xhujoy/CycleGAN-tensorflow

Creat a dataset with two domains:
  1. Convert video to images. 

      For example: https://image.online-convert.com/convert-to-jpg 
    
  2. Resize your images, and extract edges from the images. 
  
      For example: https://github.com/ppwwyyxx/tensorpack/tree/master/examples/HED

