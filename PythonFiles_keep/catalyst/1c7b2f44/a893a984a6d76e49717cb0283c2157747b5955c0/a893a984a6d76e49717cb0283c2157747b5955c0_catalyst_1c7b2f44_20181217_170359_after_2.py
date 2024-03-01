import torch
import catalyst.losses.unet as unet_loss
import catalyst.losses.center_loss as center_loss
import catalyst.losses.contrastive as contrastive_loss
import catalyst.losses.huber as huber_loss
import catalyst.losses.ce as ce
import catalyst.losses.bcece as bcece


LOSSES = {
    **torch.nn.__dict__,
    **unet_loss.__dict__,
    **center_loss.__dict__,
    **contrastive_loss.__dict__,
    **huber_loss.__dict__,
    **ce.__dict__,
    **bcece.__dict__,
}
