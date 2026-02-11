# Segmentation Subpackage
IPL segmentation methods implemented in Python


## Modules

**gauss_seg**
Implementation of the IPL standard segmentation script in Python.

Equivalent to `ipl> gauss_seg`

**autocontour**
Implementation of the IPL autocontour script in Python. This implementation
produces a "tighter" segmentation compared to the IPL implementation.

**autocontour_gobj**
Variant of autocontour requiring GOBJ masks to be used when distal and proximal bones are too close to discern

**laplace_hamming_filter**
Implementation of the IPL fft laplace hamming filter in Python.

Equivalent to `ipl> fft_laplace`
