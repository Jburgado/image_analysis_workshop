# Segmentation (again)

## Illumination correction
Something that we glossed over in the previous section is illumination (or flatfield) correction.  Even in the best adjusted microscope, the illumination intensity (and the dection efficiency) is different in different parts of the image.  Most often, things are bright in the center and dimmer at the edges.  You can often see this by taking an image with your object of interest in the center, estimating (or measuring) its intenisty, the move it to a corner and repeat the estimate.  

This is obviously disastrous when you quantify things in your image.  They better have the same intensity independent of where in the image they are.  

To improve things we often apply "flatfield correction".  This relies on having perfect knowlegde of the combination of illumination and detection efficiency at each pixel.  In the CALM, we create such "flatfield" image using the best possible approximation of a uniform, thin, fluorescent sample.  These consist of highly concentrated fluorescent dye solution, so concentrated that the absorb most of the excitation light within the first micron or less of the sample, hence only a thin film is fluoresceing.  This approach was first suggested by [Michael Model](http://www.ncbi.nlm.nih.gov/pubmed/11500847). For a full protocol, see [the CALM website](https://calm.ucsf.edu/how-acquire-flat-field-correction-images).

When we consider this flatfield image (FI), the background image (BI the "dark" image of the camera), the measured image ('MI") and the "ideal", corrected image (CI) that we would like to have, we can write the following equation:

> MI = (CI * FI) + BI

Rewriting this to solve for CI, we get:

> CI = (MI - BI) / FI


When doing this calculation, it is nice to normalize the FI image to 1 (i.e. convert it to a floating point image and divide the image by its mean).  That way the mean intensity of the CI stays the same as that of the MI.  

* 
