# Image filters and how they work

## Introduction
Image filters are used to reduce noise in the image, to sharpen borders, or to do things like blurring objects. They are still an important tool in the arsenal of possible image transformations that you can apply.  Image filters take an input image and produce an output image (even though your software may replace the input image on the screen with the outpue image). There are two fundamentally different forms: one where you can re-create the input image (given the output image and the filter), and one where that is not possible. In addition, there are fliters that act globally on the whole image, and there are filters that act locally, and that are applied section by section on the whole image.  In this session, we will limit ourselves to these "local filters"

## Local filters, what is in the neighborhood?
Local fliters use a "structuring element".  That "structuring element" will be laid over the pixel values (starting at the origin of the image), and the recipe defined by the structuring element will be applied to calculate a value for the central pixel under the structuring element in the output image. Then, the structing element will move to the next pixel, th eprocedure will be repeated, etc..  Let's start with an example.


