# ALICE with implicit mapping:
CUDA_VISIBLE_DEVICES=1 python main.py --checkpoint_dir ./alice_imp_checkpoint --sample_dir=./alice_imp_sample --test_dir=./alice_imp_test_dir --L1_lambda_sup 0.0 --cgan_lambda 1.0
CUDA_VISIBLE_DEVICES=1 python main.py --phase=test --checkpoint_dir ./alice_imp_checkpoint --sample_dir=./alice_imp_sample --test_dir=./alice_imp_test_dir --L1_lambda_sup 1.0 --cgan_lambda 1.0

# ALICE with explicit mapping:
CUDA_VISIBLE_DEVICES=0 python main.py --checkpoint_dir ./alice_exp_checkpoint --sample_dir=./alice_exp_sample --test_dir=./alice_exp_test_dir --L1_lambda_sup 10.0 --cgan_lambda 0.0
# test inference
CUDA_VISIBLE_DEVICES=1 python main.py --phase=test --checkpoint_dir ./alice_exp_checkpoint --sample_dir=./alice_exp_sample --test_dir=./alice_exp_test_dir --L1_lambda_sup 10.0 --cgan_lambda 0.0
# test transfer learning
CUDA_VISIBLE_DEVICES=1 python main.py --phase=test --checkpoint_dir ./alice_exp_checkpoint --sample_dir=./alice_exp_sample --test_dir=./alice_exp_test_transfer_dir --L1_lambda_sup 10.0 --cgan_lambda 0.0

# training with out1 edges
CUDA_VISIBLE_DEVICES=0 python main.py --checkpoint_dir ./alice_exp_out1_checkpoint --sample_dir=./alice_exp_out1_sample --test_dir=./alice_exp_out1_test_dir --L1_lambda_sup 10.0 --cgan_lambda 0.0


# CycleGAN:
CUDA_VISIBLE_DEVICES=1 python main.py --checkpoint_dir ./cyclegan_checkpoint --model_name cyclegan --sample_dir=./cyclegan_sample --test_dir=./cyclegan_test_dir
CUDA_VISIBLE_DEVICES=1 python main.py --phase=test --checkpoint_dir ./cyclegan_checkpoint --model_name cyclegan --sample_dir=./cyclegan_sample --test_dir=./cyclegan_test_dir 
