Microsoft Face API Accuracy
Out of a sample of 50 profile picture images on Instagram verified manually by me:
- False negative (male): 20
- False negative (female): 7
- True negative: 14
- True positive (female): 6
- True positive (male): 3
- There were no incorrect classifications, i.e. no gender mixups.

A quick explanation for each term:
- False negative male/female: a complete male/female face exists facing the camera, but the classifier did not identify him/her. Notably, men wearing hats had a very high false negative rate. Here are some examples of false negatives: 1, 2, 3, 4.
- True negative: profile picture did not have a whole face facing the camera and no face was classified. Note that someone facing away from the camera, a partial face being in the picture, or being too far away from the camera counts as a true negative.
- True positive male/female: correct classification of a male/female.

Now some quick accuracy stats:
- Profile pictures with complete faces: 36/50 = 72%
- Male Female ratio out of all profile pictures w/ complete faces: 64% vs 36%*
- Male recall rate: 3/23 = 13%
- Female recall rate: 6/13 = 46%
- Overall recall rate: 9/36 = 25% (recall: out of all instances, how many were correctly ID'd)
- Overall precision: 100% (precision: out of all male/female classifications, how many were correct in classifying a male/female) 
<sub><sup>Note: Actual female like-post % should be slightly higher, many times their profile pictures were technically true negatives as they faced away from the camera.</sup></sub>

In conclusion: There seems to be some decent bias in classifying females over males here. This could affect the data, as females would be more likely to be identified, while males dropped.

Possible sampling solutions:
- Quota sampling: Since there were no incorrect classifications, assume that the algorithm always doesn't mix up gender. Hence we can create a sample that is 50% classified males and females each. However, this would defeat the point of seeing gender ratios.
- Determine our error rates with more confidence, and adjust calculations given the bias.
- Look into other face APIs to get second/third opinions.
- Look into username and/or other attributes for gender detection.