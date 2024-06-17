"""
Python executable script to create MPRAGElike images from MPM or VFA multi-contrast images.

Developer: Marc-Antoine Fortin, June 2024. E-mail: marc.a.fortin@ntnu.no

"""
###################################################################################
### IMPORTS ###
import argparse
import sys
import os
import nibabel as nib
import numpy as np

###################################################################################

def main():

    # Set up the argument parser with a description and default help formatter
    parser = argparse.ArgumentParser(
        description='Script to create MPRAGElike images from MPM or VFA multi-contrast images. Developer: Marc-Antoine Fortin, NTNU, June 2024. E-mail: marc.a.fortin@ntnu.no',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Add arguments for the script
    parser.add_argument('--path2img', help="Fullpath to the folder containing the MPM/VFA images. A certain hierarchy is expected: 1) All different contrasts should be inside the same folder. 2) All contrasts should have an identifier as aprt of their names like 't1' or 'T1' for the T1w images. ' "
                                           "3) All images should be in the Nifti format (.nii or .nii.gz).", required=True)
    parser.add_argument('--echo', help='Integer defining the echo number (TE) to use from the images in the folder. The script expects a "_eX" naming for TE as used it is used by most nifti converter softwares. If single TE data is used without a "_eX" in the filenme, do not specify this flag.  ',
                        required=False, default=1)
    parser.add_argument('--reg', help='Regularization parameter for background noise removal of the MPRAGElike image. Can have more than one lambda value. If you only have one lambda value, you can directly type the value. If >1 lambda, please type a list of integers (e.g., [0, 100, '
                                      '200, 300]). A default value of 100 is set for lambda, but the most optimal lambda value can be different for different images or scalings.', required=False, default=100)
    parser.add_argument('--subid', help='Subject identifier. Can be any combination of strings and/or numbers.', required=True)
    parser.add_argument('--contrast', help="Select which MPRAGElike equation (i.e., contrasts to use to compute the MPRAGElike image) to use. 'all' to use T1w, PDw and MTw. 'PD' to use the T1 and PD images only. 'MT' to use the T1 and MT images only. Only one value can be set.", required=True, default='all')
    parser.add_argument('--path2save', help="Path where all the MPRAGElike images created from this script will be saved. A 'mprage-like' subfolder in the current working directory will be created if nothing is specified.", required=False, default=os.getcwd())

    # Parse the command-line arguments
    args = parser.parse_args()

    # Retrieve arguments
    path2img = args.path2img
    echo = args.echo
    subID = args.subid
    contrast = args.contrast
    path2save = args.path2save
    reg = args.reg

    # Process the 'reg' argument if the user gave a list as the argument value
    if '[' in reg:
        reg = reg.replace("[", "")
        reg = reg.replace("]", "")
        reg = list(reg.split(","))
    else:
        reg = int(args.reg)


    # Get the fullpath of all images in the folder.
    fullpath2imgs = get_img_paths(path2img, echo)

    # Get the image data (3D arrays + header + affine)
    t1w_data, pdw_data, mtw_data, t1w_header, pdw_header, mtw_header, t1w_affine, pdw_affine, mtw_affine = get_img_arrays(fullpath2imgs)

    # Check whether the user gave an integer or list for lamba value(s)
    if isinstance(reg, int):

        mprage_like = mprage_like_img(t1w_data, pdw_data, mtw_data, reg=reg, weight=contrast) # Create MPRAGElike image
        save_mprage_like(mprage_like, t1w_affine, path2save, subID, reg=reg, echo=echo, weight=contrast) # Save the newly created MPRAGElike image

    else:

        # Loop through all lambda values
        for r in reg:

            mprage_like = mprage_like_img(t1w_data, pdw_data, mtw_data, reg=int(r), weight=contrast) # Create MPRAGElike image
            save_mprage_like(mprage_like, t1w_affine, path2save, subID, reg=r, echo=echo, weight=contrast) # Save the newly created MPRAGElike image

# User-defined function to get the fullpath to all images
def get_img_paths(path2img, echo):


    echo_num = '_e%s'% (echo) # Create variable related to echo number of the data to use

    # List .nii images found in the directory with the corresponding echo number
    nii_files = [f for f in os.listdir(path2img) if ('.nii' and echo_num) in f]

    if not nii_files: # If the filenames didn't have the '_eX' naming convention (=> empty nii_files list), the script will assume it's single echo data and that only one magnitude volume of each contrast is present in the folder.
        nii_files = [f for f in os.listdir(path2img) if ('.nii') in f]

    magn_files = [m for m in nii_files if not ('_ph' in m or 'phase' in m)] # if there is phase data in the folder, it will be ignored.
    #mag_no_json_files = [j for j in magn_files if not '.json' in j] # Exclude .json files from the resulting list and keep only the .nii files
    fullpath2imgs = [os.path.join(path2img, magn) for magn in magn_files]

    return fullpath2imgs


# User defined function to get the image data (arrays), header and affine.
def get_img_arrays(fullpath2img):

    # For loop to identify indices of the different hMRI maps and append all maps together in a 4D matrix
    for idx, mpm in enumerate(fullpath2img):

        if 't1' in mpm or 'T1' in mpm:
            t1w = nib.load(fullpath2img[idx])
            t1w_data = t1w.get_fdata(dtype='float32')
            t1w_affine = t1w.affine
            t1w_header = t1w.header

        elif 'pd' in mpm or 'PD' in mpm:
            pdw = nib.load(fullpath2img[idx])
            pdw_data = pdw.get_fdata(dtype='float32')
            pdw_affine = pdw.affine
            pdw_header = pdw.header

        elif 'mt' in mpm or 'MT' in mpm:
            mtw = nib.load(fullpath2img[idx])
            mtw_data = mtw.get_fdata(dtype='float32')
            mtw_affine = mtw.affine
            mtw_header = mtw.header

    return t1w_data , pdw_data , mtw_data , t1w_header , pdw_header , mtw_header , t1w_affine , pdw_affine , mtw_affine

def mprage_like_img(t1w_data, pdw_data, mtw_data, reg=100, weight='all'):

    # Calculate the mprage-like image based on the desired contrast
    if weight=='all':
        mprage_like = (t1w_data - reg)/(0.5*(pdw_data + mtw_data) + reg)

    elif weight=='MT':
        mprage_like = (t1w_data - reg) / (mtw_data + reg)

    elif weight=='PD':
        mprage_like = (t1w_data - reg) / (pdw_data + reg)

    # Set NaN to 0
    #mprage_like_noNaN = mprage_like
    mprage_like_noNaN = np.nan_to_num(mprage_like)
    # Set +inf and values > 500 to 0
    mprage_like_noNaN_inf = mprage_like_noNaN
    mprage_like_noNaN_inf[mprage_like_noNaN_inf == np.inf] = 0
    mprage_like_noNaN_inf[mprage_like_noNaN_inf > 500] = 0 # Here we set all values over 500 (ad hoc very large threshold value). Since the mprage-like is a ratio, very few values (if not none) should be in around these values. And if there would, they would be outside relevant anatomy. From random checks, no values over ~20 were observed.
    # Remove negative values and set them to 0
    mprage_like_noNaN_noInf_nz = mprage_like_noNaN_inf
    mprage_like_noNaN_noInf_nz[mprage_like_noNaN_noInf_nz < 0] = 0

    # Rename final MPRAGElike image
    mprage_like_final = mprage_like_noNaN_noInf_nz

    return mprage_like_final

def save_mprage_like(mprage_like_data, mprage_like_affine, path2save, subID, reg=100, echo=1, weight='all'):

    mplike_name = 'mprage-like'
    # Create new subfolder called 'mprage-like' in the provided saving folder
    fullsavepath = os.path.join(path2save, mplike_name)
    pathExist = os.path.exists(fullsavepath)
    if not pathExist:
        os.makedirs(fullsavepath)

    # Enforce float32 data type and save the mprage-like image with the affine of one of the mpm/vfa images used to compute them
    mprage_like_data = mprage_like_data.astype(np.float32)
    mprage_img = nib.Nifti1Image(mprage_like_data, affine=mprage_like_affine)

    if weight=='all':
        mprage_img_name = '%s_%s_e%s_%s_reg%s.nii' % (str(subID), mplike_name, str(echo), weight, str(reg))
    elif weight=='PD':
        mprage_img_name = '%s_%s_e%s_%s_reg%s.nii' % (str(subID), mplike_name, str(echo), weight, str(reg))
    elif weight == 'MT':
        mprage_img_name = '%s_%s_e%s_%s_reg%s.nii' % (str(subID), mplike_name, str(echo), weight, str(reg))

    fullpath2save = os.path.join(fullsavepath, mprage_img_name)
    nib.save(mprage_img, os.path.join(fullsavepath, mprage_img_name))
    print('MPRAGE-like image saved to the following filename: %s' % (fullpath2save))


if __name__ == '__main__':
    sys.exit(main())
