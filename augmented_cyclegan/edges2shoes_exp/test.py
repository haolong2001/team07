import os
import time
import numpy as np
import torch
from torch.autograd import Variable
import torchvision.utils as vutils
from options import TestOptions, TrainOptions
from edges2shoes_data import DataLoader, load_edges2shoes, load_edges2shoes_, AlignedIterator, UnalignedIterator
from model import StochCycleGAN, AugmentedCycleGAN
import pickle as pkl
import math
from evaluate import eval_mse_A, eval_ubo_B
from model import log_prob_gaussian, gauss_reparametrize, log_prob_laplace, kld_std_guss
import random
import itertools 
import cv2
import pandas as pd 
file_count = 7000

def visualize_cycle(opt, real_A, visuals, name='cycle_test.png'):
    size = real_A.size()
    images = [img.cpu().unsqueeze(1) for img in visuals.values()]
    vis_image = torch.cat(images, dim=1).view(size[0]*len(images),size[1],size[2],size[3])
    save_path = os.path.join(opt.res_dir, name)
    vutils.save_image(vis_image.cpu(), save_path,
        normalize=True, range=(-1,1), nrow=len(images))

def visualize_multi_cycle(opt, real_B, model, name='multi_cycle_test.png'):
    size = real_B.size()
    images = model.generate_multi_cycle(real_B, steps=4)
    images = [img.cpu().unsqueeze(1) for img in images]
    vis_image = torch.cat(images, dim=1).view(size[0]*len(images),size[1],size[2],size[3])
    save_path = os.path.join(opt.res_dir, name)
    vutils.save_image(vis_image.cpu(), save_path,
        normalize=True, range=(-1,1), nrow=len(images))

def visualize_cycle_B_multi(opt, real_B, model, name='cycle_B_multi_test.png'):
    size = real_B.size()
    multi_prior_z_B = Variable(real_B.data.new(opt.num_multi,
        opt.nlatent, 1, 1).normal_(0, 1).repeat(size[0],1,1,1), volatile=True)
    fake_A, multi_fake_B = model.generate_cycle_B_multi(real_B, multi_prior_z_B)
    multi_fake_B = multi_fake_B.data.cpu().view(
        size[0], opt.num_multi, size[1], size[2], size[3])
    vis_multi_image = torch.cat([real_B.data.cpu().unsqueeze(1), fake_A.data.cpu().unsqueeze(1),
                                 multi_fake_B], dim=1) \
        .view(size[0]*(opt.num_multi+2),size[1],size[2],size[3])
    save_path = os.path.join(opt.res_dir, name)
    vutils.save_image(vis_multi_image.cpu(), save_path,
                      normalize=True, range=(-1,1), nrow=opt.num_multi+2)

c = 0
flag = False 
multi_prior_z_B_temp = 0
def visualize_multi(opt, real_A, model, name='multi_test.png'):
    global c
    global file_count 
    global flag 
    global multi_prior_z_B_temp
    size = real_A.size()
    print(size)
    # all samples in real_A share the same prior_z_B
    print(opt.num_multi)
    opt.num_multi = 10
    flag = False

    codes = pd.read_csv("feature_5.csv", header=None)
    code_tensor = torch.Tensor(codes.values)
    code_tensor = code_tensor.unsqueeze(dim=2).unsqueeze(dim=2).cuda()
    print("code tensor",code_tensor.shape)
    opt.num_multi = codes.shape[0]
    print("num", opt.num_multi)
    if flag: 
        prior = multi_prior_z_B_temp
    else:
        prior = real_A.data.new(opt.num_multi,
        opt.nlatent, 1, 1).normal_(0, 1)
        multi_prior_z_B = Variable(prior.repeat(size[0],1,1,1), volatile=True)
        multi_prior_z_B_temp = prior

    flag = True
    multi_prior_z_B = Variable(code_tensor.repeat(size[0],1,1,1), volatile=True)
    
    # print(multi)
    print("multi prior z_B",prior.shape)
    df = pd.DataFrame(prior.cpu().squeeze(dim=2).squeeze(dim=2))
    
    df.to_csv(f"{c}_codes.csv")
    c += 1
    # [ 0.7503,  1.6405,  0.8905,  0.3179],
    # codes = multi_prior_z_B[:20,:,:]
    
    # print(torch.squeeze(codes))
    # x = torch.zeros((4))
    # z = x.unsqueeze(1).unsqueeze(1).repeat(opt.num_multi,1,1,1)
    # torch[:]
    # vals = [-2, -1, 0, 1, 2]

    vals = [-2,-1, 0, 1, 2]
    # for i, val in enumerate(vals):
    #     z[i, 8 , 0] = val
    # default = 0
    # for i in range(opt.nlatent):
    #     x = torch.zeros((opt.nlatent))
    #     z = x.unsqueeze(1).unsqueeze(1).repeat(opt.num_multi,1,1,1)
    #     z[:, 0 , 0] =  0

    #     for j, val in enumerate(vals):
    #         z[j, i , 0] =  val

    #     multi_prior_z_B = Variable(z.repeat(size[0],1,1,1).cuda(), requires_grad=False)
    #     print("prior z",multi_prior_z_B.shape)
    
        # print(multi_prior_z_B.shape)
        # multi_prior_z_B = Variable(torch.Tensor([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]).repeat(size[0],1,1,1), requires_grad=False)
        # print(multi_prior_z_B)
    multi_fake_B = model.generate_multi(real_A.detach(), multi_prior_z_B)
    # fake_B = torch.transpose(multi_fake_B.detach(), 1,3)
    # mask_A = torch.transpose(real_A, 1,3)
    fake_B = multi_fake_B
    mask_A = real_A

    multi_fake_B = multi_fake_B.data.cpu().view(
        size[0], opt.num_multi, size[1], size[2], size[3])
    vis_multi_image = torch.cat([real_A.data.cpu().unsqueeze(1), multi_fake_B], dim=1) \
        .view(size[0]*(opt.num_multi+1),size[1],size[2],size[3])
    save_path = os.path.join(opt.res_dir, name)
    vutils.save_image(vis_multi_image.cpu(), save_path,
        normalize=True, range=(-1,1), nrow=opt.num_multi+1)

        # multi_fake_B = torch.zeros(50,3,64,64)
        

    fake_range = fake_B.shape[0]
    mask_range = mask_A.shape[0]
    print(mask_range)
    print(fake_range)
    count = 0

    # script_dir = os.path.dirname(__file__)
    # print(script_dir)
    A_dir = "gifA"
    B_dir = "gifB"
    for mask in range(mask_range):
        for gen in range(int(fake_range/mask_range)):
            
            # if gen != 20: 
            #     continue
            print("gen",gen)
            print(mask)
            mask_A_ = mask_A[mask,:,:,:].cpu()
            fake_B_ = fake_B[count,:,:,:].cpu()
            # print(mask_A[mask,:,:,:].shape)
            # print(fake_B[count,:,:,:].shape)
            # print('writing')
            print(mask_A_.shape)
            print(fake_B_.shape)

            mask_path = os.path.join(os.getcwd(),A_dir,f'aug_data_{str(count).zfill(3)}_{file_count}.png')
            img_path = os.path.join(os.getcwd(),B_dir,f'aug_data_{str(count).zfill(3)}_{file_count}.png')

            vutils.save_image(mask_A_, mask_path,
            normalize=True, range=(-1,1))
            vutils.save_image(fake_B_, img_path,
            normalize=True, range=(-1,1))
            count += 1
            file_count += 1
            
            
            # for label in range(1,multi_fake_B.shape[0]+1):
            #     for j in range(1,multi_fake_B.shape/):
            # print('fake_b', multi_fake_B.shape[0])
        break      

    




def visualize_inference(opt, real_A, real_B, model, name='inf_test.png'):
    size = real_A.size()

    real_B = real_B[:opt.num_multi]
    # all samples in real_A share the same post_z_B
    multi_fake_B = model.inference_multi(real_A.detach(), real_B.detach())
    multi_fake_B = multi_fake_B.data.cpu().view(
        size[0], opt.num_multi, size[1], size[2], size[3])

    vis_multi_image = torch.cat([real_A.data.cpu().unsqueeze(1), multi_fake_B], dim=1) \
        .view(size[0]*(opt.num_multi+1),size[1],size[2],size[3])

    vis_multi_image = torch.cat([torch.ones(1, size[1], size[2], size[3]).cpu(), real_B.data.cpu(),
                                 vis_multi_image.cpu()], dim=0)

    save_path = os.path.join(opt.res_dir, name)
    vutils.save_image(vis_multi_image.cpu(), save_path,
        normalize=True, range=(-1,1), nrow=opt.num_multi+1)

    

def sensitivity_to_edge_noise(opt, model, data_B, use_gpu=True):
    """This is inspired from: https://arxiv.org/pdf/1712.02950.pdf"""
    res = []
    for std in [0, 0.1, 0.2, 0.5, 1, 2, 3, 5]:
        real_B = Variable(data_B, volatile=True)
        if use_gpu:
            real_B = real_B.cuda()
        rec_B = model.generate_noisy_cycle(real_B, std)
        s = torch.abs(real_B - rec_B).sum(3).sum(2).sum(1) / (64*64*3)
        res.append(s.data.cpu().numpy().tolist())
    np.save('noise_sens', res)

def train_MVGauss_B(dataset):
    b_mean = 0
    b_var = 0
    n = 0
    for i,batch in enumerate(dataset):
        real_B = Variable(batch['B'])
        real_B = real_B.cuda()
        b_mean += real_B.mean(0, keepdim=True)
        n += 1
        print(i)
    b_mean = b_mean / n
    for i,batch in enumerate(dataset):
        real_B = Variable(batch['B'])
        real_B = real_B.cuda()
        b_var += ((real_B-b_mean)**2).mean(0, keepdim=True)
        print(i)
    b_var = b_var / n
    return b_mean, b_var

def eval_bpp_MVGauss_B(dataset, mu, logvar):
    bpp = []
    for batch in dataset:
        real_B = Variable(batch['B'])
        real_B = real_B.cuda()
        dequant = Variable(torch.zeros(*real_B.size()).uniform_(0, 1./127.5).cuda())
        real_B = real_B + dequant
        nll = -log_prob_gaussian(real_B, mu, logvar)
        nll = nll.view(real_B.size(0), -1).sum(1) + (64*64*3) * math.log(127.5)
        bpp.append(nll.mean(0).data[0] / (64*64*3*math.log(2)))
    return np.mean(bpp)

def compute_bpp_MVGauss_B(dataroot):
    trainA, trainB, devA, devB, testA, testB = load_edges2shoes(dataroot)
    train_dataset = UnalignedIterator(trainA, trainB, batch_size=200)
    print ('#training images = %d') % len(train_dataset)

    test_dataset = AlignedIterator(testA, testB, batch_size=200)
    print ('#test images = %d') % len(test_dataset)

    mvg_mean, mvg_var = train_MVGauss_B(train_dataset)
    mvg_logvar = torch.log(mvg_var + 1e-5)
    bpp = eval_bpp_MVGauss_B(test_dataset, mvg_mean, mvg_logvar)
    print("MVGauss BPP: %.4f") % bpp


def train_logvar(dataset, model, epochs=1, use_gpu=True):
    logvar_B = Variable(torch.zeros(1, 3, 64, 64).fill_(math.log(0.01)).cuda(), requires_grad=True)
    iterative_opt = torch.optim.RMSprop([logvar_B], lr=1e-2)

    for eidx in range(epochs):
        for batch in dataset:
            real_B = Variable(batch['B'])
            if use_gpu:
                real_B = real_B.cuda()
            size = real_B.size()
            dequant = Variable(torch.zeros(*real_B.size()).uniform_(0, 1./127.5).cuda())
            real_B = real_B + dequant
            enc_mu = Variable(torch.zeros(size[0], model.opt.nlatent).cuda())
            enc_logvar = Variable(torch.zeros(size[0], model.opt.nlatent).fill_(math.log(0.01)).cuda())
            fake_A = model.predict_A(real_B)
            if hasattr(model, 'netE_B'):
                params = model.predict_enc_params(fake_A, real_B)
                enc_mu = Variable(params[0].data)
                if len(params) == 2:
                    enc_logvar = Variable(params[1].data)
            z_B = gauss_reparametrize(enc_mu, enc_logvar)
            fake_B = model.predict_B(fake_A, z_B)
            z_B = z_B.view(size[0], model.opt.nlatent)
            log_prob = log_prob_laplace(real_B, fake_B, logvar_B)
            log_prob = log_prob.view(size[0], -1).sum(1)
            kld = kld_std_guss(enc_mu, enc_logvar)
            ubo = (-log_prob + kld) + (64*64*3) * math.log(127.5)
            ubo_val_new = ubo.mean(0).data[0]
            kld_val = kld.mean(0).data[0]
            bpp = ubo.mean(0).data[0] / (64*64*3* math.log(2.))

            print('UBO: %.4f, KLD: %.4f, BPP: %.4f') % (ubo_val_new, kld_val, bpp)
            loss = ubo.mean(0)
            iterative_opt.zero_grad()
            loss.backward()
            iterative_opt.step()

    return logvar_B


def compute_train_kld(train_dataset, model):
    ### DEBUGGING KLD
    train_kl = []
    for i, batch in enumerate(train_dataset):
        real_A, real_B = Variable(batch['A']), Variable(batch['B'])
        real_A = real_A.cuda()
        real_B = real_B.cuda()
        fake_A = model.predict_A(real_B)
        params = model.predict_enc_params(fake_A, real_B)
        mu = params[0]
        train_kl.append(kld_std_guss(mu, 0.0*mu).mean(0).data[0])
        if i == 100:
            break
    print('train KL:'),np.mean(train_kl)


def test_model():
    opt = TestOptions().parse()
    dataroot = opt.dataroot

    # extract expr_dir from chk_path
    expr_dir = os.path.dirname(opt.chk_path)
    opt_path = os.path.join(expr_dir, 'opt.pkl')

    # parse saved options...
    print(opt_path)
    opt.__dict__.update(parse_opt_file(opt_path))
    opt.expr_dir = expr_dir
    opt.dataroot = dataroot

    # hack this for now
    opt.gpu_ids = [0]

    opt.seed = 12345
    random.seed(opt.seed)
    np.random.seed(opt.seed)
    torch.manual_seed(opt.seed)
    torch.cuda.manual_seed_all(opt.seed)

    # create results directory (under expr_dir)
    res_path = os.path.join(opt.expr_dir, opt.res_dir)
    opt.res_dir = res_path
    if not os.path.exists(res_path):
        os.makedirs(res_path)

    use_gpu = len(opt.gpu_ids) > 0

    trainA, trainB, devA, devB, testA, testB = load_edges2shoes(opt.dataroot)
    sub_size = int(len(trainA) * 0.2)
    print(sub_size)
    print(len(trainB))

    trainA = trainA[:sub_size]
    trainB = trainB[:sub_size]
    train_dataset = UnalignedIterator(trainA, trainB, batch_size=8)
    print(len(train_dataset))
    print(f'#training images = {len(train_dataset)}')
    vis_inf = False

    
    test_dataset = AlignedIterator(testA, testB, batch_size=8)
    print(f'#test images = {len(test_dataset)}')

    dev_dataset = AlignedIterator(devA, devB, batch_size=8)
    print(f'#dev images = {len(dev_dataset)}')

    vis_inf = False
    if opt.model == 'stoch_cycle_gan':
        model = StochCycleGAN(opt, testing=True)
    elif opt.model == 'cycle_gan':
        model = StochCycleGAN(opt, ignore_noise=True, testing=True)
    elif opt.model == 'aug_cycle_gan':
        model = AugmentedCycleGAN(opt, testing=True)
        vis_inf = True
    else:
        raise NotImplementedError('Specified model is not implemented.')

    model.load(opt.chk_path)
    # model.eval()

    # debug kl
    # compute_train_kld(train_dataset, model)

    if opt.metric == 'bpp':

        if opt.train_logvar:
            print("training logvar_B on training data...")
            logvar_B = train_logvar(train_dataset, model)
        else:
            logvar_B = None

        print ("evaluating on test set...")
        t = time.time()
        test_ubo_B, test_bpp_B, test_kld_B = eval_ubo_B(test_dataset, model, 500,
                                                        visualize=True, vis_name='test_pred_B',
                                                        vis_path=opt.res_dir,
                                                        logvar_B=logvar_B,
                                                        verbose=True,
                                                        compute_l1=True)

        print("TEST_BPP_B: %.4f, TIME: %.4f") % (test_bpp_B, time.time()-t)

    elif opt.metric == 'mse':
        dev_mse_A = eval_mse_A(dev_dataset, model)
        test_mse_A = eval_mse_A(test_dataset, model)
        print (f"DEV_MSE_A: {dev_mse_A}, TEST_MSE_A: {test_mse_A}") 

    elif opt.metric == 'visual':
        opt.num_multi = 5
        n_vis = 10
        dev_dataset = AlignedIterator(devA, devB, batch_size=1)
        for i, vis_data in enumerate(dev_dataset):
            if i != 3: 
                continue
            real_A, real_B = Variable(vis_data['A'], volatile=True), \
                             Variable(vis_data['B'], volatile=True)
            prior_z_B = Variable(real_A.data.new(n_vis, opt.nlatent, 1, 1).normal_(0, 1), volatile=True)

            if use_gpu:
                real_A = real_A.cuda()
                real_B = real_B.cuda()
                prior_z_B = prior_z_B.cuda()

            # visuals = model.generate_cycle(real_A, real_B, prior_z_B)
            # visualize_cycle(opt, real_A, visuals, name='cycle_%d.png' % i)
            # exit()
            # visualize generated B with different z_B
            visualize_multi(opt, real_A, model, name='multi_%d.png' % i)
            # break
            # visualize_cycle_B_multi(opt, real_B, model, name='cycle_B_multi_%d.png' % i)

            # visualize_multi_cycle(opt, real_B, model, name='multi_cycle_%d.png' % i)

            # if vis_inf:
            #     # visualize generated B with different z_B infered from real_B
            #     visualize_inference(opt, real_A, real_B, model, name='inf_%d.png' % i)

    elif opt.metric == 'noise_sens':
        sensitivity_to_edge_noise(opt, model, test_dataset.next()['B'])
    else:
        raise NotImplementedError('wrong metric!')

def parse_opt_file(opt_path):

    def parse_val(s):
        if s == 'None':
            return None
        if s == 'True':
            return True
        if s == 'False':
            return False
        if s == 'inf':
            return float('inf')
        try:
            f = float(s)
            # special case
            if '.' in s:
                return f
            i = int(f)
            return i if i == f else f
        except ValueError:
            return s
    # opt = TrainOptions().parse(sub_dirs=['vis_multi','vis_cycle','vis_latest','train_vis_cycle'])
    opt = None
    with open(opt_path,"rb") as f:
        if opt_path.endswith('pkl'):
            opt = pkl.load(f)
        else:
            opt = dict()
            for line in f:
                if line.startswith('-----'):
                    continue
                k,v = line.split(':')
                opt[k.strip()] = parse_val(v.strip())
    # del opt["chk_path"]
    # del opt["metric"]
    return opt

if __name__ == "__main__":
    # CUDA_VISIBLE_DEVICES=0 python -m ipdb test.py --chk_path checkpoints/FOLDER/latest --res_dir val_res --opt_path checkpoints/FOLDER/opt.txt
    test_model()
    # compute_bpp_MVGauss_B('/home/a-amalma/data/edges2shoes/')
