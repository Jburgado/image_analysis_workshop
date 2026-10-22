# Segmentation

## Defining objects through segmentation
Segmentation in image analysis literally means segmenting the image in two or more objects.  These objects are defined by their numerical value in the image.  The simplest way to segment an image is to set a threshold, set everything below the threshold to zero (this could represen the background in the image) and everything at or above the threshold to 1 (this could be the object(s) that you are interested in.  

* Open napari ('uv run napari').  Open the file 'testImages/3Channel_FF_Corrected_1_MMStack_Pos0.ome.tif' (use the "napari-tiff" opener, you may need to choose "File > Open with plugin" to get that option).  If the image stages black, choose a colormap (for example, magenta, green blue for each channel. Only consider the "DAPI" channel (you can click the eye for the other channels to make invisible). Inspect the pixel values inside and outside of the nuclei.  Where would you set teh threshold, so that nuclei will have a higher value than the threshold, and the background will not?  Ask you AI assistant to segment the DAPI channel of this image with your threshold, and view the resulting segmeneted image in napari.  What problem(s) do you (and/or your AI assistant) note?

Setting a threshold by eye balling does not scale well, and certainly is not reproducible (poll your neighbors about the threshold they choose).  Ask your AI assistant what methods exist in scikit-image to automatically determine a threshold and how they work.

### What is an object?  Connected pixels
To go from a segmented image to objects, the computer code needs to determine which pixels are connected.  This works with a structuring element very much like the kernels that we used for convolution filters.  This structuring element often is a 3x3 element, or a 3x3 element with no corners (i.e. a plus sign).  When the code overlays this on teh segmented image, a pixel is considered to be "connected" if any of the pixels in the strcuturing element are a one (i.e. not zero). 

Plus sign structuring element
|       | Col 1  | Col 2  | Col 3 |
| ----- | ----- | ----- | ----- |
| Row 1 |     |  1   |     |
| Row 2 |  1   |     |  1   |
| Row 3 |     |  1   |     |



Full 8 connected neigbors
|       | Col 1  | Col 2  | Col 3 |
| ----- | ----- | ----- | ----- |
| Row 1 |  1   |  1   |  1   |
| Row 2 |  1   |     |  1   |
| Row 3 |  1   |  1   |  1   |

* Ask your AI coding assistant to write a script that reads the DAPI channel in testImages/3Channel_FF_Corrected_1_MMStack_Pos0.ome.tif, thresholds it with a value determined wit the Otsu method, and counts the total number of objects (independent of size). Show a histogram of the size (in number of pixels) of the objects.

You likely noted a significant number of very small objects (I had 11).  You can filter these out bsaed on their size (this is a very fair way of dealing with objects, you often have a good idea of the possible size range and can use that information to hone in on what is interesting).  However, you can also remove these through a process called "erosion".  When "eroding" a segmented image, the structuring element is moved over the image.  When all pixels in the element are "true" (value of one) in the input image, the output pixel will be set to one, when any of the pixels under the element are false, the output pixel will be set to zero.  This leads to the disappearence of isolated pixels, and the erosion of pixels at the borders of objects.  To compensate for this loss of pixels at the borders, erosion is often following by "dilation".  During dilation, the output pixel is set to true if any of the pixels under the structuring element are true.  You can have multiple rounds of erosion followed by an equivalent number of rounds of dilation.  

* Ask your AI assistant to run two rounds of erosion followed by two rounds of dilation on the DAPI channel in  testImages/3Channel_FF_Corrected_1_MMStack_Pos0.ome.tif after Otsu thresholding and create a histogram of the  size of the remaining objects.  

If the goal is to fill holes within existing objects, you can change the order: first run dilations until the holes arte filler, then run erosions (which will not re-open the holes) to compensate for the effect on the size of the object.


### From segmented images to objects
You now how have a segmented, binary (only zeros and ones) image on which you clearly can see what is nucleus and what is not.  For the computer to recognize these as individual entities, it is much nicer to give each connected area its own number and use a LookUp Taable that has different colors for these numbers.  

* Ask your AI coding assistant to opens the DAPI channel from testImages/3Channel_FF_Corrected_1_MMStack_Pos0.ome.tif, thresholds it using the Otsu method, run 3 rounds of erosion and 3 rounds of dilation on it, and label each of the objects with a distinct number, and save the image with a LUT with distinct colors for these numbers. Note, to see the labels as distinct colors in Napari, you may need to righ-click the layer and choose "Convert to Labels".  


You may have noticed that nuclei that are close together in the image are not 

